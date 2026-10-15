from app.rag.tfidf import TfidfIndex
from app.rag.tokenizer import tokenize


def test_search_returns_most_relevant():
    docs = [
        {"text": "退款政策：购买后七天内可以申请全额退款。", "source": "refund.md"},
        {"text": "公司成立于 2020 年，专注于人工智能。", "source": "about.md"},
    ]
    idx = TfidfIndex(docs, tokenize)
    results = idx.search("退款怎么申请？", tokenize, top_k=1)
    assert results[0][2]["source"] == "refund.md"


def test_search_empty_query_returns_empty():
    docs = [{"text": "一些内容", "source": "a.md"}]
    idx = TfidfIndex(docs, tokenize)
    assert idx.search("?!?！？", tokenize) == []
