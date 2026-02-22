import os
import requests
from bs4 import BeautifulSoup
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# Initialize LLM for claim classification
classifier_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)

def repair_truncated_json(text: str) -> list:
    """Surgically repairs truncated or malformed JSON output from the LLM."""
    # Clean markdown backticks if the LLM ignored instructions
    text = re.sub(r'```json\s*|```', '', text).strip()
    
    try:
        # 1. Look for the most complete JSON-like structure available
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        # 2. Heuristic Repair for abrupt truncation
        if text.startswith('['):
            repaired = text
            if repaired.count('"') % 2 != 0: repaired += '"'
            if not repaired.endswith('}'): repaired += '}'
            if not repaired.endswith(']'): repaired += ']'
            match = re.search(r'\[.*\]', repaired, re.DOTALL)
            if match: return json.loads(match.group(0))
    except Exception:
        return []
    return []

def extract_text_with_surgeon(html_content: str, url: str):
    """Surgically extracts product text while ignoring UI elements."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Improved Brand Extraction
    meta_brand = soup.find("meta", property="og:site_name")
    brand_name = meta_brand["content"] if meta_brand else url.split("//")[-1].split(".")[0].replace("www.", "").capitalize()

    for element in soup(["script", "style", "noscript", "svg", "form", "nav", "header", "footer", "button", "aside"]):
        element.decompose()

    claims_text = ""
    target_classes = ["product", "description", "sustainability", "materials", "details", "content", "about", "philosophy"]
    for class_name in target_classes:
        elements = soup.find_all(class_=lambda x: x and class_name in x.lower())
        for el in elements:
            claims_text += el.get_text(separator=" ", strip=True) + " "

    if len(claims_text.strip()) < 100:
        paragraphs = soup.find_all("p")
        claims_text = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20][:25])

    return brand_name, ' '.join(claims_text.split())

def classify_multi_claims(brand_name: str, extracted_text: str):
    """Agentic extraction that categorizes claims for specific DB routing."""
    if not extracted_text:
        return []

    print(f"[*] Identifying claim categories for {brand_name}...")
    
    sys_prompt = SystemMessage(content="""
    You are a Senior Sustainability Auditor. Analyze the product text and extract ALL specific sustainability claims.
    
    Categories:
    - 'B-CORP': Official B-Lab certification claims.
    - 'GOTS_ORGANIC': GOTS, Organic, or sustainable cotton/textile claims.
    - 'FSC_PACKAGING': FSC, recycled paper, or wood-based claims.
    - 'VEGAN_PETA': Vegan, PETA-approved, or cruelty-free claims.
    
    Format: ONLY return a raw JSON list. 
    Example: [{"category": "GOTS_ORGANIC", "claim_snippet": "GOTS certified organic cotton"}]
    """)
    
    user_prompt = HumanMessage(content=f"Brand: {brand_name}\nText: {extracted_text[:4000]}")
    
    try:
        response = classifier_llm.invoke([sys_prompt, user_prompt])
        # Use repair logic to prevent pipeline crashes from malformed JSON
        return repair_truncated_json(response.content.strip())
    except Exception as e:
        print(f"Extraction Error: {e}")
        return []

def scrape_product_url(target_url: str):
    """High-resilience scraping with ScraperAPI."""
    api_key = os.getenv("SCRAPER_API_KEY")
    if not api_key: return {"error": "Missing SCRAPER_API_KEY"}

    print(f"\n🚀 Scraping Target: {target_url}")
    
    payload = {
        'api_key': api_key, 
        'url': target_url, 
        'render': 'true',
        'premium': 'true', 
        'country_code': 'us' 
    }
    
    try:
        response = requests.get('http://api.scraperapi.com', params=payload, timeout=90)
        if response.status_code == 200:
            if not response.text.strip():
                return {"error": "Empty HTML received"}
            return extract_text_with_surgeon(response.text, target_url)
        return {"error": f"ScraperAPI Status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def run_extraction_pipeline(url: str):
    """Safely runs the pipeline and handles internal errors to prevent crashes."""
    scraped_result = scrape_product_url(url)
    
    # Verify the structure to prevent "KeyError" or "Unpacking" errors in the router
    if isinstance(scraped_result, dict) and "error" in scraped_result:
        scraped_result["brand_name"] = url.split("//")[-1].split(".")[0].replace("www.", "").capitalize()
        scraped_result["claims_found"] = []
        return scraped_result
    
    brand_name, extracted_text = scraped_result
    
    if not extracted_text:
        return {"error": "No text found", "brand_name": brand_name, "claims_found": []}
    
    # Categorize findings into specific Silos of Truth
    all_claims = classify_multi_claims(brand_name, extracted_text) 
    
    return {
        "brand_name": brand_name,
        "claims_found": all_claims,
        "raw_text_snapshot": extracted_text[:500] 
    }