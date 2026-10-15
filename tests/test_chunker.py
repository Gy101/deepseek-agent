from app.rag.chunker import chunk_document


def test_chunk_captures_heading():
    text = "# 计费\n\n基础版每月 99 元。\n\n专业版每月 299 元。\n"
    chunks = chunk_document(text, "pricing.md", max_chars=500)
    assert len(chunks) == 2
    assert all(c["source"] == "pricing.md" for c in chunks)
    assert all(c["heading"] == "计费" for c in chunks)


def test_chunk_respects_max_chars():
    long_text = "这是很长的一句话。" * 200
    chunks = chunk_document(long_text, "long.md", max_chars=100)
    assert len(chunks) > 1
    assert all(len(c["text"]) <= 100 for c in chunks)
