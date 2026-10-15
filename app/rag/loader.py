"""扫描知识库目录，加载 Markdown / 纯文本文档。"""
from pathlib import Path

_SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt"}


def load_documents(knowledge_dir) -> list[dict]:
    """返回 [{text, source}]，source 为相对知识库根目录的路径。"""
    docs: list[dict] = []
    root = Path(knowledge_dir)
    if not root.exists():
        return docs
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if not text.strip():
            continue
        docs.append({"text": text, "source": str(path.relative_to(root))})
    return docs
