"""内存知识库：加载文档 → 切块 → 建 TF-IDF 索引 → 检索。"""
from . import chunker, loader
from .tfidf import TfidfIndex
from .tokenizer import tokenize


class KnowledgeStore:
    def __init__(self, knowledge_dir, max_chars: int = chunker.DEFAULT_MAX_CHARS):
        self.knowledge_dir = knowledge_dir
        self.max_chars = max_chars
        self.chunks: list[dict] = []
        self.index: TfidfIndex | None = None

    def build(self) -> "KnowledgeStore":
        """重新加载并索引知识库。"""
        docs = loader.load_documents(self.knowledge_dir)
        chunks: list[dict] = []
        for doc in docs:
            chunks.extend(chunker.chunk_document(doc["text"], doc["source"], self.max_chars))
        self.chunks = chunks
        self.index = TfidfIndex(chunks, tokenize) if chunks else None
        return self

    def search(self, query: str, top_k: int = 3, threshold: float = 0.0) -> list[tuple]:
        if self.index is None:
            return []
        return self.index.search(query, tokenize, top_k=top_k, threshold=threshold)

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)
