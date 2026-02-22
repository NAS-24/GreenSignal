🌿 Green Signal AI: Agentic Sustainability Auditor
Green Signal is a high-performance, Agentic AI system designed to dismantle "Greenwashing" in the D2C (Direct-to-Consumer) industry. By utilizing a multi-agent workflow, it transforms vague marketing claims into verifiable, quantitative trust scores.

🚀 The Core Problem
Most consumers are overwhelmed by buzzwords like "eco-friendly" or "natural." Current solutions are either manual or rely on simple AI summarization of a brand’s own marketing. Green Signal solves this by acting as an independent, third-party auditor that treats every claim as "unverified" until proven against official registries.

🧠 System Architecture & Flow
Unlike linear pipelines, Green Signal uses an Agentic Reasoning-Action (ReAct) Loop.

Surgical Extraction: A specialized scraper bypasses anti-bot layers to pull raw product text.

Claim Categorization: Llama 3.1 8B identifies and categorizes specific sustainability claims (e.g., GOTS, B-Corp).

Federated Verification: The agent prioritizes "Silos of Truth"—local SQL registries of official bodies—before falling back to live web searches via Tavily.

Trust Scoring: A weighted engine calculates a score (0–100) across six key parameters.

✨ Key Features
Agentic Reasoning: Uses LangGraph to manage state and allow the agent to autonomously decide when it has enough evidence to conclude an audit.

Self-Healing Logic: If a scraper is blocked, the agent autonomously extracts the brand from the URL and pivots its research strategy.

Greenwashing Detection: Identifies "Red Flags" by cross-referencing claims with actual license IDs and certificate status.

Professional Output: Delivers a strict, industry-standard JSON audit report ready for any frontend integration.

🛠️ Tech Stack
Brain: Llama 3.1 8B (via Groq LPU for low-latency inference).

Orchestration: LangGraph & FastAPI.

Tools: Tavily Search API, ScraperAPI, BeautifulSoup4.

Vercel:- https://green-signal-five.vercel.app/

Database: SQLite (Federated Sustainability Registries).

Deployment: Render (Uvicorn/FastAPI).
