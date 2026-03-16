"""基于 SKILL.md 的 LLM 问题总结引擎。"""

import logging
from collections.abc import AsyncIterator
from pathlib import Path

from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)

_SKILL_PATH = Path(__file__).parent / "SKILL.md"
_SYSTEM_PROMPT: str | None = None


def _load_system_prompt() -> str:
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is None:
        raw = _SKILL_PATH.read_text(encoding="utf-8")
        front_matter_end = raw.find("---", raw.find("---") + 3)
        if front_matter_end != -1:
            raw = raw[front_matter_end + 3:].strip()
        _SYSTEM_PROMPT = raw
    return _SYSTEM_PROMPT


_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
        )
    return _client


def _build_messages(raw_text: str) -> list[dict]:
    system_prompt = _load_system_prompt()
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": raw_text},
    ]


async def summarize(raw_text: str, model: str | None = None) -> str:
    """非流式：等待完整响应后返回。"""
    client = _get_client()
    use_model = model or settings.LLM_MODEL
    response = await client.chat.completions.create(
        model=use_model,
        messages=_build_messages(raw_text),
        temperature=0,
        max_tokens=16384,
    )
    return response.choices[0].message.content.strip()


async def summarize_stream(raw_text: str, model: str | None = None) -> AsyncIterator[str]:
    """流式：逐 chunk 返回文本片段。"""
    client = _get_client()
    use_model = model or settings.LLM_MODEL
    stream = await client.chat.completions.create(
        model=use_model,
        messages=_build_messages(raw_text),
        temperature=0,
        max_tokens=16384,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content
