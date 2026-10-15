"""TF-IDF 向量化 + 余弦相似度检索（纯标准库）。"""
import math
from collections import Counter


class TfidfIndex:
    """对一组文档建 TF-IDF 索引，并支持按余弦相似度检索。"""

    def __init__(self, documents: list[dict], tokenizer):
        self.documents = documents
        self.idf: dict[str, float] = {}
        self._build(documents, tokenizer)

    def _build(self, documents: list[dict], tokenizer) -> None:
        n = len(documents)
        if n == 0:
            return
        df: Counter[str] = Counter()
        for doc in documents:
            tokens = tokenizer(doc["text"])
            doc["tokens"] = tokens
            df.update(set(tokens))
        # 平滑 IDF：避免 log(0)，弱化高频词
        self.idf = {t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()}
        for doc in documents:
            doc["vector"] = self._vectorize(doc["tokens"])

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        vec = {t: c * self.idf.get(t, 0.0) for t, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    def search(
        self,
        query: str,
        tokenizer,
        top_k: int = 3,
        threshold: float = 0.0,
    ) -> list[tuple[float, int, dict]]:
        """返回 [(score, 文档下标, 文档), ...] 按得分降序。"""
        q_vec = self._vectorize(tokenizer(query))
        if not q_vec:
            return []
        scored: list[tuple[float, int, dict]] = []
        for i, doc in enumerate(self.documents):
            score = self._dot(q_vec, doc["vector"])
            if score >= threshold:
                scored.append((score, i, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _dot(a: dict[str, float], b: dict[str, float]) -> float:
        """两个已 L2 归一化的向量，点积即余弦相似度。"""
        smaller, larger = (a, b) if len(a) < len(b) else (b, a)
        return sum(v * larger.get(k, 0.0) for k, v in smaller.items())
