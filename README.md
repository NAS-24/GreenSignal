# 🌿 Green Signal AI: Agentic Sustainability Auditor

**Green Signal** is a high-performance, Agentic AI auditing system designed to combat greenwashing in the Direct-to-Consumer (D2C) industry. Instead of trusting marketing language, the system independently verifies sustainability claims and converts them into quantifiable trust scores backed by evidence.

## 🚀 The Core Problem
Modern consumers are flooded with vague sustainability buzzwords such as "eco-friendly," "natural," and "sustainable." Current solutions suffer from major limitations:
* **Manual verification** is slow and impractical.
* **Most AI tools** only summarize brand marketing content.
* **Claims are rarely validated** against official certification bodies.

Green Signal solves this by acting as an independent third-party AI auditor, treating every sustainability claim as unverified until proven using trusted registries and verified sources.

## 🧠 System Architecture & Workflow
Green Signal operates using an **Agentic Reasoning-Action (ReAct) Loop**, enabling dynamic decision-making instead of a fixed pipeline.

1. **Surgical Data Extraction:** Specialized scraper bypasses anti-bot protections. Extracts raw product and brand sustainability content.
2. **Claim Categorization:** Llama 3.1 8B identifies and classifies sustainability claims (e.g., GOTS Certified, B-Corp, Carbon Neutral).
3. **Federated Verification:** Agent prioritizes trusted internal databases (**"Silos of Truth"**): Local SQLite registries of official certification bodies. Falls back to live verification using Tavily Search API when needed.
4. **Trust Scoring Engine:** Weighted evaluation model generates a 0–100 sustainability trust score across six verification parameters.

## ✨ Key Features
* **Agentic Reasoning:** Powered by LangGraph, allowing autonomous decision-making and state management.
* **Self-Healing Workflow:** If scraping fails, the agent extracts brand identity and dynamically switches research strategies.
* **Greenwashing Detection:** Cross-checks marketing claims with certification IDs and registry status. Flags misleading or unverifiable claims.
* **Professional Audit Output:** Generates structured, industry-ready JSON audit reports for seamless frontend integration.

## 🛠️ Tech Stack
| Component | Technology |
| :--- | :--- |
| **AI Model (Brain)** | Llama 3.1 8B (Groq LPU – low latency inference) |
| **Orchestration** | LangGraph, FastAPI |
| **Data Tools** | Tavily Search API, ScraperAPI, BeautifulSoup4 |
| **Database** | SQLite (Federated Sustainability Registries) |
| **Deployment (Backend)** | Render (FastAPI + Uvicorn) |
| **Frontend** | Vercel |

## 🌐 Live Demo
🔗 [https://green-signal-five.vercel.app/](https://green-signal-five.vercel.app/)
