from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class TokenLog:
    prompt_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    created_at: str = datetime.now(timezone.utc).isoformat()


class TokenLogger:
    def __init__(self) -> None:
        self.rows: list[TokenLog] = []

    def add(self, row: TokenLog) -> None:
        self.rows.append(row)

    def total_cost(self) -> float:
        return sum(row.estimated_cost_usd for row in self.rows)
