#!/usr/bin/env python3
"""CLI：加载并重建知识库索引，打印统计信息。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import BASE_DIR, settings  # noqa: E402
from app.rag.store import KnowledgeStore  # noqa: E402


def main() -> None:
    store = KnowledgeStore((BASE_DIR / settings.knowledge_dir).resolve())
    store.build()
    docs = {c["source"] for c in store.chunks}
    print(f"已索引 {store.chunk_count} 个知识块，来自 {len(docs)} 篇文档：")
    for source in sorted(docs):
        print(f"  - {source}")


if __name__ == "__main__":
    main()
