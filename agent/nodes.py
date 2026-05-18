import logging

from langchain_openai import ChatOpenAI

from pydantic import BaseModel, SecretStr

from agent.state import ResearchState
from shared.config import get_settings

class SubQuestions(BaseModel):
    questions: list[str]

logger = logging.getLogger(__name__)


def _get_planner_model() -> ChatOpenAI:
    settings = get_settings()
    openai_api_key = settings.openai_api_key.strip()
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is set but empty")

    # Catch placeholder values early so failures are explicit.
    if "your-openai-api-key" in openai_api_key.lower():
        raise RuntimeError("OPENAI_API_KEY is still a placeholder value")

    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=SecretStr(openai_api_key),
    )


def plan_node(state: ResearchState) -> dict[str, object]:
    """Generate focused sub-questions for the research query."""
    query = state.get("query", "").strip()
    domain = state.get("domain", "").strip()
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

    structured_model = _get_planner_model().with_structured_output(SubQuestions)
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
