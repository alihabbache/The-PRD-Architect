import json
from prd_architect.graph.state import PRDState
from prd_architect.graph.llm import get_llm

SYSTEM_PROMPT = """You are a senior software engineer writing acceptance criteria.
Given a product concept and user journeys, return a JSON object with one key:
- "acceptance_criteria": a list of feature objects. Each feature has fields:
  feature (string), given (string), when (string), then (string), priority ("must"|"should"|"could").

Use the Gherkin Given/When/Then format. Be precise and testable.
Respond with raw JSON only. No markdown fences, no extra text."""


def technical_translator(state: PRDState) -> dict:
    llm = get_llm()
    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Product concept: {state.concept}\n\n"
            f"User journeys: {state.user_journeys}"
        )},
    ])

    data = json.loads(response.content)

    return {
        "acceptance_criteria": json.dumps(data.get("acceptance_criteria", [])),
    }
