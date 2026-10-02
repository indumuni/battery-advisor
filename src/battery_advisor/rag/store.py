import os
from functools import lru_cache
from pathlib import Path
import chromadb

ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_DIR = ROOT / "data" / "knowledge"
COLLECTION = "battery_knowledge"

def index_dir() -> str:
    return os.environ.get("BATTERY_VECTORSTORE", str(ROOT / "data" / "vectorstore"))

@lru_cache
def get_client(path: str):
    return chromadb.PersistentClient(path=path)

def get_collection():
    """Raises if the index has not been built."""
    return get_client(index_dir()).get_collection(COLLECTION)

def reset_collection():
    client = get_client(index_dir())
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    return client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})