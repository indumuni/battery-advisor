"""Ingest knowledge documents into the vector store."""

# TODO: Implement this roadmap component.
from battery_advisor.rag.chunking import split_markdown
from battery_advisor.rag.store import KNOWLEDGE_DIR, reset_collection

def ingest() -> int:
    """Rebuild the whole index from data/knowledge/**/*.md. Returns the chunk count."""
    col = reset_collection()
    ids, docs, metas = [], [], []
    for path in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        rel = path.relative_to(KNOWLEDGE_DIR)
        category = rel.parts[0]                      # datasheets | guides | standards
        for i, c in enumerate(split_markdown(path.read_text())):
            ids.append(f"{rel.as_posix()}::{i}")
            docs.append(c.text)
            metas.append({"source": rel.as_posix(), "category": category, "heading": c.heading})
    if docs:
        col.add(ids=ids, documents=docs, metadatas=metas)
    return len(docs)