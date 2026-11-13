import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ai_provider: str
    ai_api_key: str
    ai_model: str
    port: int
    free_daily_credits: int
    database_path: str


def _clean(value: str) -> str:
    return value.strip() if value else ""


def load_settings() -> Settings:
    provider = _clean(os.getenv("AI_PROVIDER", "mock")).lower()
    if provider not in {"mock", "mistral", "openai"}:
        provider = "mock"
    key = _clean(os.getenv("AI_API_KEY", ""))
    if provider in {"mistral", "openai"} and not key:
        provider = "mock"
    model = _clean(os.getenv("AI_MODEL", ""))
    if not model:
        model = {"mistral": "mistral-small-latest", "openai": "gpt-4o-mini"}.get(provider, "")
    return Settings(
        ai_provider=provider,
        ai_api_key=key,
        ai_model=model,
        port=int(_clean(os.getenv("PORT", "8000")) or 8000),
        free_daily_credits=int(_clean(os.getenv("FREE_DAILY_CREDITS", "5")) or 5),
        database_path=_clean(os.getenv("DATABASE_PATH", "toolkit.db")) or "toolkit.db",
    )


settings = load_settings()
