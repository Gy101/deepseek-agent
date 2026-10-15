"""应用配置：从环境变量 / .env 文件读取。"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（app/config.py 的上两级）
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # DeepSeek API
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_temperature: float = 0.7
    deepseek_timeout: float = 60.0

    # RAG 检索
    top_k: int = 3
    score_threshold: float = 0.0
    knowledge_dir: str = "data/knowledge"

    # 服务
    host: str = "127.0.0.1"
    port: int = 8000


settings = Settings()
