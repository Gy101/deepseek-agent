"""对话编排：检索知识库 → 组装 Prompt → 调用 DeepSeek。"""
from .config import settings
from .deepseek_client import DeepSeekClient
from .rag.retriever import retrieve

SYSTEM_PROMPT = (
    "你是一个知识库问答助手。请严格依据用户消息中提供的【参考资料】回答问题。\n"
    "规则：\n"
    "1. 只使用【参考资料】中的信息作答，不要编造或使用外部知识。\n"
    "2. 如果参考资料不足以回答，请明确说明「根据现有知识库，我无法回答该问题」，"
    "并简要指出缺少什么信息。\n"
    "3. 回答时在相应句末用 [1][2] 标注所引用的资料编号。\n"
    "4. 回答简洁、准确、有条理。"
)


def _build_context(sources: list[dict]) -> str:
    parts = []
    for s in sources:
        heading = f"（章节：{s['heading']}）" if s.get("heading") else ""
        parts.append(f"[{s['index']}] 来源：{s['source']}{heading}\n{s['text']}")
    return "\n\n".join(parts)


class Agent:
    def __init__(self, store, client: DeepSeekClient | None = None):
        self.store = store
        self.client = client or DeepSeekClient()

    def chat(self, message: str, history: list[dict] | None = None) -> dict:
        history = history or []

        sources = retrieve(
            self.store,
            message,
            top_k=settings.top_k,
            threshold=settings.score_threshold,
        )
        context = _build_context(sources)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        if context:
            user_content = f"【参考资料】\n{context}\n\n【用户问题】\n{message}"
        else:
            user_content = f"【用户问题】\n{message}"
        messages.append({"role": "user", "content": user_content})

        reply = self.client.chat(messages)
        return {
            "reply": reply,
            "sources": [
                {
                    "index": s["index"],
                    "source": s["source"],
                    "score": s["score"],
                    "snippet": s["snippet"],
                }
                for s in sources
            ],
            "model": self.client.model,
        }
