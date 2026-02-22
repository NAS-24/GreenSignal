import os
import sqlite3
import operator
import json
import re
from typing import TypedDict, Annotated, Sequence, List

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

# To these (add 'src.' or '.' depending on your setup):
from src.scraper_module import run_extraction_pipeline
from src.scoring_engine import calculate_trust_score
# ---------------------------------------------------------
# 1. State & Tools
# ---------------------------------------------------------
class AgentState(TypedDict):
    brand_name: str
    claims_found: List[dict]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    final_audit: str

@tool
def query_federated_registry(category: str, brand_name: str) -> str:
    """
    Queries local 'Silos of Truth'. 
    Categories: 'B-CORP', 'GOTS_ORGANIC', 'FSC_PACKAGING', 'VEGAN_PETA'
    """
    print(f"\n[DATABASE] Querying {category} for: {brand_name}...")
    conn = sqlite3.connect('sustainability.db')
    cursor = conn.cursor()
    brand_query = f"%{brand_name.strip()}%"
    
    table_map = {
        'B-CORP': ('registry_bcorp', 'company_name', 'overall_score'),
        'GOTS_ORGANIC': ('registry_gots', 'brand_name', 'license_number'),
        'FSC_PACKAGING': ('registry_fsc', 'brand_name', 'license_code'),
        'VEGAN_PETA': ('registry_vegan', 'brand_name', 'status')
    }

    if category not in table_map:
        return f"Error: Category {category} not supported."

    table, col, val_col = table_map[category]
    try:
        cursor.execute(f"SELECT {val_col} FROM {table} WHERE {col} LIKE ?", (brand_query,))
        res = cursor.fetchone()
        conn.close()
        return f"{category} MATCH FOUND: {res[0]}" if res else f"{category}: NOT_FOUND"
    except Exception as e:
        return f"DB_ERROR: {str(e)}"

@tool
def tavily_search_fallback(query: str):
    """Autonomous search to verify claims or find brand certifications on the live web."""
    print(f"\n[TAVILY] Agent researching: {query}...")
    search = TavilySearchResults(max_results=3)
    return search.invoke(query)

tools = [query_federated_registry, tavily_search_fallback]
model = ChatGroq(model="llama-3.1-8b-instant", temperature=0).bind_tools(tools)

# ---------------------------------------------------------
# 2. Agentic Nodes
# ---------------------------------------------------------
def auditor_node(state: AgentState):
    """The Brain: Orchestrates the audit based on extracted claims or brand name."""
    brand = state["brand_name"]
    
    if not state["messages"]:
        if not state["claims_found"]:
            context = "No claims were extracted from the URL. Perform a general search for GOTS, B-CORP, and PETA status."
        else:
            context = f"Claims to verify: {json.dumps(state['claims_found'])}"

        sys_msg = SystemMessage(content=f"""
        You are a Senior Sustainability Auditor for {brand}.
        {context}
        
        LOGIC:
        1. For each known sustainability category, call `query_federated_registry`.
        2. If a registry returns 'NOT_FOUND', use `tavily_search_fallback` to find proof.
        3. Once all categories are checked, conclude with a final summary.
        """)
        return {"messages": [sys_msg, HumanMessage(content=f"Begin the federated audit for {brand}.")]}
    
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def action_node(state: AgentState):
    """Executes the tool calls selected by the auditor."""
    last_msg = state["messages"][-1]
    tool_outputs = []
    if hasattr(last_msg, "tool_calls"):
        for call in last_msg.tool_calls:
            tool_obj = {"query_federated_registry": query_federated_registry, "tavily_search_fallback": tavily_search_fallback}[call["name"]]
            res = tool_obj.invoke(call["args"])
            tool_outputs.append(ToolMessage(content=str(res), tool_call_id=call["id"]))
    return {"messages": tool_outputs}

