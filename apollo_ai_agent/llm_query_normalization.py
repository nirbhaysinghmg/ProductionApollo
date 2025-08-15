# llm_query_normalization.py — light normalization + 8-category classification
# Returns a consistent dict: {category, normalized_input, sql_query, user_response, updated_context}

import os
import json
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from llm_query_prompts import get_normalize_prompt
from logger import logger, error_logger, log_query

# Load environment (expects GOOGLE_API_KEY for Gemini)
load_dotenv("./../.env", override=True)


# ---------- Utilities ----------

def _flatten_context(conversation_context: Any, max_items: int = 10) -> str:
    """
    Convert the mixed context payload from chat_handler into a compact, readable transcript-like string.
    Expected shape:
      {
        "recent_history": [{"role": "user"/"assistant", "content": "..."} ...],
        "prior_context": [...]
      }
    Only the recent_history is usually needed to expand short follow-ups.
    """
    if not conversation_context or not isinstance(conversation_context, dict):
        return ""

    recent = conversation_context.get("recent_history") or []
    lines: List[str] = []
    for item in recent[-max_items:]:
        role = (item.get("role") or "").strip().lower()
        content = (item.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            lines.append(f"User: {content}")
        elif role == "assistant":
            lines.append(f"Assistant: {content}")
    return "\n".join(lines)


def _first_json_object(text: str) -> Optional[str]:
    """
    Extract the first valid-looking JSON object substring from the model output.
    Handles occasional extra prose or formatting.
    """
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    blob = text[start : end + 1].strip()
    # Quick sanity trim for trailing code fences/backticks if any slipped in.
    blob = re.sub(r"```+", "", blob)
    return blob


def _default_result() -> Dict[str, Any]:
    return {
        "category": "greeting_clarification",
        "normalized_input": "",
        "sql_query": None,
        "user_response": (
            "Hello! I’m your Apollo Tyres assistant. "
            "I can help with sizes, prices (MRP), specs, recommendations, nearby dealers, and warranty."
        ),
        "updated_context": [],
    }


def _get_llm(model_name: str = "gemini-2.0-flash", temperature: float = 0.1) -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set in the environment.")
    return ChatGoogleGenerativeAI(
        model=model_name,
        api_key=api_key,
        disable_streaming=False,
        temperature=temperature,
    )


# ---------- Public API ----------

def normalize_query_with_llm(
    user_input: str,
    conversation_context: Any = None,
    llm_flag: str = "gemini",
) -> Dict[str, Any]:
    """
    Normalize + categorize the user's query into one of 8 categories.
    Returns a dict with keys:
      - category (str)
      - normalized_input (str)
      - sql_query (None)
      - user_response (str|None)
      - updated_context (list)
    """
    try:
        logger.info("Starting normalization for user input: %s", user_input)
        llm = _get_llm(model_name="gemini-2.0-flash", temperature=0.1)
        normalize_prompt = get_normalize_prompt()

        # Flatten recent conversation for short follow-up expansion
        context_text = _flatten_context(conversation_context, max_items=10)

        # Fix: Use .format() only if prompt contains named placeholders, and ensure all literal braces in prompt are doubled
        try:
            prompt_text = normalize_prompt.format(context=context_text, question=user_input or "")
        except Exception as e:
            error_logger.error("Prompt formatting error: %s", str(e))
            # Fallback: Use prompt as-is with context/question replaced manually
            prompt_text = normalize_prompt.replace("{context}", context_text).replace("{question}", user_input or "")

        # Invoke the model; we expect strict JSON in the response
        resp = llm.invoke(prompt_text)
        output_text = (getattr(resp, "content", None) or "").strip()

        # Extract JSON object and parse
        json_blob = _first_json_object(output_text)
        if not json_blob:
            logger.warning("Failed to extract JSON object from model output.")
            return _default_result()

        data = json.loads(json_blob)

        # Enforce required keys + expected shapes
        category = (data.get("category") or "").strip().lower()
        normalized_input = data.get("normalized_input") or (user_input or "")
        sql_query = None  # always None by design
        user_response = data.get("user_response") if data.get("user_response") else None
        updated_context = data.get("updated_context") if isinstance(data.get("updated_context"), list) else []

        # Lead capture policy: classification only (no canned reply)
        if category == "lead_capture":
            user_response = None

        # Safety fallback if category missing
        if not category:
            category = "greeting_clarification"

        result = {
            "category": category,
            "normalized_input": normalized_input,
            "sql_query": sql_query,
            "user_response": user_response,
            "updated_context": updated_context,
        }

        logger.debug("Normalization result: %s", result)
        return result

    except Exception as e:
        error_logger.error("Normalization error: %s", str(e))
        # Any failure → safe default (keeps UX moving)
        return _default_result()
