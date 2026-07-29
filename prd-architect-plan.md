# The PRD Architect — Implementation Plan

## Top-Level Overview

Build a multi-agent system that translates a raw product concept into a rigorous,
machine-readable PRD (Product Requirements Document). A React/Vite frontend talks to
a FastAPI backend that runs a LangGraph orchestration graph composed of three
specialised subagents. Output is a structured Markdown + JSON PRD written to disk and
streamed to the UI in real time. Everything runs locally; the GitHub repo is the
distribution mechanism. Default LLM provider is Groq (free tier); Ollama is the
local/offline fallback.

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffold & Monorepo Layout

**Status:** `[ ] pending`

**Intent**
Establish the folder structure, tooling config, and dependency manifests for both the
Python backend and the React frontend before any feature code is written. This gives
every subsequent sub-task a clean, consistent place to land.

**Expected Outcomes**
- Repo root contains `backend/`, `frontend/`, `docker-compose.yml`, `.env.example`, `README.md`
- `backend/` is a valid Python package managed by `uv` with `pyproject.toml`
- `frontend/` is a valid Vite + React + Tailwind project
- `docker compose up` starts both services (even if they only return a health-check for now)
- `.github/workflows/ci.yml` runs lint + type-check on every push

**Todo List**
1. Create repo root files: `.gitignore`, `.env.example`, `README.md`, `docker-compose.yml`
2. Scaffold `backend/` with `pyproject.toml` (deps: `fastapi`, `uvicorn`, `langgraph`, `langchain-groq`, `langchain-ollama`, `pydantic`, `python-dotenv`)
3. Create `backend/prd_architect/__init__.py` and a minimal `backend/prd_architect/main.py` with a `/health` endpoint
4. Scaffold `frontend/` with Vite + React + TypeScript template
5. Add Tailwind CSS to the frontend
6. Add `frontend/src/App.tsx` placeholder that calls `/health` and displays the response
7. Create `.github/workflows/ci.yml` for Python lint (`ruff`) + type-check (`mypy`) and frontend build check

**Relevant Context**
- No existing files — greenfield workspace
- Use `uv` for Python dependency management (`uv init`, `uv add`)
- Vite scaffold: `npm create vite@latest frontend -- --template react-ts`
- Docker Compose: two services `backend` (port 8000) and `frontend` (port 5173)

---

### Sub-Task 2 — LangGraph Agent Graph (Backend Core)

**Status:** `[ ] pending`

**Intent**
Implement the four-node LangGraph graph: the PRD Orchestrator plus the three
specialised subagents. Each subagent receives the shared state, calls the LLM with a
focused system prompt, and writes its output back into state. The orchestrator drives
the sequence.

**Expected Outcomes**
- `backend/prd_architect/graph/` contains the graph definition and all node functions
- `backend/prd_architect/graph/state.py` defines the shared `PRDState` Pydantic model
- Running the graph with a sample concept string produces a populated `PRDState` with
  `market_context`, `user_personas`, `user_journeys`, and `acceptance_criteria` fields
- LLM provider (Groq or Ollama) is selected via `LLM_PROVIDER` env var; API key via `GROQ_API_KEY`

**Todo List**
1. Create `backend/prd_architect/graph/state.py` — define `PRDState` with all fields
2. Create `backend/prd_architect/graph/llm.py` — factory function that returns the correct LangChain chat model based on env vars
3. Create `backend/prd_architect/graph/nodes/market_researcher.py` — system prompt + LLM call, populates `market_context` and `user_personas`
4. Create `backend/prd_architect/graph/nodes/ux_specifier.py` — system prompt + LLM call, populates `user_journeys`
5. Create `backend/prd_architect/graph/nodes/technical_translator.py` — system prompt + LLM call, populates `acceptance_criteria`
6. Create `backend/prd_architect/graph/builder.py` — assemble nodes into a `StateGraph`, set edges (orchestrator → A → B → C → END)
7. Add a `__main__` smoke-test: `python -m prd_architect.graph.builder "A task management app for remote teams"`

**Relevant Context**
- LangGraph `StateGraph` with `TypedDict` or Pydantic state
- Each node function signature: `(state: PRDState) -> dict` (partial state update)
- Groq model: `llama-3.3-70b-versatile`; Ollama model: `llama3`
- All prompts are engineering-grade: they must request structured JSON output

---

### Sub-Task 3 — FastAPI Streaming Endpoint

