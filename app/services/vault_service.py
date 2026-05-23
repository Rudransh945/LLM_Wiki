import os
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path(os.getenv("VAULT_PATH", "./llmwikivault"))


def get_raw_path(subfolder: str = "") -> Path:
    p = VAULT_PATH / "raw_text"
    if subfolder:
        p = p / subfolder
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_wiki_path() -> Path:
    p = VAULT_PATH / "wiki"
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_raw_thought(content: str, title: str = None) -> Path:
    folder = get_raw_path("thoughts")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(title) if title else f"thought_{timestamp}"
    filepath = folder / f"{slug}.md"
    filepath.write_text(
        f"# {title or 'Thought'}\n\n"
        f"{content}\n\n"
        f"---\n"
        f"_Captured: {datetime.utcnow().isoformat()}_\n"
    )
    return filepath


def save_raw_web(content: str, url: str, title: str = "") -> Path:
    folder = get_raw_path("web")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(title) if title else f"web_{timestamp}"
    filepath = folder / f"{slug}.md"
    filepath.write_text(
        f"# {title or url}\n\n"
        f"**Source:** {url}\n"
        f"**Captured:** {datetime.utcnow().isoformat()}\n\n"
        f"---\n\n{content}\n"
    )
    return filepath


def read_raw_file(filepath: str) -> str:
    return Path(filepath).read_text(encoding="utf-8")


def read_wiki_page(name: str) -> str | None:
    filepath = get_wiki_path() / f"{name}.md"
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return None


def write_wiki_page(name: str, content: str) -> Path:
    filepath = get_wiki_path() / f"{name}.md"
    filepath.write_text(content, encoding="utf-8")
    _update_index(name)
    return filepath


def list_wiki_pages() -> list[str]:
    wiki_path = get_wiki_path()
    return [f.stem for f in wiki_path.glob("*.md")]


def list_raw_files(subfolder: str = "") -> list[Path]:
    folder = get_raw_path(subfolder)
    return list(folder.glob("**/*.md")) + \
           list(folder.glob("**/*.txt"))


def append_log(entry: str):
    log_path = VAULT_PATH / "log.md"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n- [{timestamp}] {entry}")


def _update_index(page_name: str):
    index_path = VAULT_PATH / "index.md"
    if not index_path.exists():
        index_path.write_text("# Knowledge Index\n\n")
    content = index_path.read_text(encoding="utf-8")
    link = f"- [[{page_name}]]"
    if link not in content:
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(f"{link}\n")


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text[:60]