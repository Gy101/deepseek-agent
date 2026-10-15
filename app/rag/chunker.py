"""把文档切分成带标题上下文的文本块。"""
import re

DEFAULT_MAX_CHARS = 500
# 在句末标点后切分，保持句子完整
_SENT_SPLIT_RE = re.compile(r"(?<=[。！？!?；;])")
# 识别 Markdown 标题行
_HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")


def _split_long(text: str, max_chars: int) -> list[str]:
    """把一个长段按句子边界切成不超过 max_chars 的块，超长单句硬切。"""
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    parts: list[str] = []
    buf = ""
    for sent in _SENT_SPLIT_RE.split(text):
        if not sent:
            continue
        if len(buf) + len(sent) <= max_chars:
            buf += sent
        else:
            if buf:
                parts.append(buf.strip())
            # 单句超长则硬切
            while len(sent) > max_chars:
                parts.append(sent[:max_chars])
                sent = sent[max_chars:]
            buf = sent
    if buf.strip():
        parts.append(buf.strip())
    return parts


def chunk_document(text: str, source: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[dict]:
    """按空行分段、识别标题，返回 [{text, source, heading}] 列表。"""
    chunks: list[dict] = []
    heading = ""

    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        first = lines[0].lstrip()
        m = _HEADING_RE.match(first)
        if m:
            heading = m.group(1).strip()
            rest = "\n".join(lines[1:]).strip()
            for c in _split_long(rest, max_chars):
                chunks.append({"text": c, "source": source, "heading": heading})
        else:
            for c in _split_long(block, max_chars):
                chunks.append({"text": c, "source": source, "heading": heading})

    return chunks
