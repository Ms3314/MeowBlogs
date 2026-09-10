"""Orchestrator node: turns research + topic into a structured blog Plan."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import llm
from app.schemas.content import Plan
from app.schemas.state import State

# this is the orchestrator so we create a plan
ORCH_SYSTEM = """You are a senior technical writer and developer advocate.
Your job is to produce a highly actionable outline for a technical blog post.

Hard requirements:
- Create 5–9 sections (tasks) suitable for the topic and audience.
- Each task must include:
  1) goal (1 sentence)
  2) 3–6 bullets that are concrete, specific, and non-overlapping
  3) target word count (120–550)

Quality bar:
- Assume the reader is a developer; use correct terminology.
- Bullets must be actionable: build/compare/measure/verify/debug.
- Ensure the overall plan includes at least 2 of these somewhere:
  * minimal code sketch / MWE (set requires_code=True for that section)
  * edge cases / failure modes
  * performance/cost considerations
  * security/privacy considerations (if relevant)
  * debugging/observability tips

Grounding rules:
- Mode closed_book: keep it evergreen; do not depend on evidence.
- Mode hybrid:
  - Use evidence for up-to-date examples (models/tools/releases) in bullets.
  - Mark sections using fresh info as requires_research=True and requires_citations=True.
- Mode open_book:
  - Set blog_kind = "news_roundup".
  - Every section is about summarizing events + implications.
  - DO NOT include tutorial/how-to sections unless user explicitly asked for that.
  - If evidence is empty or insufficient, create a plan that transparently says "insufficient sources"
    and includes only what can be supported.

Output must strictly match the Plan schema.
"""


# ye banda ak plan banata aur ye plan mein tasks rehte jo fanout hote
def orchestrator(state: State) -> dict:  # Plan is returned
    evidence = state.get("evidence", [])  # we are getting the evidence
    mode = state.get("mode", "closed_book")  # this says if research was done or not over here
    forced_kind = "news_roundup" if mode == "open_book" else None
    plan = llm.with_structured_output(Plan).invoke(
        [
            SystemMessage(
                content=ORCH_SYSTEM
            ),
            HumanMessage(content=(
                f"Topic : {state['topic']}"
                f"Mode : {mode} \n\n"
                f"As-of: {state["as_of"]} (recency_days={state['recency_days']})"  # we are mentioning the date and recency we need for the content but then we already filter this out from the research node
                f"{'Force blog_kind=news_roundup' if forced_kind else ''}\n\n"
                f"Evidence (ONLY use fresh claims ; may be empty)"
                f"{[e.model_dump() for e in evidence][:16]}"
                f"Instruction: If mode=open_book, your plan must NOT drift into a tutorial."
                ))
        ]
    )
    # if the blog is open_book make it a news_roundup type of a blog over here !!
    if forced_kind:
        plan.blog_kind = "news_roundup"  # just in case the model doesnt return it right
    return {"plan": plan}
