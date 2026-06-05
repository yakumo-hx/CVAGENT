from __future__ import annotations

from src.agents.evidence_matcher import next_question
from src.i18n import DEFAULT_LANG, t
from src.schemas import MatrixRow


BRANCHING_OPTIONS = ("YES", "INDIRECT", "ADJACENT", "PERSONAL_LEARNING", "NO")


def pick_next_gap(rows: list[MatrixRow]) -> MatrixRow | None:
    priority = {"GAP": 0, "WEAK": 1, "ADJACENT": 2, "TRANSFERABLE": 3, "DIRECT": 4}
    candidates = [row for row in rows if row.score.status in {"GAP", "WEAK", "ADJACENT"}]
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: priority[row.score.status])[0]


def plan_question(row: MatrixRow, lang: str = DEFAULT_LANG) -> dict[str, str]:
    return {
        "requirement_id": row.requirement_id,
        "requirement": row.requirement_text,
        "question": next_question(row.requirement_text, row.best_evidence_summary, row.score.status, lang),
        "why": t("interview.why_default", lang),
        "branch_hint": t("interview.branch_hint", lang),
    }


def followup_for_branch(branch: str, requirement: str, lang: str = DEFAULT_LANG) -> str:
    branch = branch.upper()
    if branch == "YES":
        return t("interview.branch.yes", lang, requirement=requirement)
    if branch == "INDIRECT":
        return t("interview.branch.indirect", lang, requirement=requirement)
    if branch == "ADJACENT":
        return t("interview.branch.adjacent", lang, requirement=requirement)
    if branch == "PERSONAL_LEARNING":
        return t("interview.branch.learning", lang, requirement=requirement)
    return t("interview.branch.no", lang)
