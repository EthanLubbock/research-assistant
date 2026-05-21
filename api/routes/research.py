import logging
from fastapi import APIRouter, HTTPException, Request
from shared.models import ResearchRequest, ResearchResponse
from agent.graph import run_research
import time

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchRequest, req: Request) -> ResearchResponse:
	logger.info("Research request received: query=%s domain=%s", request.query, request.domain)
	start = time.perf_counter()
	try:
		result = run_research(request.query, request.domain)
	except Exception as exc:
		logger.exception("Research failed: %s", exc)
		raise HTTPException(status_code=500, detail=str(exc))
	elapsed = time.perf_counter() - start
	logger.info("Research completed in %.2fs", elapsed)
	return ResearchResponse(
		query=result.get("query", request.query),
		domain=result.get("domain", request.domain),
		status="failed" if result.get("error") else "complete",
		report=result.get("report"),
		sources=result.get("sources", []),
		error=result.get("error"),
	)

