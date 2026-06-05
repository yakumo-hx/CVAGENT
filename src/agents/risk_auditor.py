from __future__ import annotations

import re

from src.i18n import DEFAULT_LANG, t
from src.schemas import FactCard, ResumeBullet, RiskFinding


NUMBER_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:%|人|个|次|轮|条|小时|天|周|月|年|k|K|万)?")


def audit_bullet(bullet: ResumeBullet, facts: list[FactCard], lang: str = DEFAULT_LANG) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    source_facts = [fact for fact in facts if fact.fact_id in bullet.fact_ids]

    if bullet.variant != "placeholder" and not bullet.fact_ids:
        findings.append(
            RiskFinding(
                code="fact_id_required",
                message=t("risk.fact_id_required", lang),
                severity="high",
            )
        )

    if _has_numbers(bullet.text) and not _facts_have_metrics(source_facts):
        findings.append(
            RiskFinding(
                code="unsupported_metric",
                message=t("risk.unsupported_metric", lang),
                severity="high",
            )
        )

    if "主导" in bullet.text and not _facts_support_lead_role(source_facts):
        findings.append(
            RiskFinding(
                code="role_inflation",
                message=t("risk.role_inflation", lang),
                severity="high",
            )
        )

    return findings


def has_unsupported_metrics(bullet: ResumeBullet, facts: list[FactCard]) -> bool:
    return any(finding.code == "unsupported_metric" for finding in audit_bullet(bullet, facts))


def has_role_inflation(bullet: ResumeBullet, facts: list[FactCard]) -> bool:
    return any(finding.code == "role_inflation" for finding in audit_bullet(bullet, facts))


def _has_numbers(text: str) -> bool:
    return bool(NUMBER_RE.search(text))


def _facts_have_metrics(facts: list[FactCard]) -> bool:
    return any(metric.value and metric.status == "provided" for fact in facts for metric in fact.metrics)


def _facts_support_lead_role(facts: list[FactCard]) -> bool:
    lead_roles = {"主导", "负责人", "独立负责", "lead", "owner"}
    return any(fact.role.lower() in lead_roles for fact in facts)
