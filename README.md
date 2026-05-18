# research-assistant

LangGraph-based research assistant with a FastAPI interface.

## Status

This stage provides the runnable project foundation:

- environment-based configuration loading
- shared request and response models
- FastAPI application bootstrap with CORS
- containerized API service with a health endpoint

## Quick start

1. Copy `.env.example` to `.env` and add your API keys.
2. Run `docker compose up --build`.
3. Check `GET /health` on `http://localhost:8000/health`.
