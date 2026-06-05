from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TokenLog:
    prompt_name: str
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TokenLogger:
    def __init__(self) -> None:
        self.rows: list[TokenLog] = []

    def add(self, row: TokenLog) -> None:
        self.rows.append(row)

    def extend(self, rows: list[TokenLog]) -> None:
        self.rows.extend(rows)

    def total_input_tokens(self) -> int:
        return sum(row.input_tokens for row in self.rows)

    def total_output_tokens(self) -> int:
        return sum(row.output_tokens for row in self.rows)

    def total_tokens(self) -> int:
        return sum(row.total_tokens for row in self.rows)

    def total_cost(self) -> float:
        return sum(row.estimated_cost_usd for row in self.rows)
