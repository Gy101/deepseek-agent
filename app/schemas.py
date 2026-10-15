"""请求 / 响应数据模型。"""
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(description="消息角色：user 或 assistant")
    content: str = Field(description="消息内容")


class ChatRequest(BaseModel):
    message: str = Field(description="用户最新一条消息")
    history: list[Message] = Field(default_factory=list, description="多轮对话历史")


class Source(BaseModel):
    index: int = Field(description="引用编号")
    source: str = Field(description="来源文档文件名")
    score: float = Field(description="检索相似度得分")
    snippet: str = Field(description="命中片段摘要")


class ChatResponse(BaseModel):
    reply: str = Field(description="模型回复")
    sources: list[Source] = Field(default_factory=list, description="本次回答引用的知识库来源")
    model: str = Field(description="实际使用的模型名")
