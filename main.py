from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ingest, query
from app.db.session import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Second Brain",
    description="Personal cognitive operating system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(query.router, prefix="/query", tags=["Query"])


@app.on_event("startup")
async def startup():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Second Brain is online.")


@app.get("/status")
async def status():
    return {
        "status": "online",
        "system": "AI Second Brain",
        "version": "1.0.0 - Phase 1"
    }