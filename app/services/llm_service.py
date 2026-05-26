import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    max_tokens=MAX_TOKENS,
    temperature=0.3
)

llm_json = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    max_tokens=MAX_TOKENS,
    temperature=0.1
)


async def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Basic LLM call — bypasses template parsing completely."""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    response = await llm.ainvoke(messages)
    return response.content.strip()


async def call_llm_json(system_prompt: str, user_prompt: str) -> str:
    """LLM call that forces JSON output."""
    system_with_json = (
        system_prompt +
        "\n\nIMPORTANT: Respond ONLY with valid JSON. "
        "No explanation, no markdown, no code fences."
    )
    messages = [
        SystemMessage(content=system_with_json),
        HumanMessage(content=user_prompt)
    ]
    response = await llm_json.ainvoke(messages)
    return response.content.strip()