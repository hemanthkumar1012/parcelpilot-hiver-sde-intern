from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    openai_api_key: str | None = None
    model: str = 'gpt-5.6-luna'
    top_k: int = 5
    data_dir: Path = ROOT / 'data'
    knowledge_dir: Path = ROOT / 'knowledge_base'


settings = Settings()
