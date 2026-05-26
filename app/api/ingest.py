from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.repository import (
    source_exists, create_source, mark_source_processed,
    log_ingestion, log_agent_run, complete_agent_run, compute_hash
)
from app.agents.ingestion_agent import run_ingestion_agent
from app.services.vault_service import (
    save_raw_thought, save_raw_web, append_log
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request Models ────────────────────────────────────

class ThoughtRequest(BaseModel):
    content: str
    title: str = ""


class WebRequest(BaseModel):
    content: str
    url: str
    title: str = ""


class RawRequest(BaseModel):
    content: str
    source_type: str = "doc"
    source_ref: str = ""


# ── Endpoints ─────────────────────────────────────────

@router.post("/thought")
async def ingest_thought(
    req: ThoughtRequest,
    db: AsyncSession = Depends(get_db)
):
    """Ingest a quick thought or idea."""
    content_hash = compute_hash(req.content)

    if await source_exists(db, content_hash):
        return {"status": "skipped", "reason": "duplicate content"}

    raw_path = save_raw_thought(req.content, req.title)
    source = await create_source(
        db, type="thought",
        path=str(raw_path),
        content_hash=content_hash
    )

    run = await log_agent_run(db, "ingestion_agent")
    try:
        result = await run_ingestion_agent(
            raw_content=req.content,
            source_type="thought",
            source_ref=req.title or "quick thought"
        )
        await mark_source_processed(db, source.id)
        await log_ingestion(
            db, action="ingest_thought",
            status=result["status"],
            source_id=source.id,
            detail=result.get("wiki_page_name")
        )
        await complete_agent_run(db, run.id, status="success")
        return result

    except Exception as e:
        await log_ingestion(
            db, action="ingest_thought",
            status="failed",
            source_id=source.id,
            detail=str(e)
        )
        await complete_agent_run(db, run.id, status="failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/web")
async def ingest_web(
    req: WebRequest,
    db: AsyncSession = Depends(get_db)
):
    """Ingest a web page capture."""
    content_hash = compute_hash(req.content)

    if await source_exists(db, content_hash):
        return {"status": "skipped", "reason": "duplicate content"}

    raw_path = save_raw_web(req.content, req.url, req.title)
    source = await create_source(
        db, type="web",
        path=str(raw_path),
        source_url=req.url,
        content_hash=content_hash
    )

    run = await log_agent_run(db, "ingestion_agent")
    try:
        result = await run_ingestion_agent(
            raw_content=req.content,
            source_type="web",
            source_ref=req.url
        )
        await mark_source_processed(db, source.id)
        await log_ingestion(
            db, action="ingest_web",
            status=result["status"],
            source_id=source.id,
            detail=result.get("wiki_page_name")
        )
        await complete_agent_run(db, run.id, status="success")
        return result

    except Exception as e:
        await log_ingestion(
            db, action="ingest_web",
            status="failed",
            source_id=source.id,
            detail=str(e)
        )
        await complete_agent_run(db, run.id, status="failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/raw")
async def ingest_raw(
    req: RawRequest,
    db: AsyncSession = Depends(get_db)
):
    """Ingest any raw content."""
    content_hash = compute_hash(req.content)

    if await source_exists(db, content_hash):
        return {"status": "skipped", "reason": "duplicate content"}

    source = await create_source(
        db, type=req.source_type,
        source_url=req.source_ref,
        content_hash=content_hash
    )

    run = await log_agent_run(db, "ingestion_agent")
    try:
        result = await run_ingestion_agent(
            raw_content=req.content,
            source_type=req.source_type,
            source_ref=req.source_ref
        )
        await mark_source_processed(db, source.id)
        await log_ingestion(
            db, action="ingest_raw",
            status=result["status"],
            source_id=source.id,
            detail=result.get("wiki_page_name")
        )
        await complete_agent_run(db, run.id, status="success")
        return result

    except Exception as e:
        await log_ingestion(
            db, action="ingest_raw",
            status="failed",
            source_id=source.id,
            detail=str(e)
        )
        await complete_agent_run(db, run.id, status="failed")
        raise HTTPException(status_code=500, detail=str(e))