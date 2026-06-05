from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from src.agents.fact_extractor import extract_fact_card_from_answer
from src.agents.jd_analyzer import analyze_jd_fallback
from src.agents.resume_parser import parse_resume_text_fallback
from src.deepseek_client import DeepSeekClient
from src.schemas import FactCard, JDAnalysis, MasterResume
from src.utils.token_logger import TokenLog

T = TypeVar("T", bound=BaseModel)


PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def parse_resume_with_deepseek(text: str, client: DeepSeekClient) -> tuple[MasterResume, TokenLog | None, str | None]:
    prompt = _prompt("resume_parser.md")
    result = client.json_chat(
        prompt,
        json.dumps({"resume_text": text}, ensure_ascii=False),
        prompt_name="resume_parser",
    )
    return _parse_or_fallback(result.data, MasterResume, result.token_log, lambda: parse_resume_text_fallback(text))


def analyze_jd_with_deepseek(text: str, client: DeepSeekClient) -> tuple[JDAnalysis, TokenLog | None, str | None]:
    prompt = _prompt("jd_analyzer.md")
    result = client.json_chat(
        prompt,
        json.dumps({"jd_text": text}, ensure_ascii=False),
        prompt_name="jd_analyzer",
    )
    return _parse_or_fallback(result.data, JDAnalysis, result.token_log, lambda: analyze_jd_fallback(text))


def extract_fact_with_deepseek(
    answer: str,
    *,
    fact_id: str,
    related_requirement: str,
    related_experience: str,
    client: DeepSeekClient,
) -> tuple[FactCard, TokenLog | None, str | None]:
    prompt = _prompt("fact_extractor.md")
    payload = {
        "fact_id": fact_id,
        "answer": answer,
        "related_requirement": related_requirement,
        "related_experience": related_experience,
    }
    result = client.json_chat(
        prompt,
        json.dumps(payload, ensure_ascii=False),
        prompt_name="fact_extractor",
    )
    fallback = lambda: extract_fact_card_from_answer(
        answer,
        fact_id=fact_id,
        related_requirement=related_requirement,
        related_experience=related_experience,
    )
    return _parse_or_fallback(result.data, FactCard, result.token_log, fallback)


def _parse_or_fallback(
    data: dict | None,
    schema: type[T],
    token_log: TokenLog | None,
    fallback,
) -> tuple[T, TokenLog | None, str | None]:
    try:
        if data is None:
            raise ValueError("DeepSeek returned empty JSON.")
        return schema.model_validate(data), token_log, None
    except (ValidationError, ValueError, TypeError) as exc:
        return fallback(), token_log, f"LLM JSON did not match schema; used local fallback. Details: {exc}"


def _prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")
