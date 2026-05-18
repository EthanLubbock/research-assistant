from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from shared.models import ResearchRequest, ResearchResponse
from agent.graph import run_research

router = APIRouter()

@router.post("/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchRequest, req: Request) -> ResearchResponse:
	try:
		result = run_research(request.query, request.domain)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc))

	return ResearchResponse(
		query=result.get("query", request.query),
		domain=result.get("domain", request.domain),
		status="failed" if result.get("error") else "complete",
		report=result.get("report"),
		error=result.get("error"),
	)
