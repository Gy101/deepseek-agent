from app.rag.tokenizer import tokenize


def test_chinese_bigram():
    toks = tokenize("退款政策")
    assert "退款" in toks


def test_single_chinese_char():
    toks = tokenize("云")
    assert "云" in toks


def test_english_words_lowercased():
    toks = tokenize("Hello World")
    assert "hello" in toks
    assert "world" in toks


def test_stopwords_filtered():
    toks = tokenize("the product")
    assert "the" not in toks
    assert "product" in toks
