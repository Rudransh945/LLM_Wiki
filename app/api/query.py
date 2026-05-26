from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.query_agent import run_query_agent
from app.services.vault_service import (
    read_wiki_page, list_wiki_pages
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request Models ────────────────────────────────────

class QueryRequest(BaseModel):
    question: str


# ── Endpoints ─────────────────────────────────────────

@router.post("/")
async def query(req: QueryRequest):
    """Ask a question answered using your wiki knowledge."""
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    try:
        result = await run_query_agent(req.question)
        return result
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wiki/pages")
async def list_pages():
    """List all wiki pages in your knowledge base."""
    pages = list_wiki_pages()
    return {"pages": pages, "count": len(pages)}


@router.get("/wiki/page/{name}")
async def get_wiki_page(name: str):
    """Get content of a specific wiki page."""
    content = read_wiki_page(name)
    if not content:
        raise HTTPException(
            status_code=404,
            detail=f"Wiki page '{name}' not found"
        )
    return {"name": name, "content": content}