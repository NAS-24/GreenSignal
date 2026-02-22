import json

def check_sandbox_database(brand_name: str) -> str:
    """
    Simulates enterprise API access to proprietary certification databases.
    Categorized exactly as defined in the system architecture.
    """
    
    # ---------------------------------------------------------
    # THE MOCK DATABASE (Your Hackathon Demo Data)
    # ---------------------------------------------------------
    sandbox_db = {
        "Patagonia": {
            "brand_level": ["B Corp Directory (B Lab)", "Climate Neutral Certified"],
            "product_material": ["Cradle to Cradle (C2C)", "FSC Certificate"],
            "industry_specific": ["GOTS Database", "Fairtrade International"]
        },
        "Lush Cosmetics": {
            "brand_level": [],
            "product_material": ["Cradle to Cradle (C2C)"],
            "industry_specific": ["Leaping Bunny / PETA", "EWG Verified"]
        },
        "FastFashionCo": {
            # Greenwashing brand - no real certifications in the database
            "brand_level": [],
            "product_material": [],
            "industry_specific": []
        }
    }
    
    # ---------------------------------------------------------
    # THE LOOKUP LOGIC
    # ---------------------------------------------------------
    print(f"\n[SANDBOX] Searching internal registries for: {brand_name}...")
    
    # Standardize the input to handle case-sensitivity (e.g., "patagonia" vs "Patagonia")
    brand_key = next((key for key in sandbox_db.keys() if key.lower() == brand_name.lower()), None)
    
    if brand_key:
        record = sandbox_db[brand_key]
        # Check if they actually have any certifications across all categories
        total_certs = sum(len(certs) for certs in record.values())
        
        if total_certs > 0:
            print(f"[SANDBOX] SUCCESS: Found {total_certs} certifications for {brand_key}.")
            return json.dumps({"status": "FOUND", "data": record})
        else:
            print(f"[SANDBOX] ALERT: Brand {brand_key} exists but has NO valid certifications.")
            return json.dumps({"status": "NO_CERTIFICATIONS_FOUND", "data": {}})
            
    print(f"[SANDBOX] MISS: {brand_name} not found in internal database.")
    return json.dumps({"status": "NOT_FOUND", "message": "Brand not in database. Fallback to Web Search required."})

# ---------------------------------------------------------
# Mock Web Search Tool (For testing without hitting API limits)
# ---------------------------------------------------------
def execute_web_search(query: str) -> str:
    """Fallback tool when Sandbox returns NOT_FOUND."""
    print(f"[WEB SEARCH] Executing search for: '{query}'")
    # In production, this connects to Tavily or DuckDuckGo.
    return "Search results indicate no credible third-party certifications. Only marketing claims found."