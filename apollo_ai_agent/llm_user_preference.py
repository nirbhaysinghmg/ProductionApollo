import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv('./../.env', override=True)

# ✅ Initialize LLM function
def initialize_llm(llm_flag="gemini"):
    """Initialize the selected LLM with context-aware capabilities."""
    if llm_flag.lower() == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash-thinking-exp-01-21", temperature=0.1)
    elif llm_flag.lower() == "groq":
        return ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
    else:
        raise ValueError("Invalid LLM flag. Use 'gemini' or 'groq'.")

# ✅ Logging function
def print_with_timestamp(message):
    """Enhanced logging with timestamps."""
    now = datetime.now()
    timestamp = now.strftime("[%Y-%m-%d %H:%M:%S.%f]")[:-3]
    print(f"{timestamp} CONTEXT_TRACKING: {message}")

# ✅ User preferences processing function
def user_preference_with_llm(question, existing_preferences=None, llm_flag="gemini"):
    """Extract and update user property preferences using LLM."""

    # ✅ Initialize LLM
    llm = initialize_llm(llm_flag)

    # ✅ Ensure existing preferences dictionary exists
    existing_preferences = existing_preferences or {}

    # 🔹 LLM Prompt with Explicit Instructions
    llm_prompt_user_preference = """
    You are a **Real Estate Investment Advisor** assisting users in refining their property preferences.  
    Your goal is to **extract, update, and finalize user preferences** for better recommendations.

    ### **User Preferences to Extract & Update:**
    1️⃣ **Budget** (min & max, in Crores only, represented as "Cr")  
    2️⃣ **Location(s)** (city/localities, represented as a single string)  
    3️⃣ **Property Type** (Apartment, Villa, Commercial, etc.)  
    4️⃣ **BHK Preference** (1BHK, 2BHK, etc.)  
    5️⃣ **Investment Goal** (Rental income, Resale profit, End-use)  
    6️⃣ **Construction Status** (Ready-to-move, Under construction)  
    7️⃣ **Holding Period** (in years)  
    8️⃣ **Risk Tolerance** (Stable, High-growth)  

    ### **Your Task:**
    1️⃣ **Extract & update user preferences.**  
    2️⃣ **Merge with existing preferences (if any).**  
    3️⃣ **Identify missing preferences.**  
    4️⃣ **Determine if user has provided sufficient preferences for recommendations.**  
    5️⃣ **If user says 'Proceed' and at least 2 major preferences exist (Budget, Location, Property Type),**  
        → ✅ **Set `"proceed_flag": True`** and generate a `"search_query"`.  
    6️⃣ **If preferences are still too incomplete, set `"proceed_flag": False` and ask for key missing details.**  

    ### **Response Format Example:**
    ```json
    {{
        "preferences": {{
            "budget_min": "2 Cr",
            "budget_max": "3 Cr",
            "preferred_locations": "Gurgaon",
            "property_type": "Apartment",
            "bhk_preference": "3BHK",
            "investment_goal": "Rental income"
        }},
        "missing_preferences": ["construction_status", "holding_period", "risk_tolerance"],
        "proceed_flag": false,
        "next_question": "What is your preferred construction status, holding period, and risk tolerance? Or do you want to proceed?"
    }}
    ```

    ### **Example When User Says 'Proceed'**
    ```json
    {{
        "preferences": {{
            "budget_min": "2 Cr",
            "budget_max": "3 Cr",
            "preferred_locations": "Gurgaon",
            "property_type": "Apartment",
            "bhk_preference": "3BHK",
            "investment_goal": "Rental income",
            "construction_status": "Ready-to-move",
            "holding_period": 5,
            "risk_tolerance": "Stable"
        }},
        "proceed_flag": true,
        "search_query": "Find 3BHK ready-to-move apartments in Gurgaon within 2 Cr to 3 Cr budget for rental income."
    }}
    ```

    ---
    **Current Preferences:**  
    {existing_preferences}

    **User Query:** "{question}"

    **Provide JSON output only. No explanations, no extra text.**
    """

    # Convert existing preferences to JSON string for LLM context
    existing_preferences_json = json.dumps(existing_preferences, indent=4)

    # ✅ Format the prompt correctly with JSON data
    prompt = llm_prompt_user_preference.format(existing_preferences=existing_preferences_json, question=question)

    try:
        print_with_timestamp(f"Processing with existing preferences: {existing_preferences_json}")
        response = llm.invoke(prompt)
        response_content = response.content.strip() if response and response.content else ""

        # ✅ PRINT RAW LLM RESPONSE FOR DEBUGGING
        print_with_timestamp(f"🔍 RAW LLM RESPONSE:\n{response_content}")

        # ✅ Extract valid JSON only
        json_start = response_content.find("{")
        json_end = response_content.rfind("}") + 1
        if json_start == -1 or json_end == -1:
            print_with_timestamp("⚠️ ERROR: LLM response did not return valid JSON. Using fallback.")
            return {
                "preferences": existing_preferences,
                "proceed_flag": False,
                "search_query": None,
                "missing_preferences": [],
                "next_question": "To proceed, please provide at least two preferences (e.g., location, budget, property type)."
            }

        json_response = response_content[json_start:json_end]

        # ✅ Validate JSON format
        try:
            response_json = json.loads(json_response)
        except json.JSONDecodeError:
            print_with_timestamp("⚠️ ERROR: JSON decoding failed. Using fallback.")
            return {
                "preferences": existing_preferences,
                "proceed_flag": False,
                "search_query": None,
                "missing_preferences": [],
                "next_question": "To proceed, please provide at least two preferences (e.g., location, budget, property type)."
            }

        # ✅ Extract flag and search query
        proceed_flag = response_json.get("proceed_flag", False)
        search_query = response_json.get("search_query", None)

        # ✅ Merge new preferences with existing ones
        updated_preferences = existing_preferences.copy()
        updated_preferences.update(response_json["preferences"])

        # ✅ If proceed_flag is True but no search query is provided, construct a fallback query
        if proceed_flag and not search_query:
            search_query = f"Find {updated_preferences.get('bhk_preference', 'any')} {updated_preferences.get('property_type', 'properties')} in {updated_preferences.get('preferred_locations', '')} within {updated_preferences.get('budget_min', '')} to {updated_preferences.get('budget_max', '')} budget."

        # ✅ Prepare response
        final_response = {
            "preferences": updated_preferences,
            "proceed_flag": proceed_flag,
            "search_query": search_query,
            "missing_preferences": response_json.get("missing_preferences", []),
            "next_question": response_json.get("next_question", None) if not proceed_flag else None
        }

        print_with_timestamp(f"✅ Updated Preferences: {json.dumps(updated_preferences, indent=4)}")
        return final_response

    except Exception as e:
        print_with_timestamp(f"❌ Preference processing error: {str(e)}")
        return {
            "preferences": existing_preferences,
            "proceed_flag": False,
            "search_query": None,
            "missing_preferences": [],
            "next_question": "To proceed, please provide at least two preferences (e.g., location, budget, property type)."
        }


# 🔹 Local Testing Block
if __name__ == "__main__":
    # Example contextual conversation
    test_context = {}
    test_queries = [
        "Looking for guidance to invest in property.",
        "best apartments in Gurgaon under ₹5 crore"
    ]
    
    for query in test_queries:
        print_with_timestamp(f"🔍 Original Query: {query}")
        response = user_preference_with_llm(query, test_context, "gemini")
        print_with_timestamp(f"✅ JSON Output: {json.dumps(response, indent=4)}\n")
