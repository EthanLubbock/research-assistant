# research-assistant

An autonomous research agent built with LangGraph and FastAPI.
Submit a topic → the agent plans sub-questions, searches the web,
evaluates whether it has enough information, and returns a
structured briefing.

## Architecture

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	plan(plan)
	search(search)
	evaluate(evaluate)
	synthesise(synthesise)
	error(error)
	__end__([<p>__end__</p>]):::last
	__start__ --> plan;
	evaluate -.-> error;
	evaluate -.-> search;
	evaluate -.-> synthesise;
	plan -.-> error;
	plan -.-> search;
	search -.-> error;
	search -.-> evaluate;
	synthesise -.-> __end__;
	synthesise -.-> error;
	error --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

## How it works

1. **plan** - breaks the query into 3 to 5 focused sub-questions using GPT-4o-mini
2. **search** - takes each sub-question and retrieves results via the Tavily web search API
3. **evaluate** - assesses whether the accumulated results are sufficient to write a thorough briefing; if not, loops back to search (capped at 4 iterations)
4. **synthesise** - combines all search results into a structured report with five sections: executive summary, key use cases, notable tools and vendors, risks and limitations, and recommended next steps
5. **error** - catches any failure in the graph and returns a clean error message rather than crashing

## Quick start

### 1. Configure environment variables

Copy `.env.example` to `.env` and fill in keys

### 2. Start the backend

```bash
docker compose up --build
```

The API will then be available at `http://localhost:8000`

### 3. Start the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The app will then be available at `http://localhost:5173`

## Example API request

If using the API directly (i.e. not via frontend) the below is an example POST request

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "AI applications in retail logistics", "domain": "retail"}'
```

### Environment variables (to add to .env)

| Variable         | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini calls                           |
| `TAVILY_API_KEY` | Tavily API key for web search (free tier: 1000 searches/month) |
