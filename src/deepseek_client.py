from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from src.config import DEEPSEEK_BASE_URL, DEFAULT_MODEL


class DeepSeekClient:
    """Small wrapper around DeepSeek's OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        if not api_key:
            raise ValueError("DeepSeek API key is required.")
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    def test_connection(self) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Reply with the single word ok."},
                {"role": "user", "content": "Connection test"},
            ],
            temperature=0,
            max_tokens=8,
        )
        return response.choices[0].message.content or ""

    def json_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
