from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

VAULT_PATH = Path(os.getenv("VAULT_PATH", "./llmwikivault"))


def is_empty(content: str) -> bool:
    stripped = content.strip()
    lines = [l.strip() for l in stripped.splitlines() if l.strip()]
    non_heading_lines = [l for l in lines if not l.startswith('#')]
    return len(non_heading_lines) == 0


def clean_vault():
    # Scan entire vault for empty md files
    all_files = list(VAULT_PATH.rglob('*.md'))
    print(f'Found {len(all_files)} total md files')

    deleted = 0
    for f in all_files:
        # Skip files in wiki/ and raw_text/ — only clean root level
        try:
            content = f.read_text(encoding='utf-8')
            if is_empty(content):
                print(f'🗑️ Deleting empty file: {f.name}')
                f.unlink()
                deleted += 1
        except Exception as e:
            print(f'Error reading {f.name}: {e}')

    print(f'\nDone! Deleted {deleted} empty files.')


clean_vault()
