"""轻量分词：中文按字符 bigram，英文/数字按单词。

纯标准库实现，无 jieba/numpy 等重依赖。中文使用字符 bigram 可以在
不做词法分词的情况下较好地覆盖词组与短语，适合 TF-IDF 关键词检索。
"""
import re

# 英文单词与数字
_WORD_RE = re.compile(r"[a-z0-9]+")
# 连续中文字符
_CJK_RUN_RE = re.compile(r"[一-鿿]+")

# 常见中英文停用词（英文按单词过滤，中文停用词不参与 bigram 判定，仅示例）
_STOPWORDS = frozenset(
    {
        "a", "an", "the", "is", "are", "was", "were", "be", "been",
        "and", "or", "of", "to", "in", "on", "for", "with", "as",
        "at", "by", "it", "this", "that", "these", "those", "we", "you",
    }
)


def tokenize(text: str) -> list[str]:
    """把文本切分成词元（token）列表。"""
    text = text.lower()
    tokens: list[str] = []

    # 英文 / 数字单词
    for m in _WORD_RE.finditer(text):
        word = m.group()
        if word not in _STOPWORDS:
            tokens.append(word)

    # 中文：连续串拆成 bigram；单字符串原样保留
    for m in _CJK_RUN_RE.finditer(text):
        run = m.group()
        if len(run) == 1:
            tokens.append(run)
        else:
            tokens.extend(run[i:i + 2] for i in range(len(run) - 1))

    return tokens
