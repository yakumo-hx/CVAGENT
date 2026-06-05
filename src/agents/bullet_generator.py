from __future__ import annotations

from src.i18n import DEFAULT_LANG, t
from src.schemas import FactCard, ResumeBullet


def generate_bullet_variants(
    facts: list[FactCard],
    *,
    requirement: str,
    lang: str = DEFAULT_LANG,
) -> list[ResumeBullet]:
    confirmed = [fact for fact in facts if fact.can_use_in_resume and not fact.needs_confirmation]
    if not confirmed:
        return [
            ResumeBullet(
                variant="placeholder",
                text=t("writer.placeholder", lang, requirement=requirement),
                fact_ids=[],
                related_jd_requirements=[requirement],
                risk=t("writer.placeholder_risk", lang),
                gap_suggestions=[t("writer.placeholder_gap", lang)],
            )
        ]

    fact = confirmed[0]
    tools = _join_terms(fact.tools, lang) if fact.tools else t("writer.placeholder_tools", lang)
    metric_text = _metric_text(fact, lang)
    role = _safe_role(fact.role, lang)

    conservative = ResumeBullet(
        variant="conservative",
        text=t("writer.bullet.conservative", lang, role=role, claim=fact.claim, tools=tools, metric_text=metric_text),
        fact_ids=[fact.fact_id],
        related_jd_requirements=fact.related_jd_requirements,
        risk=fact.risk,
    )
    standard = ResumeBullet(
        variant="standard",
        text=t(
            "writer.bullet.standard",
            lang,
            requirement=requirement,
            role=role,
            claim=fact.claim,
            metric_text=metric_text,
        ),
        fact_ids=[fact.fact_id],
        related_jd_requirements=fact.related_jd_requirements,
        risk=fact.risk,
    )
    jd_strong = ResumeBullet(
        variant="jd_strong",
        text=t(
            "writer.bullet.jd_strong",
            lang,
            tools=tools,
            requirement=requirement,
            role=role,
            claim=fact.claim,
            metric_text=metric_text,
        ),
        fact_ids=[fact.fact_id],
        related_jd_requirements=fact.related_jd_requirements,
        risk=fact.risk,
    )
    return [conservative, standard, jd_strong]


def _metric_text(fact: FactCard, lang: str) -> str:
    provided = [metric.value for metric in fact.metrics if metric.value and metric.status == "provided"]
    if not provided:
        return t("writer.placeholder_metric", lang)
    return t("writer.metric_prefix", lang, metrics=_join_terms(provided, lang))


def _safe_role(role: str, lang: str) -> str:
    if lang == "en":
        if role in {"主导", "负责人", "独立负责", "lead", "owner"}:
            return "Led "
        if role in {"负责", "实现", "设计", "owned", "responsible"}:
            return "Owned "
        return "Contributed to "
    if role in {"主导", "负责人", "独立负责"}:
        return "主导"
    if role in {"负责", "实现", "设计"}:
        return "负责"
    if role == "参与":
        return "参与"
    return "参与"


def _join_terms(values: list[str], lang: str) -> str:
    return ", ".join(values) if lang == "en" else "、".join(values)
