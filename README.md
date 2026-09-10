# MeowBlogs

**Turn a single topic into a researched, well-structured technical blog post.**

MeowBlogs runs a [LangGraph](https://github.com/langchain-ai/langgraph) agent pipeline that
decides whether the topic needs live web research, gathers evidence, drafts an outline, writes
every section in parallel, and generates diagrams — then hands you editable Markdown you can
copy or download.

 <img width="1430" height="825" alt="download (13)" src="https://github.com/user-attachments/assets/a6d88bb1-2e4b-487e-9ea8-19862cc74010" />


## Short description

MeowBlogs is an AI blog-generation studio. Give it a topic and it routes the request (closed-book
vs. web-researched), researches with Tavily when needed, plans a multi-section outline, fans out
parallel workers to write each section, merges everything, then plans and renders supporting
diagrams with OpenAI image models — all streamed live to a React editor UI and saved to a local
history library.

---

## Features

- **Adaptive research** — a router classifies each topic as `closed_book`, `hybrid`, or `open_book`
  and only searches the web when freshness matters.
- **Evidence grounding** — Tavily results are deduped and filtered by recency, then cited in the text.
- **Parallel writing** — one worker per section, executed concurrently via LangGraph `Send`.
- **Automatic diagrams** — up to 3 images planned per post and generated with `gpt-image-1-mini`.
- **Live progress** — Server-Sent Events stream every pipeline step to the UI.
- **Editable output** — split/edit/preview Markdown editor with copy and download.
- **Saved history** — every generation is persisted to SQLite and browsable in the app.

---

## Architecture

```
        ┌───────────────┐
topic ─►│  router_node  │  classify: needs_research? mode?
        └───────┬───────┘
      needs_research?
        ┌───────┴─────────┐
        ▼                 ▼
 ┌──────────────┐   (closed_book)
 │ research_node│◄─ Tavily search + evidence synthesis
 └──────┬───────┘
        ▼
 ┌───────────────┐
 │  orchestrator │  builds Plan: 5–9 sections (tasks)
 └───────┬───────┘
         ▼  fanout (Send) — one per task
 ┌───────────────┐
 │  worker xN    │  writes each section (parallel)
 └───────┬───────┘
         ▼
 ┌──────────────────────── reducer subgraph ─────────────────────────┐
 │  merge_content ─► decide_images ─► generate_and_place_images      │
 └───────────────────────────────┬───────────────────────────────────┘
                                 ▼
                    final Markdown + generated images
```

The same graph is defined in the notebook at
[`learning_cmpx/1main_research_fineimages.ipynb`](learning_cmpx/1main_research_fineimages.ipynb),
which is the source of truth for the agent logic.

---

## Tech stack

| Layer      | Tech |
|------------|------|
| Agents     | LangGraph, LangChain Core |
| LLM        | OpenAI (`gpt-5.4-mini` by default) via `langchain-openai` |
| Research   | Tavily (`langchain-community`) |
| Images     | OpenAI `gpt-image-1-mini` |
| Backend    | FastAPI, Uvicorn, SQLAlchemy + SQLite, SSE |
| Frontend   | React 18, Vite, React Router, Tailwind CSS, `@uiw/react-md-editor`, FontAwesome |

---

## Project structure

```
blogAgent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app (CORS, /images mount, lifespan)
│   │   ├── config.py               # env loading, paths, model names
│   │   ├── llm.py                  # shared LLM client
│   │   ├── graph.py                # LangGraph wiring (parent + reducer subgraph)
│   │   ├── db.py / models.py       # SQLite history store
│   │   ├── schemas/                # Pydantic schemas + graph State
│   │   ├── nodes/                  # one file per agent node
│   │   ├── tools/tavily.py         # web search helper
│   │   ├── services/openai_image.py# image generation helper
│   │   └── routers/blog.py         # SSE generate + history routes
│   ├── outputs/                    # generated .md + images/ (gitignored)
│   ├── blog.db                     # SQLite history (gitignored)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/                  # Landing, Generator, History
│       ├── components/             # Navbar, MarkdownEditor, ProgressTimeline, ui/
│       └── lib/                    # API/SSE client, utils, icon shim
├── learning_cmpx/                  # notebooks (agent source of truth) + samples
└── .env                            # API keys (not committed)
```

---

## Getting started

### Prerequisites

- Python 3.11+ (project venv uses 3.13) and Node 18+
- API keys: **OpenAI** and **Tavily**

### 1. Environment

Create a `.env` in the project root:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### 2. Backend

```bash
cd backend
# install deps (the repo already includes blogvenv/)
../blogvenv/bin/pip install -r requirements.txt

# run on port 8000
../blogvenv/bin/python -m uvicorn app.main:app --reload --port 8000
```

Verify: <http://127.0.0.1:8000/api/health> → `{"status":"ok"}`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The Vite dev server proxies `/api` and `/images` to
`http://127.0.0.1:8000` (override with `VITE_BACKEND_URL`).

---

## API reference

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/blog/generate` | Runs the full pipeline, streams progress via **SSE** |
| `GET`  | `/api/blogs` | List saved blogs (summaries) |
| `GET`  | `/api/blogs/{id}` | Fetch a saved blog with Markdown |
| `DELETE` | `/api/blogs/{id}` | Delete a saved blog |
| `GET`  | `/api/health` | Health check |
| `GET`  | `/images/{file}` | Static generated images |

### SSE events

`POST /api/blog/generate` with `{ "topic": "..." }` emits:

| Event      | Payload |
|------------|---------|
| `start`    | `{ topic, as_of }` |
| `progress` | `{ node, status, mode, needs_research }` |
| `plan`     | the structured `Plan` (title, sections, kind) |
| `evidence` | `{ count, items[] }` from web research |
| `section`  | `{ task_id, markdown }` as each worker finishes |
| `images`   | `{ count, specs[] }` |
| `done`     | `{ id, title, markdown, file_path, ... }` |
| `error`    | `{ message }` |

---

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | — | LLM + image generation |
| `TAVILY_API_KEY` | — | Web research |
| `BLOG_LLM_MODEL` | `gpt-5.4-mini` | Text LLM for all nodes |
| `BLOG_OPENAI_IMAGE_MODEL` | `gpt-image-1-mini` | Diagram generation |
| `VITE_BACKEND_URL` | `http://127.0.0.1:8000` | Frontend dev proxy target |

Generated posts are written to `backend/outputs/` and images to `backend/outputs/images/`.
History is stored in `backend/blog.db`.

---

## Notes

- The LangGraph nodes are ported 1:1 from
  `learning_cmpx/1main_research_fineimages.ipynb`; keep them in sync when the notebook changes.
- Image generation is the slowest step and is billed per image; keep prompts to a minimum.
- Only `backend/outputs/`, `backend/blog.db`, `.env`, and `node_modules`/`dist` are gitignored —
  never commit secrets.
