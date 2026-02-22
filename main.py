import json
import os
import sys
import re
from src.scraper_module import run_extraction_pipeline
from src.agent_router import app 

def run_audit_system(url: str):
    print("\n" + "═"*60)
    print(" 🌿 GREEN SIGNAL: AI SUSTAINABILITY AUDITOR")
    print("═"*60)

    # --- PHASE 1: SMART SCRAPING ---
    print("\n[PHASE 1] Extracting Claims & Brand Data...")
    extracted = run_extraction_pipeline(url)
    
    # Self-Healing: If scraper fails, keep going with brand from URL
    if "error" in extracted:
        print(f"⚠️ Scraper Alert: {extracted['error']}")
        brand = url.split("://")[-1].split("/")[0].replace("www.", "").split(".")[0].capitalize()
        print(f"[*] Self-Healing: Auditing via General Search for: {brand}")
        extracted_data = {"brand_name": brand, "claims_found": []}
    else:
        brand = extracted["brand_name"]
        extracted_data = extracted

    # --- PHASE 2: AGENTIC VERIFICATION ---
    print(f"\n[PHASE 2] Starting Agentic Reasoning for: {brand}...")
    # This triggers the federated registry lookups and Tavily fallbacks
    final_state = app.invoke({
        "brand_name": brand,
        "claims_found": extracted_data.get("claims_found", []),
        "messages": []
    })

    # --- PHASE 3: REPORTING & EXPORT ---
    print("\n[PHASE 3] Finalizing Professional Audit Report...")
    try:
        # Extract and parse the structured JSON from the agent
        audit_json = final_state.get("final_audit", "{}")
        report = json.loads(audit_json)
        
        # Save the detailed report to your disk
        filename = f"audit_report_{brand.lower()}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=4)
            
        # Final Dashboard View
        print("\n" + "█"*60)
        print(f"📋 BRAND: {report.get('brandName', brand)}")
        print(f"⭐ TRUST SCORE: {report.get('sustainabilityScore', 'N/A')}/100")
        print(f"⚖️ VERDICT: {report.get('recommendation', {}).get('verdict', 'Unknown')}")
        print("-" * 60)
        print(f"🧠 SUMMARY: {report.get('recommendation', {}).get('summary', 'Audit failed to generate summary.')}")
        print("█"*60)
        print(f"\n✅ Professional Audit saved to: {filename}\n")

    except Exception as e:
        print(f"❌ Reporting Error: {e}")
        print("Raw Agent Output:", final_state.get("final_audit"))

if __name__ == "__main__":
    # Get URL from command line or user input
    target_url = sys.argv[1] if len(sys.argv) > 1 else input("🔗 Enter Product URL: ").strip()
    
    if target_url:
        run_audit_system(target_url)
    else:
        print("❌ No URL provided. Exiting.")