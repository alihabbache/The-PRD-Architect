# PRD Architect

> A multi-agent system that turns a raw product concept into a full PRD in seconds.

Three specialised AI agents — **Market Researcher**, **UX Specifier**, and **Technical Translator** — run sequentially via a [LangGraph](https://github.com/langchain-ai/langgraph) graph. Progress streams live to the browser via Server-Sent Events. The output is a structured PRD in both Markdown and JSON, downloadable from the UI.

---

## Architecture

```
Browser (React + Vite)
  │  POST /generate  (concept string)
  │  ← SSE stream (agent progress + final PRD)
  ▼
FastAPI  ──►  LangGraph graph
                 │
                 ├─ market_researcher  →  market_context, user_personas
                 ├─ ux_specifier       →  user_journeys
                 └─ technical_translator → acceptance_criteria
                 │
                 └─ formatter  →  prd.md + prd.json  (saved to outputs/)
```

**LLM:** Groq (`llama-3.3-70b-versatile`) by default; switch to Ollama (`llama3`) with one env var.

---

## Quickstart

### Prerequisites
- Python 3.12+ and [`uv`](https://docs.astral.sh/uv/)
- Node.js 20+
- A free [Groq API key](https://console.groq.com) **or** [Ollama](https://ollama.ai) running locally

### 1. Clone & configure

```bash
git clone https://github.com/alihabbache/The-PRD-Architect.git
cd prd-architect
cp .env.example .env
# Edit .env and set your GROQ_API_KEY
```

### 2. Start the backend

```bash
cd backend
uv sync
uv run uvicorn prd_architect.main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**, type a concept, and watch the agents fire.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | `groq` or `ollama` |
| `GROQ_API_KEY` | — | Required when `LLM_PROVIDER=groq` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3` | Ollama model name |

---

## Outputs

Each run creates `backend/outputs/{timestamp}/`:
- `prd.md` — full PRD in Markdown
- `prd.json` — structured PRD as JSON

Both files are also downloadable directly from the UI.

---

## Project Structure

```
.
├── backend/
│   └── prd_architect/
│       ├── main.py               # FastAPI app entry point
│       ├── api/
│       │   ├── routes.py         # POST /generate SSE endpoint
│       │   └── schemas.py        # Request/response models
│       ├── graph/
│       │   ├── builder.py        # LangGraph StateGraph assembly
│       │   ├── state.py          # PRDState Pydantic model
│       │   ├── llm.py            # LLM factory (Groq / Ollama)
│       │   └── nodes/
│       │       ├── market_researcher.py
│       │       ├── ux_specifier.py
│       │       └── technical_translator.py
│       └── output/
│           └── formatter.py      # PRDState → Markdown + JSON
└── frontend/
    └── src/
        ├── App.tsx               # Root layout + state wiring
        ├── components/
        │   ├── ConceptForm.tsx
        │   ├── AgentProgressCard.tsx
        │   ├── PRDViewer.tsx
        │   └── ui/               # shadcn-style primitives
        └── hooks/
            └── useGeneratePRD.ts # SSE client + agent state
```

---

## Smoke-testing the graph directly

```bash
cd backend
uv run python -m prd_architect.graph.builder "A mobile app for remote async standups"
```

This bypasses the HTTP layer and prints the raw `PRDState` JSON to stdout.
