from pydantic import BaseModel, Field
from typing import Literal


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="The research topic to investigate.")
    domain: str = Field(default="", description="Optional domain or industry context.")


class ResearchResponse(BaseModel):
    query: str
    domain: str = ""
    status: Literal["pending", "running", "complete", "failed"] = "complete"
    report: str | None = None
    error: str | None = None
