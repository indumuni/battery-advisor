from battery_advisor.rag.ingest import ingest
from battery_advisor.rag.retriever import search_knowledge

n = ingest()
print(f"Indexed {n} chunks")
for hit in search_knowledge("can I charge LiFePO4 in freezing weather", k=3)["results"]:
    print(f'{hit["score"]:.2f}  {hit["source"]}  [{hit["heading"]}]')