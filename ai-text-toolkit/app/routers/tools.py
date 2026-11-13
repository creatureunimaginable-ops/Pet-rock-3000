from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.provider import TOOLS, AIError, get_provider
from app.config import settings
from app.database import get_history, get_usage_count, record_usage, save_history

router = APIRouter(prefix="/api")

MAX_INPUT_CHARS = 8000


class ToolRequest(BaseModel):
    client_id: str = Field(min_length=8, max_length=64)
    text: str = Field(min_length=1, max_length=MAX_INPUT_CHARS)
    options: dict = Field(default_factory=dict)


class ToolResponse(BaseModel):
    tool: str
    result: str
    credits_remaining: int


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _credits_remaining(client_id: str) -> int:
    return max(0, settings.free_daily_credits - get_usage_count(client_id, _today()))


@router.get("/tools")
def list_tools() -> dict:
    return {
        "tools": [
            {"id": tool_id, "label": meta["label"], "options": meta["options"]}
            for tool_id, meta in TOOLS.items()
        ],
        "demo_mode": settings.ai_provider == "mock",
        "free_daily_credits": settings.free_daily_credits,
        "max_input_chars": MAX_INPUT_CHARS,
    }


@router.get("/credits/{client_id}")
def credits(client_id: str) -> dict:
    return {"credits_remaining": _credits_remaining(client_id), "free_daily_credits": settings.free_daily_credits}


@router.post("/tools/{tool}", response_model=ToolResponse)
def run_tool(tool: str, request: ToolRequest) -> ToolResponse:
    if tool not in TOOLS:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool}")
    if _credits_remaining(request.client_id) <= 0:
        raise HTTPException(status_code=429, detail="Daily free credits used up. Come back tomorrow!")
    try:
        result = get_provider().generate(tool, request.text, request.options)
    except AIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    now = datetime.now(timezone.utc).isoformat()
    save_history(request.client_id, tool, request.text, result, now)
    used = record_usage(request.client_id, _today())
    return ToolResponse(
        tool=tool,
        result=result,
        credits_remaining=max(0, settings.free_daily_credits - used),
    )


@router.get("/history/{client_id}")
def history(client_id: str) -> dict:
    return {"items": get_history(client_id)}
