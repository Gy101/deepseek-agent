"""把检索结果整理成结构化对象，供提示词注入与前端展示。"""


def retrieve(store, query: str, top_k: int = 3, threshold: float = 0.0) -> list[dict]:
    """返回 [{index, source, heading, score, snippet, text}]。"""
    results: list[dict] = []
    for rank, (score, _idx, chunk) in enumerate(store.search(query, top_k, threshold), start=1):
        results.append(
            {
                "index": rank,
                "source": chunk["source"],
                "heading": chunk.get("heading", ""),
                "score": round(score, 4),
                "snippet": chunk["text"][:200],
                "text": chunk["text"],
            }
        )
    return results
