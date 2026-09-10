"""HTTP routes: one SSE route that runs the whole graph, plus history CRUD."""
import json
import uuid
from datetime import date

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.config import OUTPUTS_DIR
from app.db import SessionLocal
from app.graph import graph_app
from app.models import Blog
from app.schemas.api import BlogDetail, BlogSummary, GenerateRequest

router = APIRouter(prefix="/api", tags=["blog"])


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


def _normalize_md(md: str) -> str:
    # The graph writes image links as `images/<file>`; serve them from /images.
    return (md or "").replace("](images/", "](/images/")


def _dump(obj, fallback):
    if obj is None:
        return fallback
    try:
        return obj.model_dump()
    except Exception:
        return fallback


def _initial_state(req: GenerateRequest) -> dict:
    return {
        "topic": req.topic.strip(),
        "mode": "",
        "needs_research": False,
        "queries": [],
        "evidence": [],
        "plan": None,
        "as_of": req.as_of or date.today().isoformat(),
        "recency_days": 7,  # router may overwrite
        "sections": [],
        "final": "",
        "image_specs": [],
    }


def _persist(state: dict, plan, evidence, final_md: str) -> Blog:
    plan_dict = _dump(plan, {})
    evidence_list = [_dump(e, {}) for e in (evidence or [])] if isinstance(evidence, list) else []
    image_specs = state.get("image_specs") or []

    title = plan_dict.get("blog_title", "") or state.get("topic", "")
    slug = title.lower().replace(" ", "_") + ".md"
    file_path = str(OUTPUTS_DIR / slug)

    blog = Blog(
        id=uuid.uuid4().hex,
        topic=state.get("topic", ""),
        title=title,
        mode=state.get("mode", "") or "",
        blog_kind=plan_dict.get("blog_kind", "") or "",
        needs_research=bool(state.get("needs_research", False)),
        markdown=final_md,
        file_path=file_path,
        plan_json=json.dumps(plan_dict, default=str),
        evidence_json=json.dumps(evidence_list, default=str),
        image_specs_json=json.dumps(image_specs, default=str),
    )

    db = SessionLocal()
    try:
        db.add(blog)
        db.commit()
        db.refresh(blog)
    finally:
        db.close()
    return blog


def _event_stream(req: GenerateRequest):
    state_input = _initial_state(req)
    state = dict(state_input)
    plan = None
    evidence = []
    image_specs = []

    yield _sse("start", {"topic": state_input["topic"], "as_of": state_input["as_of"]})

    try:
        for chunk in graph_app.stream(state_input, stream_mode="updates"):
            for node, update in chunk.items():
                updates = update if isinstance(update, list) else [update]

                if node == "worker":
                    produced = 0
                    for u in updates:
                        if not isinstance(u, dict):
                            continue
                        for task_id, section_md in (u.get("sections") or []):
                            state.setdefault("sections", [])
                            state["sections"].append((task_id, section_md))
                            produced += 1
                            yield _sse("section", {"task_id": task_id, "markdown": section_md})
                    yield _sse("progress", {"node": "worker", "status": "done", "sections": produced})
                    continue

                for u in updates:
                    if not isinstance(u, dict):
                        continue
                    if u.get("plan") is not None:
                        plan = u["plan"]
                        yield _sse("plan", _dump(plan, {}))
                    if "evidence" in u and u["evidence"] is not None:
                        evidence = u["evidence"]
                        yield _sse(
                            "evidence",
                            {"count": len(evidence), "items": [_dump(e, {}) for e in evidence]},
                        )
                    if "image_specs" in u:
                        image_specs = u["image_specs"] or []
                    for key, value in u.items():
                        if key == "sections":
                            continue
                        state[key] = value

                yield _sse(
                    "progress",
                    {
                        "node": node,
                        "status": "done",
                        "mode": state.get("mode") or "",
                        "needs_research": bool(state.get("needs_research")),
                    },
                )

        final_md = state.get("final") or state.get("merged_md") or ""
        final_md = _normalize_md(final_md)

        if image_specs:
            yield _sse("images", {"count": len(image_specs), "specs": image_specs})

        blog = _persist(state, plan, evidence, final_md)

        yield _sse(
            "done",
            {
                "id": blog.id,
                "topic": blog.topic,
                "title": blog.title,
                "mode": blog.mode,
                "blog_kind": blog.blog_kind,
                "needs_research": blog.needs_research,
                "evidence_count": len(evidence or []),
                "image_count": len(image_specs),
                "file_path": blog.file_path,
                "markdown": final_md,
            },
        )
    except Exception as exc:  # surface graph/LLM failures to the client
        yield _sse("error", {"message": str(exc)})


@router.post("/blog/generate")
def generate_blog(req: GenerateRequest):
    return StreamingResponse(
        _event_stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/blogs", response_model=list[BlogSummary])
def list_blogs():
    db = SessionLocal()
    try:
        rows = db.query(Blog).order_by(Blog.created_at.desc()).all()
        return [row.summary() for row in rows]
    finally:
        db.close()


@router.get("/blogs/{blog_id}", response_model=BlogDetail)
def get_blog(blog_id: str):
    db = SessionLocal()
    try:
        row = db.query(Blog).filter(Blog.id == blog_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        try:
            evidence = json.loads(row.evidence_json or "[]")
        except Exception:
            evidence = []
        try:
            plan = json.loads(row.plan_json or "{}")
        except Exception:
            plan = {}
        return {
            **row.summary(),
            "markdown": row.markdown or "",
            "file_path": row.file_path or "",
            "evidence_count": len(evidence),
            "task_count": len(plan.get("tasks", [])),
        }
    finally:
        db.close()


@router.delete("/blogs/{blog_id}")
def delete_blog(blog_id: str):
    db = SessionLocal()
    try:
        row = db.query(Blog).filter(Blog.id == blog_id).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        db.delete(row)
        db.commit()
        return {"ok": True}
    finally:
        db.close()
