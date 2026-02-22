import os
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import your agent and scraper logic
from src.scraper_module import run_extraction_pipeline
from src.agent_router import app as langgraph_app

app = FastAPI(title="Green Signal API")

# Define the request structure
class AuditRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "Green Signal Sustainability Auditor API is Online"}

@app.post("/audit")
async def perform_audit(request: AuditRequest):
    """
    Triggers the 3-Phase Audit Pipeline via API.
    """
    url = request.url.strip()
    
    # --- PHASE 1: EXTRACTION ---
    print(f"[*] Starting Phase 1 (Extraction) for: {url}")
    extracted = run_extraction_pipeline(url)
    
    # Self-Healing: Handle scraper failures
    if "error" in extracted:
        # Extract brand name from URL if scraper hits a 500
        brand = url.split("://")[-1].split("/")[0].replace("www.", "").split(".")[0].capitalize()
        extracted_data = {"brand_name": brand, "claims_found": []}
    else:
        brand = extracted["brand_name"]
        extracted_data = extracted

    # --- PHASE 2: AGENTIC AUDIT ---
    print(f"[*] Starting Phase 2 (Agentic Reasoning) for: {brand}")
    try:
        # Invoke the LangGraph workflow to query federated registries
        final_state = langgraph_app.invoke({
            "brand_name": brand,
            "claims_found": extracted_data.get("claims_found", []),
            "messages": []
        })
        
        # --- PHASE 3: PARSING & RESPONSE ---
        # Get the professional JSON structure from the summary node
        audit_json = final_state.get("final_audit", "{}")
        
        # Parse and return as a direct JSON response
        report = json.loads(audit_json)
        return report

    except Exception as e:
        print(f"Audit Failure: {e}")
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Local testing command: python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)