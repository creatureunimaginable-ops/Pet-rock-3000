import re

import httpx

from app.config import settings

TOOLS = {
    "summarize": {
        "label": "Summarize",
        "options": {
            "length": ["short", "medium", "detailed"],
        },
    },
    "rewrite": {
        "label": "Rewrite",
        "options": {
            "tone": ["professional", "casual", "friendly", "persuasive"],
        },
    },
    "captions": {
        "label": "Captions",
        "options": {
            "platform": ["instagram", "twitter", "linkedin"],
        },
    },
}


class AIError(Exception):
    pass


def build_prompt(tool: str, text: str, options: dict) -> str:
    if tool == "summarize":
        length = options.get("length", "short")
        guidance = {
            "short": "in 1-2 sentences",
            "medium": "in 3-5 sentences",
            "detailed": "in one thorough paragraph plus 3 key bullet points",
        }[length]
        return f"Summarize the following text {guidance}. Reply with only the summary.\n\n{text}"
    if tool == "rewrite":
        tone = options.get("tone", "professional")
        return (
            f"Rewrite the following text in a {tone} tone. Preserve the meaning and "
            f"roughly the same length. Reply with only the rewritten text.\n\n{text}"
        )
    if tool == "captions":
        platform = options.get("platform", "instagram")
        return (
            f"Write 3 catchy social media captions for {platform} based on the following "
            f"content. Number them 1-3 and include relevant hashtags. Reply with only the captions.\n\n{text}"
        )
    raise AIError(f"Unknown tool: {tool}")


class MockProvider:
    def generate(self, tool: str, text: str, options: dict) -> str:
        if tool == "summarize":
            length = options.get("length", "short")
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
            if length == "short":
                body = " ".join(sentences[:2])
            elif length == "medium":
                body = " ".join(sentences[:5])
            else:
                body = text.strip()
            return f"[demo] {body}"
        if tool == "rewrite":
            tone = options.get("tone", "professional")
            openers = {
                "professional": "To summarize formally, ",
                "casual": "So basically, ",
                "friendly": "Here's the nice part: ",
                "persuasive": "Consider this: ",
            }
            return f"[demo] {openers[tone]}{text.strip()}"
        if tool == "captions":
            platform = options.get("platform", "instagram")
            snippet = text.strip()[:60]
            tags = {"instagram": "#instagood #trending", "twitter": "#buildinpublic", "linkedin": "#growth #careers"}
            return (
                f"[demo] 1. {snippet} \u2014 you won't believe what happens next. {tags[platform]}\n"
                f"2. Big things start with small steps: {snippet}. {tags[platform]}\n"
                f"3. POV: you just discovered {snippet}. {tags[platform]}"
            )
        raise AIError(f"Unknown tool: {tool}")


class OpenAICompatibleProvider:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def generate(self, tool: str, text: str, options: dict) -> str:
        prompt = build_prompt(tool, text, options)
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            raise AIError(f"AI request failed: {exc}") from exc
        if not isinstance(content, str) or not content.strip():
            raise AIError("AI returned an empty response")
        return content.strip()


class MistralProvider(OpenAICompatibleProvider):
    def __init__(self, api_key: str, model: str) -> None:
        super().__init__("https://api.mistral.ai/v1", api_key, model)


def get_provider():
    if settings.ai_provider == "mistral":
        return MistralProvider(settings.ai_api_key, settings.ai_model)
    if settings.ai_provider == "openai":
        return OpenAICompatibleProvider("https://api.openai.com/v1", settings.ai_api_key, settings.ai_model)
    return MockProvider()
