import logging
from typing import Literal, cast

from langgraph.graph import END, START, StateGraph

from agent.nodes import (
    error_node,
    evaluate_node,
    plan_node,
    search_node,
    synthesise_node,
)
from agent.state import ResearchState

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Node wrapper
# ---------------------------------------------------------------------------

def _safe(node_fn):
    """Wrap a node so any unhandled exception writes to state['error']."""
    def wrapper(state: ResearchState) -> dict[str, object]:
        try:
            return node_fn(state)
        except Exception as exc:
            logger.exception("Node '%s' raised an unhandled exception", node_fn.__name__)
            return {"error": str(exc)}

    wrapper.__name__ = node_fn.__name__
    return wrapper


# ---------------------------------------------------------------------------
# Routing functions
# ---------------------------------------------------------------------------

def _route_after_plan(state: ResearchState) -> Literal["search", "error"]:
    if state.get("error"):
        return "error"
    return "search"


def _route_after_search(state: ResearchState) -> Literal["evaluate", "error"]:
    if state.get("error"):
        return "error"
    return "evaluate"


def _route_after_evaluate(
    state: ResearchState,
) -> Literal["search", "synthesise", "error"]:
    if state.get("error"):
        return "error"
    if state.get("sufficient") or state.get("iteration_count", 0) >= 4:
        return "synthesise"
    return "search"


def _route_after_synthesise(state: ResearchState) -> str:
    if state.get("error"):
        return "error"
    return END


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def _build_graph() -> StateGraph:
    workflow = StateGraph(ResearchState)

    workflow.add_node("plan", _safe(plan_node))
    workflow.add_node("search", _safe(search_node))
    workflow.add_node("evaluate", _safe(evaluate_node))
    workflow.add_node("synthesise", _safe(synthesise_node))
    workflow.add_node("error", error_node)

    workflow.add_edge(START, "plan")
    workflow.add_conditional_edges(
        "plan",
        _route_after_plan,
        {"search": "search", "error": "error"},
    )
    workflow.add_conditional_edges(
        "search",
        _route_after_search,
        {"evaluate": "evaluate", "error": "error"},
    )
    workflow.add_conditional_edges(
        "evaluate",
        _route_after_evaluate,
        {"search": "search", "synthesise": "synthesise", "error": "error"},
    )
    workflow.add_conditional_edges(
        "synthesise",
        _route_after_synthesise,
        {"error": "error", END: END},
    )
    workflow.add_edge("error", END)

    return workflow


_compiled = _build_graph().compile()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_research(query: str, domain: str = "") -> ResearchState:
    """Run the full research pipeline and return the final state."""
    if not query or not query.strip():
        raise ValueError("query must be a non-empty string")

    initial_state: ResearchState = {
        "query": query.strip(),
        "domain": domain.strip(),
        "sub_questions": [],
        "current_question_index": 0,
        "search_results": [],
        "iteration_count": 0,
        "sufficient": False,
        "report": "",
        "error": None,
    }

    logger.info("Starting research: query=%r, domain=%r", query, domain)
    result: ResearchState = cast(ResearchState, _compiled.invoke(initial_state))
    logger.info(
        "Research complete — %s sources, %s chars in report, error=%s",
        len(result.get("search_results", [])),
        len(result.get("report", "")),
        result.get("error"),
    )
    return result


# ---------------------------------------------------------------------------
# CLI — end-to-end run + Mermaid diagram
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pathlib
    import sys
    import textwrap

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    # Save Mermaid diagram
    diagram = _compiled.get_graph().draw_mermaid()
    mmd_path = pathlib.Path(__file__).parent / "graph.mmd"
    mmd_path.write_text(diagram, encoding="utf-8")
    print(f"Graph diagram saved to {mmd_path}\n")
    print(diagram)
    print()

    # End-to-end run
    query = sys.argv[1] if len(sys.argv) > 1 else "AI in retail logistics"
    domain = sys.argv[2] if len(sys.argv) > 2 else "retail"

    print(f"Running research: {query!r} (domain: {domain!r})\n{'=' * 60}")
    state = run_research(query, domain)

    if state.get("error"):
        print(f"\nERROR: {state.get('error')}")
        sys.exit(1)

    print(textwrap.fill(f"Sub-questions answered: {len(state.get('sub_questions', []))}", 80))
    print(f"Sources gathered:       {len(state.get('search_results', []))}")
    print(f"Iterations:             {state.get('iteration_count', 0)}")
    print(f"\n{'=' * 60}\n")
    print(state.get("report", ""))
