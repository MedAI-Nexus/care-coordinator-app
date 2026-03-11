"""Query ChromaDB for relevant chunks."""

import chromadb
from config import CHROMA_PERSIST_DIR


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    # Uses ChromaDB's default embedding function (onnxruntime all-MiniLM-L6-v2)
    # Compatible with sentence-transformers embeddings used during ingestion
    return client.get_or_create_collection(
        name="neuronav_docs",
        metadata={"hnsw:space": "cosine"},
    )


def search(query: str, drug_filter: str = None, doc_type_filter: str = None, n_results: int = 5) -> list:
    """Search the knowledge base."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    where_filter = None
    conditions = []
    if drug_filter:
        conditions.append({"drug": drug_filter.lower()})
    if doc_type_filter:
        conditions.append({"doc_type": doc_type_filter})

    if len(conditions) == 1:
        where_filter = conditions[0]
    elif len(conditions) > 1:
        where_filter = {"$and": conditions}

    kwargs = {
        "query_texts": [query],
        "n_results": min(n_results, collection.count()),
    }
    if where_filter:
        kwargs["where"] = where_filter

    results = collection.query(**kwargs)

    output = []
    for i in range(len(results["documents"][0])):
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        output.append({
            "content": results["documents"][0][i],
            "source": meta.get("source", "Unknown"),
            "drug": meta.get("drug", ""),
            "doc_type": meta.get("doc_type", ""),
        })

    return output
