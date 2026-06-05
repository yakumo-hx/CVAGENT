from __future__ import annotations

import json

from src.security import redact_secrets
from src.schemas import ExportBundle, FactCard, JDAnalysis, MatrixRow, ResumeBullet


def build_export_bundle(
    *,
    bullets: list[ResumeBullet],
    facts: list[FactCard],
    jd: JDAnalysis | None,
    matrix_rows: list[MatrixRow],
) -> ExportBundle:
    return ExportBundle(
        tailored_resume_md=redact_secrets(_resume_md(bullets)),
        evidence_cards_json=redact_secrets(
            json.dumps([fact.model_dump() for fact in facts], ensure_ascii=False, indent=2)
        ),
        jd_analysis_json=redact_secrets(jd.model_dump_json(indent=2) if jd else "{}"),
        gap_report_md=redact_secrets(_gap_report(matrix_rows)),
        interview_prep_md=redact_secrets(_interview_prep(bullets)),
    )


def _resume_md(bullets: list[ResumeBullet]) -> str:
    lines = ["# Tailored Resume Bullets", ""]
    for bullet in bullets:
        if bullet.variant == "placeholder":
            continue
        lines.append(f"- {bullet.text}")
        lines.append(f"  - fact_ids: {', '.join(bullet.fact_ids)}")
    return "\n".join(lines).strip() + "\n"


def _gap_report(rows: list[MatrixRow]) -> str:
    lines = ["# Evidence Gap Report", ""]
    for row in rows:
        lines.append(f"## {row.requirement_text}")
        lines.append(f"- status: {row.score.status}")
        lines.append(f"- score: {row.score.total}")
        lines.append(f"- gap: {row.gap}")
        lines.append(f"- next question: {row.next_question}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _interview_prep(bullets: list[ResumeBullet]) -> str:
    lines = ["# Interview Prep", ""]
    for bullet in bullets:
        if bullet.variant != "placeholder":
            lines.append(f"- 面试官可能追问：请解释这条经历的角色、工具、过程和结果。")
            lines.append(f"  - bullet: {bullet.text}")
    return "\n".join(lines).strip() + "\n"