def summary_node(state: AgentState):
    """Compiles findings into the professional multi-parameter Audit JSON format."""
    print(f"\n[NODE] Compiling Professional Audit Report...")
    
    prompt = f"""
    Generate a professional sustainability audit for {state['brand_name']} in the following JSON format.
    
    STRICT JSON STRUCTURE:
    {{
      "brandName": "{state['brand_name']}",
      "sustainabilityScore": 0-100,
      "scoreBreakdown": [
        {{"parameter": "Materials & Sourcing", "score": 0-25, "maxScore": 25, "color": "#4CAF50"}},
        {{"parameter": "Certifications", "score": 0-20, "maxScore": 20, "color": "#2196F3"}},
        {{"parameter": "Carbon & Energy", "score": 0-20, "maxScore": 20, "color": "#FF9800"}},
        {{"parameter": "Waste & Packaging", "score": 0-15, "maxScore": 15, "color": "#9C7A4D"}},
        {{"parameter": "Supply Chain Ethics", "score": 0-10, "maxScore": 10, "color": "#E57373"}},
        {{"parameter": "Transparency & Reporting", "score": 0-10, "maxScore": 10, "color": "#7E57C2"}}
      ],
      "claims": [],
      "certifications": [],
      "redFlags": [],
      "recommendation": {{
        "verdict": "Verified/Conditional/Flagged",
        "score": 0-100,
        "reasons": [],
        "summary": ""
      }}
    }}
    
    RULES:
    - Base scores on actual 'MATCH FOUND' results in chat. 
    - Mark claims 'verified' only if a Registry Tool confirmed them.
    - Return ONLY the raw JSON.
    """
    
    response = ChatGroq(model="llama-3.1-8b-instant", temperature=0).invoke(
        state["messages"] + [HumanMessage(content=prompt)]
    )
    
    # Surgical Regex Cleaner to prevent 'Extra Data' errors
    match = re.search(r'\{.*\}', response.content, re.DOTALL)
    clean_json = match.group(0) if match else "{}"
    
    return {"final_audit": clean_json}

# ---------------------------------------------------------
# 3. Graph Logic
# ---------------------------------------------------------
def should_continue(state: AgentState):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "action"
    return "summary"

workflow = StateGraph(AgentState)
workflow.add_node("auditor", auditor_node)
workflow.add_node("action", action_node)
workflow.add_node("summary", summary_node)

workflow.set_entry_point("auditor")
workflow.add_conditional_edges("auditor", should_continue, {"action": "action", "summary": "summary"})
workflow.add_edge("action", "auditor")
workflow.add_edge("summary", END)
app = workflow.compile()

# ---------------------------------------------------------
# 4. Main Execution Pipeline
# ---------------------------------------------------------
if __name__ == "__main__":
    url = input("\n🔗 Paste Product URL: ").strip()
    print("\n[PHASE 1] Multi-Claim Extraction...")
    extracted = run_extraction_pipeline(url)
    
    if "error" in extracted:
        print(f"⚠️ Scraper Alert: {extracted['error']}")
        fallback_brand = url.split("://")[-1].split("/")[0].replace("www.", "").split(".")[0].capitalize()
        print(f"[*] Self-Healing: Triggering General Brand Audit for: {fallback_brand}")
        
        extracted = {
            "brand_name": fallback_brand,
            "claims_found": [] 
        }

    print(f"\n[PHASE 2] Starting Agentic Routing for: {extracted['brand_name']}...")
    result = app.invoke({
        "brand_name": extracted["brand_name"],
        "claims_found": extracted.get("claims_found", []),
        "messages": []
    })
    
    print("\n[PHASE 3] Trust Metric Calculation...")
    # This now receives a clean JSON string with professional parameters
    trust_report = calculate_trust_score(result["final_audit"])
    
    print("\n" + "█"*50)
    print(f"📊 FINAL AUDIT: {extracted['brand_name']}")
    print(f"⭐ TRUST SCORE: {trust_report['final_score']}/100 - {trust_report['level']}")
    print(f"🧠 REASONING: {trust_report['details'].get('recommendation', {}).get('summary', 'N/A')}")
    print("█"*50 + "\n")
    
    # Optional: Save JSON report
    with open(f"audit_{extracted['brand_name'].lower()}.json", "w") as f:
        json.dump(trust_report['details'], f, indent=4)