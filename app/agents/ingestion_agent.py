import json
import logging
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.services.llm_service import call_llm, call_llm_json
from app.services.vault_service import (
    read_wiki_page, write_wiki_page, append_log
)
from app.prompts.ingestion_prompts import (
    EXTRACT_CONCEPTS_PROMPT,
    MERGE_WIKI_PROMPT,
    CONTRADICTION_CHECK_PROMPT
)

logger = logging.getLogger(__name__)


# ── State ─────────────────────────────────────────────
class IngestionState(TypedDict):
    raw_content: str
    source_type: str
    source_ref: str
    extraction: Optional[dict]
    wiki_page_name: Optional[str]
    new_wiki_content: Optional[str]
    existing_content: Optional[str]
    contradiction: Optional[dict]
    final_content: Optional[str]
    action: Optional[str]
    status: Optional[str]
    error: Optional[str]


# ── Nodes ─────────────────────────────────────────────
async def extract_node(state: IngestionState) -> IngestionState:
    """Step 1: Extract concepts from raw content using LLM."""
    logger.info("Ingestion step: extracting concepts")
    try:
        # Truncate content to avoid token limit issues
        content = state['raw_content'][:6000]
        raw = await call_llm_json(
            system_prompt=EXTRACT_CONCEPTS_PROMPT,
            user_prompt=(
                f"Source type: {state['source_type']}\n"
                f"Source reference: {state['source_ref']}\n\n"
                f"---\n\n{content}"
            )
        )
        extraction = json.loads(raw)
        return {
            **state,
            "extraction": extraction,
            "wiki_page_name": extraction.get("wiki_page_name", "untitled"),
            "new_wiki_content": extraction.get("wiki_content", ""),
            "status": "extracting"
        }
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {**state, "status": "failed", "error": str(e)}


async def check_wiki_node(state: IngestionState) -> IngestionState:
    """Step 2: Check if wiki page already exists."""
    logger.info(f"Ingestion step: checking wiki for {state['wiki_page_name']}")
    existing = read_wiki_page(state["wiki_page_name"])
    return {
        **state,
        "existing_content": existing,
        "status": "checking"
    }


async def contradiction_node(state: IngestionState) -> IngestionState:
    """Step 3: Check for contradictions if page exists."""
    logger.info("Ingestion step: checking contradictions")
    if not state["existing_content"]:
        return {**state, "contradiction": None, "status": "no_conflict"}
    try:
        raw = await call_llm_json(
            system_prompt=CONTRADICTION_CHECK_PROMPT,
            user_prompt=(
                f"EXISTING WIKI:\n{state['existing_content']}\n\n"
                f"NEW INFORMATION:\n{state['new_wiki_content']}"
            )
        )
        contradiction = json.loads(raw)
        return {**state, "contradiction": contradiction}
    except Exception:
        return {
            **state,
            "contradiction": {
                "has_contradiction": False,
                "recommendation": "merge_anyway"
            }
        }


async def merge_node(state: IngestionState) -> IngestionState:
    """Step 4a: Merge new content into existing wiki page."""
    logger.info(f"Ingestion step: merging into {state['wiki_page_name']}")
    merged = await call_llm(
        system_prompt=MERGE_WIKI_PROMPT,
        user_prompt=(
            f"EXISTING WIKI PAGE:\n{state['existing_content']}\n\n"
            f"NEW INFORMATION TO MERGE:\n{state['new_wiki_content']}"
        )
    )
    return {**state, "final_content": merged, "action": "merged"}


async def create_node(state: IngestionState) -> IngestionState:
    """Step 4b: Create a brand new wiki page."""
    logger.info(f"Ingestion step: creating {state['wiki_page_name']}")
    return {
        **state,
        "final_content": state["new_wiki_content"],
        "action": "created"
    }


async def reject_node(state: IngestionState) -> IngestionState:
    """Step 4c: Reject due to contradiction."""
    logger.info(f"Ingestion step: rejecting {state['wiki_page_name']}")
    append_log(
        f"REJECTED ingestion for {state['wiki_page_name']} "
        f"— contradictions found"
    )
    return {**state, "status": "flagged", "action": "rejected"}


async def write_node(state: IngestionState) -> IngestionState:
    """Step 5: Write final content to wiki."""
    logger.info(f"Ingestion step: writing {state['wiki_page_name']}")
    write_wiki_page(state["wiki_page_name"], state["final_content"])
    append_log(
        f"{state['action'].upper()} wiki page: "
        f"{state['wiki_page_name']} | "
        f"source: {state['source_type']}"
    )
    return {**state, "status": "success"}


# ── Routing ───────────────────────────────────────────

def route_after_extract(state: IngestionState) -> str:
    if state["status"] == "failed":
        return END
    return "check_wiki"


def route_after_contradiction(state: IngestionState) -> str:
    if not state["existing_content"]:
        return "create"
    recommendation = state.get("contradiction", {}).get(
        "recommendation", "merge_anyway"
    )
    if recommendation == "reject":
        return "reject"
    return "merge"


def route_after_action(state: IngestionState) -> str:
    if state["action"] == "rejected":
        return END
    return "write"


# ── Build Graph ───────────────────────────────────────

def build_ingestion_graph():
    graph = StateGraph(IngestionState)

    graph.add_node("extract", extract_node)
    graph.add_node("check_wiki", check_wiki_node)
    graph.add_node("contradiction_check", contradiction_node)
    graph.add_node("merge", merge_node)
    graph.add_node("create", create_node)
    graph.add_node("reject", reject_node)
    graph.add_node("write", write_node)

    graph.set_entry_point("extract")

    graph.add_conditional_edges("extract", route_after_extract)
    graph.add_edge("check_wiki", "contradiction_check")
    graph.add_conditional_edges(
        "contradiction_check", route_after_contradiction
    )
    graph.add_conditional_edges("merge", route_after_action)
    graph.add_conditional_edges("create", route_after_action)
    graph.add_conditional_edges("reject", route_after_action)
    graph.add_edge("write", END)

    return graph.compile()


ingestion_graph = build_ingestion_graph()


# ── Main Entry ────────────────────────────────────────

async def run_ingestion_agent(
    raw_content: str,
    source_type: str,
    source_ref: str = ""
) -> dict:
    initial_state: IngestionState = {
        "raw_content": raw_content,
        "source_type": source_type,
        "source_ref": source_ref,
        "extraction": None,
        "wiki_page_name": None,
        "new_wiki_content": None,
        "existing_content": None,
        "contradiction": None,
        "final_content": None,
        "action": None,
        "status": None,
        "error": None
    }

    result = await ingestion_graph.ainvoke(initial_state)

    return {
        "status": result.get("status"),
        "wiki_page_name": result.get("wiki_page_name"),
        "action": result.get("action"),
        "title": result.get("extraction", {}).get("title"),
        "concepts": result.get("extraction", {}).get("concepts", []),
        "tags": result.get("extraction", {}).get("tags", []),
        "error": result.get("error")
    }