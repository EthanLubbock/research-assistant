from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import settings
from api.routes import research


app = FastAPI(title="research-assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router)


@app.get("/health")
def health_check() -> dict[str, str]:
	return {
		"status": "ok",
		"openai_configured": "yes" if bool(settings.openai_api_key) else "no",
		"tavily_configured": "yes" if bool(settings.tavily_api_key) else "no",
	}
