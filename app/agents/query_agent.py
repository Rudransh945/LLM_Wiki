import json
import logging
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.services.llm_service import call_llm, call_llm_json
from app.services.vault_service import read_wiki_page, list_wiki_pages
from app.prompts.query_prompts import (
    QUERY_SYSTEM_PROMPT,
    INTENT_CLASSIFY_PROMPT
)

logger = logging.getLogger(__name__)


# ── State ─────────────────────────────────────────────
class QueryState(TypedDict):
    question: str
    intent: Optional[str]
    keywords: Optional[list]
    suggested_pages: Optional[list]
    context_pages: Optional[list]
    context_str: Optional[str]
    answer: Optional[str]
    sources: Optional[list]
    status: Optional[str]


# ── Nodes ─────────────────────────────────────────────

async def classify_node(state: QueryState) -> QueryState:
    """Step 1: Classify intent and find relevant wiki pages."""
    logger.info(f"Query step: classifying intent")
    try:
        raw = await call_llm_json(
            system_prompt=INTENT_CLASSIFY_PROMPT,
            user_prompt=state["question"]
        )
        intent_data = json.loads(raw)
        return {
            **state,
            "intent": intent_data.get("intent", "unknown"),
            "keywords": intent_data.get("keywords", []),
            "suggested_pages": intent_data.get("wiki_pages_likely", []),
            "status": "classified"
        }
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return {
            **state,
            "intent": "unknown",
            "keywords": [],
            "suggested_pages": [],
            "status": "classified"
        }


async def retrieve_node(state: QueryState) -> QueryState:
    """Step 2: Retrieve relevant wiki pages."""
    logger.info("Query step: retrieving wiki pages")
    all_pages = list_wiki_pages()
    context_pages = []
    keywords = state.get("keywords", [])
    suggested_pages = state.get("suggested_pages", [])

    # Priority: suggested pages first
    for page_name in suggested_pages:
        content = read_wiki_page(page_name)
        if content:
            context_pages.append((page_name, content))

    # Keyword fallback: scan all pages
    if len(context_pages) < 3:
        for page_name in all_pages:
            if page_name in suggested_pages:
                continue
            content = read_wiki_page(page_name)
            if content and any(
                kw.lower() in content.lower()
                for kw in keywords
            ):
                context_pages.append((page_name, content))
            if len(context_pages) >= 5:
                break

    return {
        **state,
        "context_pages": context_pages,
        "sources": [name for name, _ in context_pages],
        "status": "retrieved"
    }


async def answer_node(state: QueryState) -> QueryState:
    """Step 3: Generate answer from retrieved context."""
    logger.info("Query step: generating answer")
    context_pages = state.get("context_pages", [])

    if not context_pages:
        return {
            **state,
            "answer": (
                "I don't have any relevant knowledge on this topic yet. "
                "Try ingesting some content about it first."
            ),
            "status": "success"
        }

    context_str = "\n\n---\n\n".join(
        [f"[wiki/{name}]\n{content}"
         for name, content in context_pages]
    )

    answer = await call_llm(
        system_prompt=QUERY_SYSTEM_PROMPT,
        user_prompt=(
            f"KNOWLEDGE CONTEXT:\n{context_str}\n\n"
            f"---\n\nQUESTION: {state['question']}"
        )
    )

    return {
        **state,
        "answer": answer,
        "status": "success"
    }


# ── Build Graph ───────────────────────────────────────

def build_query_graph():
    graph = StateGraph(QueryState)

    graph.add_node("classify_intent", classify_node)
    graph.add_node("retrieve_pages", retrieve_node)
    graph.add_node("generate_answer", answer_node)

    graph.set_entry_point("classify_intent")

    graph.add_edge("classify_intent", "retrieve_pages")
    graph.add_edge("retrieve_pages", "generate_answer")
    graph.add_edge("generate_answer", END)
    return graph.compile()


query_graph = build_query_graph()


# ── Main Entry ────────────────────────────────────────

async def run_query_agent(question: str) -> dict:
    initial_state: QueryState = {
        "question": question,
        "intent": None,
        "keywords": None,
        "suggested_pages": None,
        "context_pages": None,
        "context_str": None,
        "answer": None,
        "sources": None,
        "status": None
    }

    result = await query_graph.ainvoke(initial_state)

    return {
        "answer": result.get("answer"),
        "sources": result.get("sources", []),
        "intent": result.get("intent")
    }