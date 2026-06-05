from __future__ import annotations

import re

from src.i18n import DEFAULT_LANG, t
from src.schemas import FactCard, Metric


def extract_fact_card_from_answer(
    answer: str,
    *,
    fact_id: str,
    related_requirement: str,
    related_experience: str = "",
    lang: str = DEFAULT_LANG,
) -> FactCard:
    tools = _extract_tools(answer)
    metrics = _extract_metrics(answer)
    role = _extract_role(answer)

    return FactCard(
        fact_id=fact_id,
        claim=_first_sentence(answer),
        related_jd_requirements=[related_requirement],
        related_experience=related_experience,
        tools=tools,
        metrics=metrics,
        role=role,
        outcome=_extract_outcome(answer),
        confidence="medium" if len(answer.strip()) >= 20 else "low",
        risk="" if metrics else t("fact.risk.no_metric", lang),
        can_use_in_resume=False,
        needs_confirmation=True,
    )


def _first_sentence(text: str) -> str:
    parts = re.split(r"[。.!！?？\n]", text.strip())
    return parts[0].strip() if parts and parts[0].strip() else text.strip()


def _extract_tools(text: str) -> list[str]:
    known = ["Python", "Streamlit", "FastAPI", "React", "SQL", "DeepSeek", "LLM", "Agent", "SQLite", "Pydantic"]
    return [tool for tool in known if tool.lower() in text.lower()]


def _extract_metrics(text: str) -> list[Metric]:
    values = re.findall(r"\d+(?:\.\d+)?\s*(?:%|人|个|次|轮|条|小时|天|周|月|年|k|K|万)?", text)
    return [Metric(type="mentioned_number", value=value.strip(), status="provided") for value in values]


def _extract_role(text: str) -> str:
    if any(token in text for token in ("主导", "负责人", "独立负责")):
        return "主导"
    if any(token in text for token in ("负责", "实现", "设计")):
        return "负责"
    if "参与" in text:
        return "参与"
    return ""


def _extract_outcome(text: str) -> str:
    for token in ("提升", "降低", "减少", "增加", "完成", "上线", "交付"):
        index = text.find(token)
        if index >= 0:
            return text[index : index + 80]
    return ""
