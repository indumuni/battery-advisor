from battery_advisor.rag.store import get_collection

MIN_SCORE = 0.25   # cosine similarity floor; tune it against your evals

def search_knowledge(query: str, k: int = 4, category: str | None = None) -> dict:
    try:
        col = get_collection()
    except Exception:
        return {"error": "Knowledge index not built. Run: uv run python scripts/build_index.py"}

    res = col.query(query_texts=[query], n_results=k,
                    where={"category": category} if category else None)
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        score = round(1 - dist, 3)
        if score >= MIN_SCORE:
            hits.append({"source": meta["source"], "heading": meta["heading"],
                         "score": score, "text": doc})
    if not hits:
        return {"query": query, "results": [],
                "note": "No relevant passages found. Say so; do not answer as if sourced."}
    return {"query": query, "results": hits}