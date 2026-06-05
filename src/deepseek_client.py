from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from openai import OpenAI

from src.config import DEEPSEEK_BASE_URL, DEFAULT_MODEL
from src.security import redact_secrets
from src.utils.token_logger import TokenLog


@dataclass
class DeepSeekResult:
    content: str
    data: dict[str, Any] | None
    token_log: TokenLog


class DeepSeekClient:
    """Small wrapper around DeepSeek's OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        if not api_key:
            raise ValueError("DeepSeek API key is required.")
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    def guidance_message(self) -> DeepSeekResult:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是 Resume Evidence Agent 的引导助手。"
                        "只返回一句简短中文，引导用户粘贴简历和目标 JD。"
                    ),
                },
                {"role": "user", "content": "请给用户一句开场引导。"},
            ],
            temperature=0,
            max_tokens=80,
        )
        content = response.choices[0].message.content or ""
        return DeepSeekResult(
            content=redact_secrets(content),
            data=None,
            token_log=_token_log_from_response("settings.guidance_message", self.model, response),
        )

    def test_connection(self) -> str:
        return self.guidance_message().content

    def json_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        prompt_name: str = "json_chat",
        temperature: float = 0.2,
    ) -> DeepSeekResult:
        safe_system = redact_secrets(system_prompt)
        safe_user = redact_secrets(user_prompt)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": safe_system},
                {"role": "user", "content": safe_user},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = redact_secrets(response.choices[0].message.content or "{}")
        return DeepSeekResult(
            content=content,
            data=json.loads(content),
            token_log=_token_log_from_response(prompt_name, self.model, response),
        )


def _token_log_from_response(prompt_name: str, model: str, response: Any) -> TokenLog:
    usage = getattr(response, "usage", None)
    input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", input_tokens + output_tokens) or 0)
    return TokenLog(
        prompt_name=prompt_name,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
    )
