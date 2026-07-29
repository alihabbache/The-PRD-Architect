import json
from prd_architect.graph.state import PRDState


def to_markdown(state: PRDState) -> str:
    personas = json.loads(state.user_personas or "[]")
    journeys = json.loads(state.user_journeys or "[]")
    criteria = json.loads(state.acceptance_criteria or "[]")

    lines = [
        f"# PRD: {state.concept}",
        "",
        "## Market Context",
        "",
        state.market_context or "",
        "",
        "## User Personas",
        "",
    ]

    for p in personas:
        lines += [
            f"### {p.get('name', 'Persona')} — {p.get('role', '')}",
            f"**Goals:** {', '.join(p.get('goals', []))}",
            f"**Pain Points:** {', '.join(p.get('pain_points', []))}",
            "",
        ]

    lines += ["## User Journeys", ""]
    for j in journeys:
        lines += [
            f"### {j.get('persona', '')} — {j.get('goal', '')}",
            "**Steps:**",
        ]
        for i, step in enumerate(j.get("steps", []), 1):
            lines.append(f"{i}. {step}")
        lines += [
            "",
            "**Pain Points:**",
        ]
        for pp in j.get("pain_points", []):
            lines.append(f"- {pp}")
        lines.append("")

    lines += ["## Acceptance Criteria", ""]
    for c in criteria:
        priority = c.get("priority", "should").upper()
        lines += [
            f"### [{priority}] {c.get('feature', '')}",
            f"- **Given:** {c.get('given', '')}",
            f"- **When:** {c.get('when', '')}",
            f"- **Then:** {c.get('then', '')}",
            "",
        ]

    return "\n".join(lines)


def to_json(state: PRDState) -> dict:
    return {
        "concept": state.concept,
        "market_context": state.market_context,
        "user_personas": json.loads(state.user_personas or "[]"),
        "user_journeys": json.loads(state.user_journeys or "[]"),
        "acceptance_criteria": json.loads(state.acceptance_criteria or "[]"),
    }
