import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))

# Single LLM instance reused across entire app
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    max_tokens=MAX_TOKENS,
    temperature=0.3
)

# LLM with lower temperature for JSON responses
llm_json = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    max_tokens=MAX_TOKENS,
    temperature=0.1
)


async def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Basic LLM call using LangChain RunnableSequence."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt)
    ])
    chain = prompt | llm | StrOutputParser()
    response = await chain.ainvoke({})
    return response.strip()


async def call_llm_json(system_prompt: str, user_prompt: str) -> str:
    """LLM call that forces JSON output."""
    system_with_json = (
        system_prompt +
        "\n\nIMPORTANT: Respond ONLY with valid JSON. "
        "No explanation, no markdown, no code fences."
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_with_json),
        ("human", user_prompt)
    ])
    chain = prompt | llm_json | StrOutputParser()
    response = await chain.ainvoke({})
    return response.strip()