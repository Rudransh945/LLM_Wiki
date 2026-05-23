from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Source, WikiPage, IngestionLog, AgentRun
from datetime import datetime
import hashlib


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


# ── Sources ───────────────────────────────────────────

async def source_exists(db: AsyncSession, content_hash: str) -> bool:
    result = await db.execute(
        select(Source).where(Source.hash == content_hash)
    )
    return result.scalar_one_or_none() is not None


async def create_source(db: AsyncSession, type: str, path: str = None,
                         source_url: str = None, content_hash: str = None) -> Source:
    source = Source(type=type, path=path, 
                    source_url=source_url, hash=content_hash)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


async def mark_source_processed(db: AsyncSession, source_id: int):
    result = await db.execute(
        select(Source).where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()
    if source:
        source.processed = True
        await db.commit()


# ── Wiki Pages ────────────────────────────────────────

async def upsert_wiki_page(db: AsyncSession, name: str, path: str) -> WikiPage:
    result = await db.execute(
        select(WikiPage).where(WikiPage.name == name)
    )
    page = result.scalar_one_or_none()
    if page:
        page.path = path
        page.updated_at = datetime.utcnow()
        page.embedding_version += 1
    else:
        page = WikiPage(name=name, path=path)
        db.add(page)
    await db.commit()
    await db.refresh(page)
    return page


async def get_all_wiki_pages(db: AsyncSession):
    result = await db.execute(select(WikiPage))
    return result.scalars().all()


# ── Logs ──────────────────────────────────────────────

async def log_ingestion(db: AsyncSession, action: str, status: str,
                         source_id: int = None, detail: str = None):
    log = IngestionLog(source_id=source_id, action=action, 
                       status=status, detail=detail)
    db.add(log)
    await db.commit()


async def log_agent_run(db: AsyncSession, agent_name: str) -> AgentRun:
    run = AgentRun(agent_name=agent_name, status="running")
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def complete_agent_run(db: AsyncSession, run_id: int, 
                              status: str = "success"):
    result = await db.execute(
        select(AgentRun).where(AgentRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if run:
        run.status = status
        run.ended_at = datetime.utcnow()
        await db.commit()