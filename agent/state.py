from typing import TypedDict, NotRequired


class SearchResult(TypedDict):
    title: str
    url: str
    content: str


class ResearchState(TypedDict):
    query: str
    domain: str
    sub_questions: NotRequired[list[str]]
    current_question_index: NotRequired[int]
    search_results: NotRequired[list[SearchResult]]
    iteration_count: NotRequired[int]
    sufficient: NotRequired[bool]
    report: NotRequired[str]
    sources: NotRequired[list[dict[str, str]]]
    error: NotRequired[str | None]
