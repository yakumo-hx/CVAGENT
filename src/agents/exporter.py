from __future__ import annotations

import json

from src.agents.evidence_matcher import gap_text, next_question, status_label
from src.i18n import DEFAULT_LANG, t
from src.security import redact_secrets
from src.schemas import ExportBundle, FactCard, JDAnalysis, MatrixRow, ResumeBullet


def build_export_bundle(
    *,
    bullets: list[ResumeBullet],
    facts: list[FactCard],
    jd: JDAnalysis | None,
    matrix_rows: list[MatrixRow],
    lang: str = DEFAULT_LANG,
) -> ExportBundle:
    return ExportBundle(
        tailored_resume_md=redact_secrets(_resume_md(bullets, lang)),
        evidence_cards_json=redact_secrets(
            json.dumps([fact.model_dump() for fact in facts], ensure_ascii=False, indent=2)
        ),
        jd_analysis_json=redact_secrets(jd.model_dump_json(indent=2) if jd else "{}"),
        gap_report_md=redact_secrets(_gap_report(matrix_rows, lang)),
        interview_prep_md=redact_secrets(_interview_prep(bullets, lang)),
    )


def _resume_md(bullets: list[ResumeBullet], lang: str) -> str:
    lines = [f"# {t('export.resume_title', lang)}", ""]
    for bullet in bullets:
        if bullet.variant == "placeholder":
            continue
        lines.append(f"- {bullet.text}")
        lines.append(f"  - {t('writer.fact_ids', lang)}: {', '.join(bullet.fact_ids)}")
    return "\n".join(lines).strip() + "\n"


def _gap_report(rows: list[MatrixRow], lang: str) -> str:
    lines = [f"# {t('export.gap_title', lang)}", ""]
    for row in rows:
        lines.append(f"## {row.requirement_text}")
        lines.append(f"- {t('export.status', lang)}: {status_label(row.score.status, lang)}")
        lines.append(f"- {t('export.score', lang)}: {row.score.total}")
        lines.append(f"- {t('export.gap', lang)}: {gap_text(row.score.status, lang)}")
        lines.append(
            f"- {t('export.next_question', lang)}: "
            f"{next_question(row.requirement_text, row.best_evidence_summary, row.score.status, lang)}"
        )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _interview_prep(bullets: list[ResumeBullet], lang: str) -> str:
    lines = [f"# {t('export.interview_title', lang)}", ""]
    for bullet in bullets:
        if bullet.variant != "placeholder":
            lines.append(f"- {t('export.interview_question', lang)}")
            lines.append(f"  - {t('export.bullet', lang)}: {bullet.text}")
    return "\n".join(lines).strip() + "\n"
