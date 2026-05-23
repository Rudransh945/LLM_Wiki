# AI Second Brain (LLM Wiki-Inspired) — Full Antigravity Implementation Manual

# 1. Product Definition (NON-NEGOTIABLE)

## What this project IS
A persistent AI second brain inspired by Andrej Karpathy’s LLM Wiki concept.

This system:
- captures raw information from multiple sources
- converts raw information into structured long-term memory
- maintains a living knowledge wiki
- answers questions using accumulated knowledge
- reflects on patterns in knowledge/thinking
- recommends learning paths
- performs maintenance on its own knowledge base

Core identity:
**Personal cognitive operating system**

---

## What this project is NOT
NOT:
- a simple chatbot
- a normal RAG assistant
- a note-taking app clone
- temporary context retrieval
- generic Q&A bot

Difference from normal RAG:

Normal RAG:
query → retrieve chunks → answer → forget

This system:
query → retrieve knowledge → reason → preserve memory → evolve

---

## Karpathy Alignment
Original LLM Wiki principle:
AI should maintain the wiki.

So:

WRONG:
Human writes wiki, AI reads it.

CORRECT:
Human provides raw knowledge, AI builds wiki.

This implementation follows that.

---

# 2. System Philosophy

Mental model:

Human brain equivalent:

- sensory input → raw/
- long-term memory → wiki/
- semantic association → FAISS/vector memory
- reasoning cortex → Groq LLM
- habits/reflection → reflection agents
- maintenance/cleanup → maintenance agent

This is a second brain, not a chatbot.

---

# 3. Final Vault Contract

```text
vault/
  raw/
    thoughts/
    web/
    clips/
    docs/

  wiki/
  index.md
  log.md
```

---

## Folder Rules

### raw/
SOURCE OF TRUTH

Rules:
- immutable
- never overwrite original source
- AI reads from here
- provenance must be preserved

Subfolders:

#### raw/thoughts/
User quick ideas.
Example:
- startup idea
- AI architecture thought
- learning insight

#### raw/web/
Web research captures.
Stored with:
- URL
- timestamp
- title
- raw extracted text

#### raw/clips/
Browser clipper captures.

#### raw/docs/
PDF/DOC/TXT imports.

---

### wiki/
AI-MANAGED LONG TERM MEMORY

Rules:
- AI writes here
- user can review/edit optionally
- structured markdown knowledge only
- no raw junk

Contains:
- concepts
- summaries
- topic pages
- comparisons
- reflections
- learning notes

---

### index.md
Navigation map.

Purpose:
quick entry into knowledge base.

---

### log.md
Audit trail.

Tracks:
- what got ingested
- what changed
- timestamps
- failures

---

# 4. Final Tech Stack

## Core Stack

### Obsidian
Purpose:
persistent markdown knowledge memory

Why:
- graph visualization
- markdown-native
- local-first
- human readable

---

### Groq
Purpose:
LLM reasoning engine

Responsibilities:
- reasoning
- synthesis
- extraction
- reflection
- query answering

---

### FastAPI
Purpose:
backend orchestration

Responsibilities:
- APIs
- service orchestration
- agent triggers

---

### LangGraph
Purpose:
agent workflow orchestration

Needed because:
multiple stateful agents exist.

---

### FAISS
Purpose:
semantic memory retrieval

Needed because keyword search is insufficient.

---

### Sentence Transformers
Purpose:
embedding generation

Suggested:
all-MiniLM-L6-v2

---

### SQLite
Purpose:
metadata persistence

Stores:
- source records
- ingestion state
- wiki mappings
- logs

---

### APScheduler
Purpose:
automation

Examples:
- nightly reflection
- maintenance runs
- periodic indexing

---

### BeautifulSoup
Purpose:
HTML parsing

---

### PyMuPDF
Purpose:
PDF ingestion

---

### Streamlit
Purpose:
MVP interface

---

# 5. Full Backend Structure

