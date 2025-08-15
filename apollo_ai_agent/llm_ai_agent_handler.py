# llm_ai_agent_handler.py

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
import llm_ai_agent_prompts  # our prompt library

load_dotenv('./../.env', override=True)

# Optional safety settings (if you plug them into your LLM setup)
safety_settings = {
    "HARASSMENT": "BLOCK_NONE",
    "HATE_SPEECH": "BLOCK_NONE",
    "SEXUAL": "BLOCK_NONE",
    "DANGEROUS": "BLOCK_NONE",
}


def create_chain(
    llm_flag: str = "gemini",
    query_category: str = None,
    system_prompt: str = None,
    human_prompt: str = None,
    mobile: bool = False
):
    """
    Create a LangChain ChatPromptTemplate → LLM → StrOutputParser chain.

    Args:
        llm_flag:        "gemini" or "groq"
        query_category:  for logging/tracing (optional)
        system_prompt:   the system-role instructions (string)
        human_prompt:    the human-role template (string)
        mobile:          if True, may choose a mobile‐optimized LLM or prompt

    Returns:
        A chain you can call `.stream({...})` on.
    """
    # 1️⃣ Instantiate the chosen LLM
    if llm_flag == "groq":
        llm = ChatGroq(temperature=0, model_name="deepseek-r1-distill-llama-70b")
    elif llm_flag == "gemini":
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-04-17",
            api_key=os.getenv("GOOGLE_API_KEY"),
            disable_streaming=False,
            temperature=0.1
        )
    else:
        raise ValueError("Invalid LLM flag. Use 'gemini' or 'groq'.")

    # (Optional) print for telemetry
    print(f"[LLM Chain] category={query_category} mobile={mobile}")

    # 2️⃣ Select or fall back to default prompts
    sys_text = system_prompt or llm_ai_agent_prompts.default_agent_prompt
    hum_text = human_prompt  or llm_ai_agent_prompts.default_agent_human_prompt

    # 3️⃣ Build prompt templates
    system = SystemMessagePromptTemplate.from_template(sys_text)
    human  = HumanMessagePromptTemplate.from_template(hum_text)

    # 4️⃣ Combine into a chat prompt and attach the LLM + parser
    chat_prompt = ChatPromptTemplate(messages=[system, human])
    qna_chain  = chat_prompt | llm | StrOutputParser()

    return qna_chain
