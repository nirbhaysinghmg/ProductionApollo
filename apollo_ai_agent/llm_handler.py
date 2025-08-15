# llm_handler.py — category-only prompt selection with user_location + streaming

from typing import Optional

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

from logger import logger, error_logger, log_query
import time

from llm_prompts import get_prompt_content
from llm_prompts_mobile import get_prompt_mobile_content

# Load environment variables (expects GOOGLE_API_KEY if using Gemini)
load_dotenv("./../.env", override=True)


def _get_llm(llm_flag: str = "gemini"):
    """
    Return an LLM instance suitable for streaming.
    """
    flag = (llm_flag or "gemini").lower()
    if flag == "groq":
        # Deterministic, support-style answers
        return ChatGroq(temperature=0.1, model_name="deepseek-r1-distill-llama-70b")
    # Default: fast Gemini for low latency; keep streaming enabled
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        disable_streaming=False,
        temperature=0.1,
    )


def create_chain(
    llm_flag: str = "gemini",
    query_category: Optional[str] = None,
    mobile: bool = False,
):
    """
    Build a streaming chain for the Apollo Tyres assistant.

    Args:
        llm_flag: "gemini" (default) or "groq"
        query_category: one of the routed categories; defaults to "contextual_query"
        mobile: whether to use the mobile-optimized prompt set
    """
    # 1) Select LLM
    llm = _get_llm(llm_flag)
    logger.info(f"LLM selected: {llm_flag}")

    # 2) Choose system prompt by category (no subcategories)
    category = (query_category or "contextual_query").strip().lower()
    system_prompt = (
        get_prompt_mobile_content(category) if mobile else get_prompt_content(category)
    )
    logger.info(f"System prompt selected for category '{category}': {system_prompt[:120]}...")

    system = SystemMessagePromptTemplate.from_template(system_prompt)

    # 3) Human template — keep it generic; your category-specific system prompt does the heavy lifting
    human_template = """
You are the Apollo Tyres AI Agent. Answer with brand-specific, helpful content and honor any formatting hints from the user.

### Inputs
- Previous Conversation:
{chat_history}

### Context
{context}

### Question
{question}

### Answer
"""

    human = HumanMessagePromptTemplate.from_template(human_template)

    # 4) Build chat prompt and chain; StrOutputParser() allows incremental streaming in chat_handler
    chat_prompt = ChatPromptTemplate(messages=[system, human])
    chain = chat_prompt | llm | StrOutputParser()
    logger.info(f"Chain created for category '{category}' and llm_flag '{llm_flag}'.")
    return chain

# Example usage:
# logger.info("Sending prompt to LLM: %s", prompt)
# error_logger.error("LLM error: %s", str(e))
# log_query(user_id, user_input, normalized_input, category, context, full_response, response_time, error)

# Utility for streaming and logging (to be called from chat_handler)
def run_chain_with_logging(chain, inputs, user_id, normalized_input, category, context):
    start_time = time.time()
    full_response = ""
    try:
        logger.info(f"Running LLM chain for user {user_id}, category: {category}, inputs: {inputs}")
        for piece in chain.stream(inputs):
            full_response += str(piece)
        response_time = time.time() - start_time
        log_query(
            user_id,
            inputs.get("question", ""),
            normalized_input,
            category,
            context,
            full_response,
            response_time
        )
        logger.info(f"LLM chain completed for user {user_id}, category: {category}, response: {full_response[:200]}")
        return full_response
    except Exception as e:
        response_time = time.time() - start_time
        log_query(
            user_id,
            inputs.get("question", ""),
            normalized_input,
            category,
            context,
            full_response,
            response_time,
            error=str(e),
            exc_info=True
        )
        error_logger.error(f"LLM chain error for user {user_id}, category: {category}: {e}", exc_info=True)
        return None
