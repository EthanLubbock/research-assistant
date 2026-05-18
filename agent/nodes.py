import logging

from langchain_openai import ChatOpenAI

from pydantic import BaseModel, SecretStr

from agent.state import ResearchState
from agent.tools import tavily_search
from shared.config import get_settings

class SubQuestions(BaseModel):
    questions: list[str]


class SufficiencyDecision(BaseModel):
    sufficient: bool

logger = logging.getLogger(__name__)


def _get_model(model: str, temperature: float = 0) -> ChatOpenAI:
    settings = get_settings()
    openai_api_key = settings.openai_api_key.strip()
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is set but empty")

    # Catch placeholder values early so failures are explicit.
    if "your-openai-api-key" in openai_api_key.lower():
        raise RuntimeError("OPENAI_API_KEY is still a placeholder value")

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=SecretStr(openai_api_key),
    )


def plan_node(state: ResearchState) -> dict[str, object]:
    """Generate focused sub-questions for the research query."""
    query = state.get("query", "").strip()
    domain = state.get("domain", "").strip()
    logger.info("plan_node: generating sub-questions for query=%s domain=%s", query, domain)
    if not query:
        raise ValueError("State 'query' must be provided for planning")

    domain_text = domain if domain else "general"
    prompt = (
        "You are a research planning assistant. "
        "Break a research query into 3 to 5 concrete sub-questions that can be answered "
        "with web search.\n\n"
        f"Research query: {query}\n"
        f"Domain context: {domain_text}\n"
    )

    structured_model = _get_model(model="gpt-4o-mini", temperature=0).with_structured_output(SubQuestions)
    response = structured_model.invoke(prompt)
    if isinstance(response, SubQuestions):
        sub_questions = response.questions
    elif isinstance(response, dict):
        sub_questions = [str(item).strip() for item in response.get("questions", []) if str(item).strip()]
    else:
        raise ValueError("Planner returned an unsupported response format")

    logger.info("Generated %s sub-questions", len(sub_questions))
    return {
        "sub_questions": sub_questions,
        "current_question_index": 0,
        "iteration_count": state.get("iteration_count", 0),
        "error": None,
    }


def search_node(state: ResearchState) -> dict[str, object]:
    """Search for the next unanswered sub-question and append results to state."""
    sub_questions = state.get("sub_questions", [])
    current_index = state.get("current_question_index", 0)
    if current_index >= len(sub_questions):
        logger.warning("search_node called but no sub-question at index %s", current_index)
        return {"iteration_count": state.get("iteration_count", 0) + 1}
    question = sub_questions[current_index]
    logger.info("search_node: searching for '%s' (%d/%d)", question, current_index + 1, len(sub_questions))
    results = tavily_search(question)
    existing = list(state.get("search_results", []))
    return {
        "search_results": existing + results,
        "current_question_index": current_index + 1,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


def evaluate_node(state: ResearchState) -> dict[str, object]:
    """Decide whether accumulated search results are sufficient to write a report."""
    iteration_count = state.get("iteration_count", 0)
    query = state.get("query", "")
    search_results = state.get("search_results", [])
    if iteration_count >= 4:
        logger.info("evaluate_node: hard cap reached (%d iterations), marking sufficient", iteration_count)
        return {"sufficient": True}
    results_text = "\n\n".join(
        f"Title: {r.get('title', '')}\nURL: {r.get('url', '')}\nContent: {r.get('content', '')}"
        for r in search_results
    )
    prompt = (
        "You are a research quality evaluator. "
        "Given a research query and the search results collected so far, decide whether the "
        "results are sufficient to write a comprehensive research briefing covering the key "
        "aspects, depth, and relevance of the topic.\n\n"
        f"Research query: {query}\n\n"
        f"Search results collected:\n{results_text}\n"
    )
    structured_model = _get_model(model="gpt-4o-mini", temperature=0).with_structured_output(SufficiencyDecision)
    response = structured_model.invoke(prompt)
    if isinstance(response, SufficiencyDecision):
        sufficient = response.sufficient
    elif isinstance(response, dict):
        sufficient = bool(response.get("sufficient", False))
    else:
        sufficient = False
    logger.info("evaluate_node: sufficient=%s iteration=%d", sufficient, iteration_count)
    return {"sufficient": sufficient}


def synthesise_node(state: ResearchState) -> dict[str, object]:
    """Write a structured research report from all accumulated search results."""
    query = state.get("query", "")
    domain = state.get("domain", "").strip()
    search_results = state.get("search_results", [])
    logger.info("synthesise_node: generating report for query=%s domain=%s", query, domain)
    results_text = "\n\n".join(
        f"Source: {r.get('title', '')} ({r.get('url', '')})\n{r.get('content', '')}"
        for r in search_results
    )
    domain_text = f" in the {domain} sector" if domain else ""
    prompt = (
        f"You are an expert research analyst. Using only the sources provided below, write a "
        f"comprehensive research briefing on the following topic{domain_text}.\n\n"
        f"Topic: {query}\n\n"
        f"Sources:\n{results_text}\n\n"
        "Structure your report with exactly these five sections. Use markdown headings.\n\n"
        "## Executive Summary\n"
        "A concise 3-4 sentence overview of the key findings.\n\n"
        "## Key Use Cases\n"
        "The most important real-world applications and how they are being used.\n\n"
        "## Notable Tools and Vendors\n"
        "Specific products, platforms, or companies mentioned in the sources.\n\n"
        "## Risks and Limitations\n"
        "Challenges, drawbacks, or concerns raised by the sources.\n\n"
        "## Recommended Next Steps\n"
        "Concrete actions a decision-maker could take based on these findings.\n\n"
        "Write in a professional tone. Cite source titles inline where relevant. "
        "Do not invent information not present in the sources."
    )
    model = _get_model(model="gpt-4o", temperature=0.3)
    response = model.invoke(prompt)
    report = response.content if isinstance(response.content, str) else str(response.content)
    logger.info("synthesise_node: report generated (%d chars, %d sources)", len(report), len(search_results))
    return {"report": report, "error": None}


def error_node(state: ResearchState) -> dict[str, object]:
    """Capture an unhandled exception message into state without crashing the graph."""
    existing_error = state.get("error")
    if existing_error:
        logger.error("error_node reached with: %s", existing_error)
        return {}

    logger.error("error_node reached but no error message was set in state")
    return {"error": "An unknown error occurred during research."}
