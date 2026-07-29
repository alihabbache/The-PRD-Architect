from langgraph.graph import StateGraph, END
from prd_architect.graph.state import PRDState
from prd_architect.graph.nodes.market_researcher import market_researcher
from prd_architect.graph.nodes.ux_specifier import ux_specifier
from prd_architect.graph.nodes.technical_translator import technical_translator


def build_graph():
    graph = StateGraph(PRDState)

    graph.add_node("market_researcher", market_researcher)
    graph.add_node("ux_specifier", ux_specifier)
    graph.add_node("technical_translator", technical_translator)

    graph.set_entry_point("market_researcher")
    graph.add_edge("market_researcher", "ux_specifier")
    graph.add_edge("ux_specifier", "technical_translator")
    graph.add_edge("technical_translator", END)

    return graph.compile()


# Smoke test: python -m prd_architect.graph.builder
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()

    concept = sys.argv[1] if len(sys.argv) > 1 else "A task management app for remote teams"
    app = build_graph()
    result = app.invoke({"concept": concept})
    import json
    print(json.dumps(result, indent=2))
