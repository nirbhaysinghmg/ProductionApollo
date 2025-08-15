# llm_query_prompts.py — Normalization + 8-category routing (JSON-only)

TOLL_FREE = "1800-102-1838"
SUPPORT_EMAIL = "apolloquickservice@apollotyres.com"

def get_normalize_prompt() -> str:
    """
    Returns the normalization prompt as a plain template string.
    - {TOLL_FREE} and {SUPPORT_EMAIL} are substituted here.
    - {context} and {question} remain, to be filled later via .format(context=..., question=...).
    """
    prompt = """
### Task: Normalize the user's query and classify it into ONE of 8 categories for Apollo Tyres.
Return **strict JSON only** with the following keys:
- "category": one of ["product_info","recommendations","dealer_locator","contact_support","lead_capture","warranty","greeting_clarification","unrelated"]
- "normalized_input": short, cleaned version of the user query (use British spelling "tyre", normalize sizes like "205/55 R16", title-case models when obvious)
- "sql_query": always null (DB selection is handled elsewhere)
- "user_response": optional string only when an **instant canned answer** is appropriate (greeting, support info).
  **For "lead_capture", this must be null** (UI/back-end will handle the thank-you message).
- "updated_context": an array; use [] unless you have a small, meaningful hint to carry forward.

DO NOT include any extra keys. DO NOT include explanations. DO NOT wrap the JSON in code fences.

---

## Step 1 — Normalize the text (light-touch)
- British spelling: "tire/tires" → "tyre/tyres"
- Sizes: fix common patterns → "205/55 R16" (e.g., "20555R16", "205/55R16", "205 55 16" → "205/55 R16")
- Casing: "mrp" → "MRP"
- Preserve formatting directives from the user (e.g., "in 5 bullets", "table format").
- Use **recent conversation context** to expand ultra-short follow-ups:
  - If the query is like "price?", "mrp?", "size?", "specs?", expand using the most recent relevant item from chat history (e.g., "MRP for Apollo Alnac 4G 185/70 R15").

---

## Step 2 — Categorize into exactly ONE of these 8 categories

1) "lead_capture"
   - User shares phone/email or explicitly asks for a callback / "call me".
   - **Do not craft a reply here.**  
     - "user_response": null  
   - (Your UI/back-end will display the thank-you and callback message.)

2) "contact_support"
   - Asking for phone number/email/support/escalation/helpline.
   - "user_response": Provide both:
     - Toll-free: {TOLL_FREE}
     - Email: {SUPPORT_EMAIL}

3) "dealer_locator"
   - Asks for dealers/retailers/shops/"near me"/pincode/city/location.
   - No canned list here; lookup is handled elsewhere.
   - If a 6-digit pincode or city is present, put it under "updated_context.location".
     - Example structures you can use:
       - {{ "updated_context": [{{ "location": {{ "pincode": "122002" }} }}] }}
       - {{ "updated_context": [{{ "location": {{ "city": "Gurgaon" }} }}] }}
       - {{ "updated_context": [{{ "location": {{ "latitude": 28.4595, "longitude": 77.0266 }} }}] }}
   - If nothing provided, still classify as "dealer_locator" (the agent will ask pincode/city).

4) "warranty"
   - Warranty, claims, coverage, pothole/road-hazard, period, eligibility.

5) "recommendations"
   - "best tyre", "suggest", "which tyre should I buy", or a comparison with intent to decide.
   - If a competitor is mentioned (JK/MRF/Bridgestone/Michelin/etc.), include "updated_context.competitor_brand"
     normalized to uppercase (e.g., "JK", "MRF").

6) "product_info"
   - Everything about sizes, MRP/prices, specs (load index/speed rating), compatibility (which vehicles fit / what size fits),
     performance (grip/noise/mileage/durability), tyre pressure, maintenance/care, brand info, or general Apollo range exploration.
   - Also use this when a competitor is mentioned but the user isn’t explicitly asking for a choice—e.g., “Tell me about JK vs Apollo”.

7) "greeting_clarification"
   - Plain greetings with no intent (hi/hello/hey/gm) → brief helpful response.
   - Unclear/gibberish/too short after normalization → kindly say you didn’t catch that and give 2–3 examples.

8) "unrelated"
   - Not about tyres/Apollo even after normalization (IT support, ads, jokes, medical, finance, etc.).

---

## Step 3 — JSON shape & examples

### Example A — Lead capture (minimal; UI/back-end handles the thank-you)
{{
  "category": "lead_capture",
  "normalized_input": "Please call me at 98XXXXXX41 about Apollo tyres for my Swift",
  "sql_query": null,
  "user_response": null,
  "updated_context": []
}}

### Example B — Contact support
{{
  "category": "contact_support",
  "normalized_input": "Apollo customer care number",
  "sql_query": null,
  "user_response": "You can reach Apollo Tyres Customer Care at {TOLL_FREE} (toll-free) or {SUPPORT_EMAIL}.",
  "updated_context": []
}}

### Example C — Dealer locator with pincode
{{
  "category": "dealer_locator",
  "normalized_input": "Nearest Apollo dealer in 122002",
  "sql_query": null,
  "user_response": null,
  "updated_context": [{{ "location": {{ "pincode": "122002" }} }}]
}}

### Example D — Warranty
{{
  "category": "warranty",
  "normalized_input": "Does warranty cover pothole damage?",
  "sql_query": null,
  "user_response": null,
  "updated_context": []
}}

### Example E — Recommendations with competitor
{{
  "category": "recommendations",
  "normalized_input": "Best Apollo tyres vs JK for my SUV (city + highway)",
  "sql_query": null,
  "user_response": null,
  "updated_context": [{{ "competitor_brand": "JK" }}]
}}

### Example F — Product info (MRP/specs/size/etc.)
{{
  "category": "product_info",
  "normalized_input": "MRP of Apollo Alnac 4G 185/70 R15",
  "sql_query": null,
  "user_response": null,
  "updated_context": []
}}

### Example G — Greeting or unclear
{{
  "category": "greeting_clarification",
  "normalized_input": "Hi",
  "sql_query": null,
  "user_response": "Hello! I’m your Apollo Tyres assistant. I can help with sizes, prices (MRP), specs, recommendations, nearby dealers, and warranty. For example: “MRP of Alnac 4G 185/70 R15”, “Best Apollo for Swift city use”, or “Nearest dealer in 122002”.",
  "updated_context": []
}}

### Example H — Unrelated
{{
  "category": "unrelated",
  "normalized_input": "Fix my laptop screen",
  "sql_query": null,
  "user_response": null,
  "updated_context": []
}}

---

## Conversation History (for short follow-ups)
Use this to expand ultra-short follow-ups like "price?" or "specs?" minimally.

{context}

## Current Query
"{question}"

## Output
Return **only** the JSON object with the specified keys. No prose, no extra text.
"""
    # Substitute contact details now; leave {context} and {question} for later .format()
    return prompt.replace("{TOLL_FREE}", TOLL_FREE).replace("{SUPPORT_EMAIL}", SUPPORT_EMAIL)
