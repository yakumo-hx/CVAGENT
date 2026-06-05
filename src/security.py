from __future__ import annotations

import re


SECRET_PATTERNS = [
    re.compile(r"ds-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"DEEPSEEK_API_KEY\s*=\s*[^\s]+", re.IGNORECASE),
    re.compile(r"Authorization:\s*Bearer\s+[^\s]+", re.IGNORECASE),
]


def mask_secret(value: str, *, visible_prefix: int = 6, visible_suffix: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= visible_prefix + visible_suffix:
        return "*" * len(value)
    return f"{value[:visible_prefix]}{'*' * 8}{value[-visible_suffix:]}"


def redact_secrets(text: str) -> str:
    redacted = text or ""
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def contains_secret(text: str) -> bool:
    return any(pattern.search(text or "") for pattern in SECRET_PATTERNS)
