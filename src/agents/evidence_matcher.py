from __future__ import annotations

from src.agents.jd_analyzer import flatten_requirements
from src.i18n import DEFAULT_LANG, t
from src.schemas import JDAnalysis, MatchScore, MatrixRow, MasterResume, ResumeItem


def build_evidence_matrix(resume: MasterResume, jd: JDAnalysis, lang: str = DEFAULT_LANG) -> list[MatrixRow]:
    rows: list[MatrixRow] = []
    evidence_items = resume.projects + resume.experiences

    for requirement in flatten_requirements(jd):
        best_item, score = _best_match(requirement.text, evidence_items)
        rows.append(
            MatrixRow(
                requirement_id=requirement.id,
                requirement_text=requirement.text,
                best_evidence_id=best_item.id if best_item else None,
                best_evidence_summary=best_item.description if best_item else "",
                score=score,
                gap=gap_text(score.status, lang),
                next_question=next_question(requirement.text, best_item.title if best_item else "", score.status, lang),
            )
        )
    return rows


def status_label(status: str, lang: str = DEFAULT_LANG) -> str:
    return t(f"status.{status.lower()}", lang)


def gap_text(status: str, lang: str = DEFAULT_LANG) -> str:
    return t(f"matrix.gap.{status.lower()}", lang)


def next_question(requirement: str, evidence_label: str = "", status: str = "", lang: str = DEFAULT_LANG) -> str:
    if status in {"DIRECT", "TRANSFERABLE"}:
        return t("matrix.next.strong", lang)
    if evidence_label:
        return t("matrix.next.related", lang, requirement=requirement)
    return t("matrix.next.missing", lang, requirement=requirement)


def score_requirement_against_item(requirement: str, item: ResumeItem) -> MatchScore:
    req_tokens = _tokens(requirement)
    item_tokens = _tokens(item.description + " " + " ".join(item.tools + item.keywords))
    overlap = len(req_tokens & item_tokens)
    base = min(100, overlap * 20)

    direct = base
    transferable = min(100, base + (20 if item.tools else 0))
    adjacent = min(100, base + 15)
    impact = 80 if item.metrics or item.outcomes else 30
    total = round(direct * 0.4 + transferable * 0.3 + adjacent * 0.2 + impact * 0.1)

    return MatchScore(
        direct=direct,
        transferable=transferable,
        adjacent=adjacent,
        impact=impact,
        total=total,
        status=_status(total),
    )


def _best_match(requirement: str, items: list[ResumeItem]) -> tuple[ResumeItem | None, MatchScore]:
    if not items:
        return None, MatchScore(direct=0, transferable=0, adjacent=0, impact=0, total=0, status="GAP")

    scored = [(item, score_requirement_against_item(requirement, item)) for item in items]
    scored.sort(key=lambda pair: pair[1].total, reverse=True)
    return scored[0]


def _tokens(text: str) -> set[str]:
    normalized = text.lower().replace("/", " ").replace(",", " ")
    return {part.strip("，。；;:：()（）") for part in normalized.split() if len(part.strip()) >= 2}


def _status(total: int) -> str:
    if total >= 90:
        return "DIRECT"
    if total >= 75:
        return "TRANSFERABLE"
    if total >= 60:
        return "ADJACENT"
    if total >= 45:
        return "WEAK"
    return "GAP"
