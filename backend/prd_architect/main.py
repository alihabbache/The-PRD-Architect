from dotenv import load_dotenv
load_dotenv()

import os
import time
from collections import defaultdict, deque
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
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


# ── Rate limiting for the LLM-backed endpoint ────────────────────────────────
# Simple in-memory sliding window per client IP (single-process deployments).
# Each /generate call spends LLM quota, so unauthenticated bursts are capped.
# Tune with RATE_LIMIT_MAX / RATE_LIMIT_WINDOW_SECONDS. Behind a reverse proxy,
# configure uvicorn --proxy-headers so request.client reflects the real client.
_RATE_MAX = int(os.getenv("RATE_LIMIT_MAX", "5"))
_RATE_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
_hits: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def rate_limit(request: Request, call_next) -> Response:
    if request.method == "POST" and request.url.path == "/generate":
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = _hits[ip]
        while window and now - window[0] > _RATE_WINDOW:
            window.popleft()
        if len(window) >= _RATE_MAX:
            return JSONResponse(
                {"detail": "Too many requests. Please retry later."},
                status_code=429,
                headers={"Retry-After": str(_RATE_WINDOW)},
            )
        window.append(now)
        if len(_hits) > 10_000:  # bound memory: drop idle clients
            for k in [k for k, v in _hits.items() if not v]:
                del _hits[k]
    return await call_next(request)


@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    # Remove the server fingerprint header
    if "server" in response.headers:
        del response.headers["server"]
    return response


app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}