**Status:** `[ ] pending`

**Intent**
Expose the LangGraph graph over HTTP with a Server-Sent Events (SSE) streaming
endpoint so the frontend can display real-time agent progress as each subagent
completes its work.

**Expected Outcomes**
- `POST /generate` accepts `{"concept": "..."}` and streams SSE events
- Each SSE event carries `{"agent": "<name>", "status": "running"|"done", "output": "..."}` 
- A final event carries the complete PRD as both Markdown and JSON
- `GET /health` returns `{"status": "ok"}`
- CORS is configured for `http://localhost:5173`

**Todo List**
1. Add `backend/prd_architect/api/routes.py` with the `POST /generate` SSE route
2. Add `backend/prd_architect/api/schemas.py` — request/response Pydantic models
3. Wire the LangGraph graph into the route: iterate graph stream, emit one SSE event per node completion
4. Add `backend/prd_architect/output/formatter.py` — converts final `PRDState` to Markdown string and JSON dict
5. Write completed PRD files to `backend/outputs/{timestamp}/prd.md` and `prd.json`
6. Update `backend/prd_architect/main.py` to mount the router and configure CORS

**Relevant Context**
- FastAPI SSE: use `fastapi.responses.StreamingResponse` with `media_type="text/event-stream"`
- LangGraph streaming: `graph.stream(input, stream_mode="updates")` yields node-name → output dicts
- `outputs/` directory should be git-ignored but created on first run

---

### Sub-Task 4 — React Frontend UI

**Status:** `[ ] pending`

**Intent**
Build the user-facing web interface: a concept input form, a real-time agent progress
tracker that lights up as each subagent completes, and a final PRD viewer with copy
and download controls.

**Expected Outcomes**
- Single-page app with a clean, modern design (Tailwind + shadcn/ui components)
- User types a concept, hits "Generate PRD", sees three agent cards update live via SSE
- Final PRD is rendered as formatted Markdown in the UI
- "Download .md" and "Download .json" buttons are functional
- UI is fully responsive

**Todo List**
1. Install and configure `shadcn/ui` in the frontend
2. Create `frontend/src/components/ConceptForm.tsx` — textarea + submit button
3. Create `frontend/src/components/AgentProgressCard.tsx` — shows agent name, status badge, and output preview
4. Create `frontend/src/components/PRDViewer.tsx` — renders final Markdown using `react-markdown`
5. Create `frontend/src/hooks/useGeneratePRD.ts` — manages SSE connection, parses events, updates state
6. Wire everything into `frontend/src/App.tsx` with layout and state management
7. Add download handlers for `.md` and `.json` outputs

**Relevant Context**
- SSE in browser: native `EventSource` API or `fetch` with `ReadableStream` (use `fetch` for POST support)
- `react-markdown` for rendering the final PRD
- Tailwind for all styling; shadcn/ui for `Button`, `Card`, `Badge`, `Textarea` primitives

---

### Sub-Task 5 — Integration, Docker Compose & README

**Status:** `[ ] pending`

**Intent**
Wire the backend and frontend together end-to-end, finalise the Docker Compose setup
so the entire system starts with one command, and write the GitHub-ready README with
setup instructions, architecture overview, and contribution guide.

**Expected Outcomes**
- `docker compose up` starts both services; UI at `http://localhost:5173` generates a real PRD
- `.env.example` documents all required and optional env vars
- `README.md` includes: project description, architecture diagram (ASCII or Mermaid), quickstart, env var reference, and how to swap LLM providers
- `CONTRIBUTING.md` explains how to add a new subagent node

**Todo List**
1. Finalise `docker-compose.yml`: backend builds from `backend/Dockerfile`, frontend from `frontend/Dockerfile`
2. Write `backend/Dockerfile` (multi-stage: install deps with `uv`, copy source, run `uvicorn`)
3. Write `frontend/Dockerfile` (multi-stage: `npm ci && npm run build`, serve with `nginx`)
4. End-to-end smoke test: start compose, submit a concept, verify PRD files are written to `backend/outputs/`
5. Write final `README.md`
6. Write `CONTRIBUTING.md`

**Relevant Context**
- Backend Dockerfile base: `python:3.12-slim`
- Frontend Dockerfile base: `node:20-alpine` for build, `nginx:alpine` for serve
- Env vars injected via `docker-compose.yml` `env_file: .env`
- `outputs/` volume-mounted so PRD files persist on the host
