import json
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from prd_architect.api.schemas import GenerateRequest
from prd_architect.graph.builder import build_graph
from prd_architect.graph.state import PRDState
from prd_architect.output.formatter import to_markdown, to_json

logger = logging.getLogger(__name__)

router = APIRouter()

# Absolute anchor for all output writes — prevents path traversal
_OUTPUTS_ROOT = Path("outputs").resolve()

AGENT_LABELS = {
    "market_researcher": "Market Researcher",
    "ux_specifier": "UX Specifier",
    "technical_translator": "Technical Translator",
}


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@router.post("/generate")
async def generate(request: GenerateRequest):
    async def stream():
        try:
            graph = build_graph()

            # Accumulate state across all node updates
            accumulated: dict = {"concept": request.concept}

            for chunk in graph.stream(
                {"concept": request.concept}, stream_mode="updates"
            ):
                for node_name, update in chunk.items():
                    accumulated.update(update)
                    label = AGENT_LABELS.get(node_name, node_name)
                    yield _sse({"agent": label, "status": "done"})

            # Build final state from accumulated updates
            final_state = PRDState(**accumulated)
            md = to_markdown(final_state)
            prd_json = to_json(final_state)

            # Write outputs to disk — path is constructed from a fixed root +
            # a timestamp-only subdirectory, so no user input reaches the filesystem.
            out_dir = _OUTPUTS_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "prd.md").write_text(md, encoding="utf-8")
            (out_dir / "prd.json").write_text(
                json.dumps(prd_json, indent=2), encoding="utf-8"
            )

            yield _sse({
                "agent": "orchestrator",
                "status": "complete",
                "markdown": md,
                "json": prd_json,
            })

        except Exception as exc:
            logger.exception("Error during PRD generation")
            yield _sse({"agent": "orchestrator", "status": "error", "message": "Generation failed. Check server logs."})

    return StreamingResponse(stream(), media_type="text/event-stream")
