import asyncio
import httpx
from pathlib import Path
import sqlite3

CLIPS_PATH = Path(r'C:\GenAI_projects\LLM_wiki\LLM_Wiki_vault\LLM_Wiki\raw_text\clips')
DB_PATH = r'C:\GenAI_projects\LLM_wiki\second_brain.db'


def get_already_ingested() -> set:
    """Get all file names already ingested from database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(
            "SELECT source_url FROM sources WHERE processed = 1"
        )
        ingested = {row[0] for row in cursor.fetchall()}
        conn.close()
        return ingested
    except Exception:
        return set()


async def ingest_all():
    files = list(CLIPS_PATH.glob('*.md'))
    print(f'Found {len(files)} files in clips folder')

    already_ingested = get_already_ingested()
    print(f'Already ingested: {len(already_ingested)} files')

    new_files = [f for f in files if f.name not in already_ingested]
    print(f'New files to ingest: {len(new_files)}')

    if not new_files:
        print('Nothing new to ingest!')
        return

    for f in new_files:
        print(f'\nIngesting: {f.name}...')
        content = f.read_text(encoding='utf-8')
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    'http://localhost:8000/ingest/raw',
                    json={
                        'content': content,
                        'source_type': 'clip',
                        'source_ref': f.name
                    },
                    timeout=180
                )
                result = r.json()
                status = result.get('status')
                wiki = result.get('wiki_page_name')
                print(f'✅ {f.name} → {status} | wiki: {wiki}')
        except Exception as e:
            print(f'❌ Error on {f.name}: {e}')

        await asyncio.sleep(3)

    print('\nDone! All new clips ingested.')

asyncio.run(ingest_all())