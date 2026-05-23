from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    path = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    hash = Column(String, nullable=True, unique=True)


class WikiPage(Base):
    __tablename__ = "wiki_pages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    path = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    embedding_version = Column(Integer, default=0)


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)


class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(Integer, primary_key=True, index=True)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)