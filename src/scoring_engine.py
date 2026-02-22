import json


def _extract_first_json(text: str) -> str:
    """Return the first balanced JSON object or array from text.
    Scans for first '{' or '[' and returns substring up to matching closing brace/bracket.
    Raises ValueError if no balanced JSON found.
    """
    if not text:
        raise ValueError("Empty AI output")

    # find start
    start_idx = None
    for i, ch in enumerate(text):
        if ch in '{[':
            start_idx = i
            start_ch = ch
            break
    if start_idx is None:
        raise ValueError("No JSON object/array found in AI output")

    # select matching end
    stack = []
    pairs = {'{': '}', '[': ']'}
    for i in range(start_idx, len(text)):
        ch = text[i]
        if ch == start_ch:
            stack.append(ch)
        elif ch in pairs.values():
            if not stack:
                # unmatched closing
                raise ValueError("Unbalanced JSON in AI output")
            # pop corresponding opener
            stack.pop()
            if not stack:
                return text[start_idx:i+1]

    raise ValueError("Unterminated JSON in AI output")


def calculate_trust_score(ai_json_output: str) -> dict:
    """Step 5: Trust Metric Calculation.
    Hardened to extract the first balanced JSON payload and ignore trailing chatter.
    """
    try:
        clean_json = _extract_first_json(ai_json_output)
        data = json.loads(clean_json)
        
        # 2. Type Safety: Handle cases where an array [item] is returned instead of {item}
        if isinstance(data, list):
            data = data[0] if len(data) > 0 else {}
        
        # 3. Standard Value Extraction
        confidence = float(data.get("confidence", 0.9))
        category = str(data.get("category", "vague")).lower()
        verdict = str(data.get("verdict", "UNCERTAIN")).upper()
        reasoning = str(data.get("reasoning", "")).lower()
        
        # 4. DYNAMIC BASE SCORE
        if verdict == "VERIFIED":
            base_score = 80
        elif verdict == "FLAGGED":
            base_score = 20
        else:
            base_score = 50
            
        # 5. CATEGORY WEIGHTS
        weights = {
            "brand_level": 10,
            "product_material": 10,
            "industry_specific": 15,
            "vague": -20
        }
        category_weight = weights.get(category, 5)
        
        # 6. CALCULATE ADJUSTMENT & BONUSES
        adjustment = (category_weight * confidence) if verdict == "VERIFIED" else -(abs(category_weight) * confidence)
        
        bonus = 0
        if verdict == "VERIFIED":
            # Registry 'Silo of Truth' Bonus
            registries = ["b-corp", "gots", "fsc", "peta", "match found"]
            for reg in registries:
                if reg in reasoning:
                    bonus += 3

        final_score = max(0, min(100, base_score + adjustment + bonus))
        
        # 7. DEFINE TRUST LEVELS
        if final_score >= 85:
            level = "Certified Excellence 🏆"
        elif final_score >= 70:
            level = "High Trust ✅"
        elif final_score >= 45:
            level = "Medium Trust ⚠️"
        else:
            level = "Greenwashing Detected 🚨"
            
        return {
            "final_score": round(final_score, 1),
            "level": level,
            "details": data
        }
        
    except Exception as e:
        print(f"Scoring Error: {e}")
        return {
            "final_score": 0, 
            "level": "Error", 
            "details": {"reasoning": f"Failed to parse AI output: {str(e)}"}
        }