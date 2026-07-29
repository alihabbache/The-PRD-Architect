from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prd_architect.api.routes import router
from prd_architect.api.schemas import HealthResponse

# ── Startup guard: fail fast if required env vars are missing ─────────────────
_provider = os.getenv("LLM_PROVIDER", "groq").lower()
if _provider == "groq" and not os.getenv("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY is not set. Copy .env.example to .env and add your key, "
        "or set LLM_PROVIDER=ollama to use a local model."
    )

# ── Allowed origins ───────────────────────────────────────────────────────────
# In production override with the real frontend URL via ALLOWED_ORIGINS env var.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app = FastAPI(
    title="PRD Architect",
    version="0.1.0",
    # Disable the auto-generated docs in non-dev environments
    docs_url="/docs" if os.getenv("APP_ENV", "development") == "development" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    # Remove the server fingerprint header
    response.headers.pop("server", None)
    return response


app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}
