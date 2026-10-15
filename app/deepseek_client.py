"""DeepSeek API 客户端（OpenAI 兼容的 chat/completions 端点）。

参考文档：https://api-docs.deepseek.com/
- Base URL: https://api.deepseek.com
- 端点: POST /chat/completions
- 认证: Authorization: Bearer <API_KEY>
- 模型: deepseek-v4-flash（默认）/ deepseek-v4-pro
"""
import httpx

from .config import settings


class DeepSeekError(Exception):
    """DeepSeek 调用失败。"""


class DeepSeekClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        temperature: float | None = None,
    ):
        self.base_url = (base_url or settings.deepseek_base_url).rstrip("/")
        self.api_key = api_key or settings.deepseek_api_key
        self.model = model or settings.deepseek_model
        self.temperature = settings.deepseek_temperature if temperature is None else temperature
        self._client = httpx.Client(timeout=timeout or settings.deepseek_timeout)

    def chat(self, messages: list[dict]) -> str:
        """发送对话消息，返回助手回复文本。"""
        if not self.api_key:
            raise DeepSeekError("未配置 DEEPSEEK_API_KEY，请在 .env 中设置")

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = self._client.post(url, json=payload, headers=headers)
        except httpx.TimeoutException as e:
            raise DeepSeekError(f"请求超时（>{self._client.timeout}s）：{e}") from e
        except httpx.HTTPError as e:
            raise DeepSeekError(f"网络错误：{e}") from e

        if resp.status_code != 200:
            raise DeepSeekError(f"DeepSeek API 返回 {resp.status_code}: {resp.text[:500]}")

        try:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as e:
            raise DeepSeekError(f"解析响应失败：{resp.text[:500]}") from e

    def close(self) -> None:
        self._client.close()
