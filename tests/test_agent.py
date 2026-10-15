from app.agent import Agent
from app.rag.store import KnowledgeStore


class FakeClient:
    model = "deepseek-v4-flash"

    def __init__(self):
        self.calls: list[list[dict]] = []

    def chat(self, messages):
        self.calls.append(messages)
        return "这是模拟回答 [1]"


def _make_store(tmp_path):
    (tmp_path / "kb.md").write_text("# 退款\n购买后 7 天内可申请全额退款。\n", encoding="utf-8")
    store = KnowledgeStore(str(tmp_path))
    store.build()
    return store


def test_agent_injects_context_and_returns_sources(tmp_path):
    store = _make_store(tmp_path)
    client = FakeClient()
    agent = Agent(store, client)

    result = agent.chat("如何退款？", [])
    assert result["reply"] == "这是模拟回答 [1]"
    assert result["model"] == "deepseek-v4-flash"
    assert len(result["sources"]) == 1

    user_msg = client.calls[0][-1]["content"]
    assert "【参考资料】" in user_msg
    assert "【用户问题】" in user_msg
    assert "退款" in user_msg


def test_agent_keeps_history(tmp_path):
    store = _make_store(tmp_path)
    client = FakeClient()
    agent = Agent(store, client)

    agent.chat("你好", [{"role": "user", "content": "之前的问题"}])
    messages = client.calls[0]
    assert messages[1] == {"role": "user", "content": "之前的问题"}


def test_agent_no_context_when_store_empty(tmp_path):
    store = KnowledgeStore(str(tmp_path))
    store.build()  # 空目录
    client = FakeClient()
    agent = Agent(store, client)

    result = agent.chat("随便问问", [])
    assert result["sources"] == []
    user_msg = client.calls[0][-1]["content"]
    assert "【参考资料】" not in user_msg
