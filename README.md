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

1. Copy `.env.example` to `.env` and fill in keys
2. `docker compose up --build`
3. POST to `/research` (example below)

## Example request

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "AI applications in retail logistics", "domain": "retail"}'
```

## Example response

### Executive Summary

Artificial intelligence (AI) is revolutionizing retail logistics by enhancing supply chain management, inventory control, and operational efficiency. Key applications include predictive analytics, digital twins, and AI-powered platforms that optimize logistics processes. Notable tools such as IBM's Food Trust platform demonstrate the integration of AI with blockchain for supply chain transparency. However, challenges such as data privacy and the complexity of AI implementation remain. Retailers are encouraged to adopt AI technologies strategically to maximize their return on investment and agility in the market.

### Key Use Cases

AI applications in retail logistics are diverse and impactful. Predictive analytics is a significant use case, helping retailers anticipate demand and optimize inventory levels, as highlighted in "AI in Retail Supply Chain | ThroughPut AI." Digital twins, which create virtual models of physical supply chains, enable real-time monitoring and decision-making (Nomtek). AI is also used in platforms like IBM's Food Trust to enhance transparency and traceability in the food supply chain by combining AI with blockchain technology (RTS Labs). These technologies collectively improve efficiency and reduce costs across the retail logistics spectrum.

### Notable Tools and Vendors

Several tools and vendors are leading the charge in AI applications for retail logistics. IBM's Food Trust platform is a prominent example, leveraging AI and blockchain to monitor the food supply chain (RTS Labs). This platform exemplifies how AI can be integrated with other technologies to enhance supply chain transparency. Additionally, companies like ThroughPut AI are providing solutions that drive efficiency and predictive analytics in the retail supply chain (ThroughPut AI). These vendors offer innovative solutions that are transforming logistics operations in the retail sector.

### Risks and Limitations

Despite the advantages, AI in retail logistics presents certain risks and limitations. Data privacy concerns are paramount, as the integration of AI requires access to vast amounts of sensitive information (NetSuite). The complexity of implementing AI solutions can also be a barrier, requiring significant investment in technology and expertise (Nomtek). Additionally, there is a risk of over-reliance on AI systems, which may lead to vulnerabilities if the technology fails or is not properly managed (RTS Labs). These challenges necessitate careful consideration and strategic planning by retailers.

### Recommended Next Steps

To effectively leverage AI in retail logistics, decision-makers should consider the following actions:

1. **Conduct a Needs Assessment**: Evaluate the specific logistics challenges and opportunities within the organization to identify where AI can provide the most value.
2. **Invest in Training and Expertise**: Develop internal capabilities by investing in training programs to equip staff with the skills needed to implement and manage AI technologies.

3. **Pilot AI Solutions**: Start with pilot projects to test AI applications in a controlled environment, allowing for adjustments and learning before full-scale implementation.

4. **Prioritize Data Security**: Implement robust data privacy measures to protect sensitive information and comply with regulatory requirements.

5. **Collaborate with Trusted Vendors**: Partner with reputable AI vendors like IBM and ThroughPut AI to access cutting-edge technologies and industry expertise.

By taking these steps, retailers can strategically integrate AI into their logistics operations, enhancing efficiency and competitiveness in the market.

## Project structure

research-assistant/
├── agent/
│ ├── state.py # ResearchState TypedDict - the shared memory passed between nodes
│ ├── tools.py # Tavily search wrapper - isolated so the provider can be swapped
│ ├── nodes.py # One function per graph node: plan, search, evaluate, synthesise, error
│ └── graph.py # Assembles the StateGraph, defines edges and loop logic, exposes run_research()
│
├── api/
│ ├── main.py # FastAPI app initialisation and CORS configuration
│ ├── routes/
│ │ └── research.py # POST /research and GET /health endpoints
│ ├── Dockerfile
│ └── requirements.txt
│
├── shared/
│ ├── config.py # Loads and validates environment variables, exposes a cached Settings object
│ └── models.py # Pydantic schemas for API request and response validation
│
├── docker-compose.yml # Single-service compose config for the API container
├── .env.example # Required environment variables - copy to .env to run locally
└── README.md

### Environment variables

| Variable         | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini calls                           |
| `TAVILY_API_KEY` | Tavily API key for web search (free tier: 1000 searches/month) |
