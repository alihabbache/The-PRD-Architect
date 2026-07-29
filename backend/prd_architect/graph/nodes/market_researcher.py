from prd_architect.graph.state import PRDState
from prd_architect.graph.llm import get_llm

SYSTEM_PROMPT = """You are a senior market research analyst.
Given a product concept, return a JSON object with exactly two keys:
- "market_context": a concise paragraph describing the target market, key competitors, and market opportunity.
- "user_personas": a list of 2-3 user persona objects, each with fields: name, role, goals, pain_points.

Respond with raw JSON only. No markdown fences, no extra text."""


def market_researcher(state: PRDState) -> dict:
    llm = get_llm()
    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Product concept: {state.concept}"},
    ])

    import json
    data = json.loads(response.content)

    return {
        "market_context": data.get("market_context", ""),
        "user_personas": json.dumps(data.get("user_personas", [])),
    }