```text
app/
  api/
    ingest.py
    query.py
    research.py
    reflect.py
    maintenance.py

  agents/
    ingestion_agent.py
    query_agent.py
    reflection_agent.py
    learning_agent.py
    maintenance_agent.py
    research_agent.py

  services/
    vault_service.py
    llm_service.py
    embedding_service.py
    retrieval_service.py
    parser_service.py
    wiki_service.py

  workflows/
    ingestion_workflow.py
    query_workflow.py
    reflection_workflow.py
    maintenance_workflow.py
    research_workflow.py

  db/
    models.py
    repository.py
    session.py

  parsers/
    markdown_parser.py
    pdf_parser.py
    web_parser.py

  prompts/
    ingestion_prompts.py
    query_prompts.py
    reflection_prompts.py
    maintenance_prompts.py

  utils/
```

---

# 6. Agent Architecture

## Ingestion Agent
MOST IMPORTANT AGENT

Responsibilities:
- detect new source
- classify source type
- parse source
- normalize content
- extract concepts
- detect relationships
- compare with wiki
- detect contradictions
- create/update wiki pages
- refresh vector index
- log activity

Workflow:

```text
new source
 ↓
classify
 ↓
parse
 ↓
normalize
 ↓
extract concepts
 ↓
find related wiki pages
 ↓
merge logic
 ↓
contradiction detection
 ↓
write wiki
 ↓
refresh FAISS
 ↓
log
```

---

## Query Agent
Responsibilities:
- accept user question
- determine intent
- retrieve relevant knowledge
- semantic recall
- context assembly
- reasoning
- answer generation

Workflow:

```text
query
 ↓
intent classification
 ↓
keyword retrieval
 ↓
semantic retrieval
 ↓
rank context
 ↓
Groq reasoning
 ↓
response
```

---

## Reflection Agent
Responsibilities:
- detect recurring themes
- infer evolving interests
- identify behavioral patterns
- summarize intellectual progress

---

## Learning Advisor Agent
Responsibilities:
- knowledge gap detection
- roadmap suggestion
- weak area discovery

---

## Maintenance Agent
Responsibilities:
- duplicate detection
- broken links
- stale pages
- contradictions
- orphan pages

---

## Research Agent
Responsibilities:
- web search
- fetch sources
- save to raw/web
- trigger ingestion

---

# 7. FastAPI APIs

```text
POST /ingest
POST /query
POST /research
POST /reflect
POST /lint
GET /wiki/page/{name}
GET /status
```

---

# 8. SQLite Schema

```sql
sources(
 id,
 type,
 path,
 source_url,
 timestamp,
 processed,
 hash
)

wiki_pages(
 id,
 name,
 path,
 updated_at,
 embedding_version
)

ingestion_logs(
 id,
 source_id,
 action,
 status,
 timestamp
)

agent_runs(
 id,
 agent_name,
 status,
 started_at,
 ended_at
)

reflections(
 id,
 summary,
 created_at
)
```

---

# 9. Semantic Memory Design

Pipeline:

```text
wiki page
 ↓
chunk
 ↓
embed
 ↓
store in FAISS
 ↓
query retrieval
```

Rules:
- hybrid retrieval
- keyword + semantic
- top-k ranking
- periodic refresh

---

# 10. Prompt Contracts

Antigravity should preserve prompt modularity.

Prompts needed:
- ingestion prompt
- merge prompt
- contradiction prompt
- query prompt
- reflection prompt
- maintenance prompt
- advisor prompt

---

# 11. Build Roadmap

## Phase 1
MVP

Build:
- vault integration
- ingestion
- wiki writing
- query answering

## Phase 2
Semantic memory

Build:
- embeddings
- FAISS
- retrieval

## Phase 3
Agent intelligence

Build:
- reflection
- learning advisor
- maintenance

## Phase 4
Automation

Build:
- scheduler
- auto maintenance
- auto reflection

## Phase 5
Advanced autonomy

Build:
- voice
- proactive suggestions
- autonomous research

---

# 12. Engineering Risks

Risks:
- hallucinated wiki updates
- duplicate pages
- semantic drift
- stale embeddings
- corrupted knowledge
- poor retrieval

Mitigations:
- provenance
- approval mode
- maintenance agent
- immutable raw storage

---

# 13. Antigravity Build Instructions

Build exactly with:
- modular architecture
- service separation
- agent orchestration via LangGraph
- approval mode first
- deterministic ingestion where possible
- semantic retrieval mandatory
- preserve vault contract

DO NOT simplify into basic chatbot architecture.

Project identity must remain second-brain architecture.

