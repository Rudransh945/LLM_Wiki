import time
import logging
import asyncio
import httpx
import sqlite3
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import os

load_dotenv()

VAULT_PATH = Path(os.getenv("VAULT_PATH", "./llmwikivault"))
CLIPS_PATH = VAULT_PATH / "raw_text" / "clips"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_empty_file(content: str) -> bool:
    """Check if file is empty or contains only headings."""
    stripped = content.strip()
    lines = [l.strip() for l in stripped.splitlines() if l.strip()]
    non_heading_lines = [l for l in lines if not l.startswith('#')]
    return len(non_heading_lines) == 0


def clean_vault_empty_files():
    """Delete all empty or heading-only md files from entire vault."""
    print('\n🧹 Cleaning empty files from vault...')
    all_files = list(VAULT_PATH.rglob('*.md'))
    deleted = 0
    for f in all_files:
        # Never delete files inside wiki/ or raw_text/clips/
        if 'wiki' in f.parts or 'clips' in f.parts or 'raw_text' in f.parts:
            continue
        try:
            content = f.read_text(encoding='utf-8')
            if is_empty_file(content):
                print(f'🗑️ Deleting empty file: {f.name}')
                f.unlink()
                deleted += 1
        except Exception as e:
            logger.error(f'Error reading {f.name}: {e}')
    print(f'🧹 Cleaned {deleted} empty files\n')


def already_ingested(content: str) -> bool:
    """Check if file was already ingested by comparing hash."""
    try:
        h = hashlib.sha256(content.encode()).hexdigest()
        conn = sqlite3.connect('second_brain.db')
        cursor = conn.execute(
            'SELECT id FROM sources WHERE hash = ?', (h,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False


async def ingest_file(filepath: Path):
    """Send a single file to the ingest API."""
    try:
        content = filepath.read_text(encoding='utf-8')
        async with httpx.AsyncClient() as client:
            r = await client.post(
                'http://localhost:8000/ingest/raw',
                json={
                    'content': content,
                    'source_type': 'clip',
                    'source_ref': filepath.name
                },
                timeout=180
            )
            result = r.json()
            status = result.get('status')
            wiki = result.get('wiki_page_name')
            print(f'✅ {filepath.name} → {status} | wiki: {wiki}')
    except Exception as e:
        logger.error(f'Failed to ingest {filepath.name}: {e}')


class ClipHandler(FileSystemEventHandler):
    """Watches clips folder and auto ingests new files."""

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        if filepath.suffix in ['.md', '.txt']:
            time.sleep(2)
            content = filepath.read_text(encoding='utf-8')

            if is_empty_file(content):
                print(f'🗑️ Empty file detected: {filepath.name} — deleting')
                filepath.unlink()
                return

            logger.info(f'New clip detected: {filepath.name}')
            asyncio.run(ingest_file(filepath))

    def on_modified(self, event):
        """Also watch for empty files created anywhere in vault."""
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        if filepath.suffix == '.md':
            # Only clean root level vault files not in clips or wiki
            if 'wiki' not in filepath.parts and \
               'clips' not in filepath.parts and \
               'raw_text' not in filepath.parts:
                try:
                    content = filepath.read_text(encoding='utf-8')
                    if is_empty_file(content):
                        print(f'🗑️ Empty vault file: {filepath.name} — deleting')
                        filepath.unlink()
                except Exception:
                    pass


def start_watcher():
    """Start watching clips folder. Also ingests any existing uningested files."""
    # Clean empty files from vault first
    clean_vault_empty_files()

    CLIPS_PATH.mkdir(parents=True, exist_ok=True)
    logger.info(f'Watching: {CLIPS_PATH}')

    # Scan existing clips
    print('Checking for existing clips...')
    existing_files = list(CLIPS_PATH.glob('*.md'))
    print(f'Found {len(existing_files)} existing clips')

    for f in existing_files:
        content = f.read_text(encoding='utf-8')

        if is_empty_file(content):
            print(f'🗑️ Empty file: {f.name} — deleting')
            f.unlink()
            continue

        if already_ingested(content):
            print(f'⏭️ Already ingested: {f.name} — skipping')
            continue

        print(f'📥 New clip found: {f.name} — ingesting...')
        asyncio.run(ingest_file(f))
        time.sleep(3)

    # Watch entire vault for empty files + clips folder for new clips
    print('\n👁️ Watcher is now running...')
    print('Any new clip you add will be auto ingested!')
    print('Empty files will be auto deleted!')
    print('Press CTRL+C to stop\n')

    event_handler = ClipHandler()
    observer = Observer()

    # Watch clips folder for new clips
    observer.schedule(event_handler, str(CLIPS_PATH), recursive=True)

    # Also watch vault root for empty files created by Obsidian
    observer.schedule(event_handler, str(VAULT_PATH), recursive=False)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print('\nWatcher stopped.')
    observer.join()
    