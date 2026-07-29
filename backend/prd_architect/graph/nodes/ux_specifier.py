import json
from prd_architect.graph.state import PRDState
from prd_architect.graph.llm import get_llm

SYSTEM_PROMPT = """You are a senior UX designer.
Given a product concept and a set of user personas, return a JSON object with one key:
- "user_journeys": a list of journey objects. Each journey has fields:
  persona (string), goal (string), steps (list of strings), pain_points (list of strings).

Respond with raw JSON only. No markdown fences, no extra text."""


def ux_specifier(state: PRDState) -> dict:
    llm = get_llm()
    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Product concept: {state.concept}\n\n"
            f"User personas: {state.user_personas}"
        )},
    ])

    data = json.loads(response.content)

    return {
        "user_journeys": json.dumps(data.get("user_journeys", [])),
    }
