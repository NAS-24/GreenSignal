from src.scoring_engine import calculate_trust_score

cases = [
    # 1. JSON with trailing text
    '{"confidence":0.8,"category":"brand_level","verdict":"VERIFIED","reasoning":"b-corp found"} some trailing chatter',
    # 2. Two JSON objects concatenated
    '{"confidence":0.7,"category":"product_material","verdict":"FLAGGED","reasoning":""}{"confidence":0.9}',
    # 3. JSON wrapped in text with preamble
    'Response:\nHere is the result:\n{"confidence":0.95,"category":"brand_level","verdict":"VERIFIED","reasoning":"match found in gots"}\nThanks',
    # 4. Array JSON
    '[{"confidence":0.6,"category":"industry_specific","verdict":"UNCERTAIN","reasoning":"no matches"}]\nMore text'
]

for i, case in enumerate(cases, 1):
    print(f"--- Case {i} ---")
    res = calculate_trust_score(case)
    print(res)

print("Done")
