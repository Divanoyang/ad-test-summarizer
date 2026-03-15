"""基于 SKILL.md 的 LLM 问题总结引擎。"""

import logging
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


async def summarize(raw_text: str, model: str | None = None) -> str:
    """调用 LLM 对测试问题文本进行聚类归纳总结，返回 Markdown 格式文本。"""
    client = _get_client()
    system_prompt = _load_system_prompt()
    use_model = model or settings.LLM_MODEL

    response = await client.chat.completions.create(
        model=use_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.3,
        max_tokens=8192,
    )
    return response.choices[0].message.content.strip()
