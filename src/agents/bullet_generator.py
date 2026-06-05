from __future__ import annotations

from src.schemas import FactCard, ResumeBullet


def generate_bullet_variants(
    facts: list[FactCard],
    *,
    requirement: str,
) -> list[ResumeBullet]:
    confirmed = [fact for fact in facts if fact.can_use_in_resume and not fact.needs_confirmation]
    if not confirmed:
        return [
            ResumeBullet(
                variant="placeholder",
                text=f"[待补充] 目前没有已确认事实卡可支撑「{requirement}」。",
                fact_ids=[],
                related_jd_requirements=[requirement],
                risk="缺少已确认事实，不能生成正式简历 bullet",
                gap_suggestions=["继续追问角色、工具、规模、结果和可验证材料"],
            )
        ]

    fact = confirmed[0]
    tools = "、".join(fact.tools) if fact.tools else "[待补充工具]"
    metric_text = _metric_text(fact)
    role = _safe_role(fact.role)

    conservative = ResumeBullet(
        variant="conservative",
        text=f"{role}{fact.claim}，使用 {tools} 完成相关工作{metric_text}。",
        fact_ids=[fact.fact_id],
        related_jd_requirements=fact.related_jd_requirements,
        risk=fact.risk,
    )
    standard = ResumeBullet(
        variant="standard",
        text=f"围绕「{requirement}」，{role}{fact.claim}，沉淀为可面试解释的项目证据{metric_text}。",
        fact_ids=[fact.fact_id],
        related_jd_requirements=fact.related_jd_requirements,
        risk=fact.risk,
    )
    jd_strong = ResumeBullet(
        variant="jd_strong",
        text=f"基于 {tools} 支撑「{requirement}」相关场景，{role}{fact.claim}{metric_text}。",
        fact_ids=[fact.fact_id],
        related_jd_requirements=fact.related_jd_requirements,
        risk=fact.risk,
    )
    return [conservative, standard, jd_strong]


def _metric_text(fact: FactCard) -> str:
    provided = [metric.value for metric in fact.metrics if metric.value and metric.status == "provided"]
    if not provided:
        return "，[待补充结果/指标]"
    return "，涉及 " + "、".join(provided)


def _safe_role(role: str) -> str:
    if role in {"主导", "负责人", "独立负责"}:
        return "主导"
    if role in {"负责", "实现", "设计"}:
        return "负责"
    if role == "参与":
        return "参与"
    return "参与"
