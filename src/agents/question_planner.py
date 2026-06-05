from __future__ import annotations

from src.schemas import MatrixRow


BRANCHING_OPTIONS = ("YES", "INDIRECT", "ADJACENT", "PERSONAL_LEARNING", "NO")


def pick_next_gap(rows: list[MatrixRow]) -> MatrixRow | None:
    priority = {"GAP": 0, "WEAK": 1, "ADJACENT": 2, "TRANSFERABLE": 3, "DIRECT": 4}
    candidates = [row for row in rows if row.score.status in {"GAP", "WEAK", "ADJACENT"}]
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: priority[row.score.status])[0]


def plan_question(row: MatrixRow) -> dict[str, str]:
    return {
        "requirement_id": row.requirement_id,
        "requirement": row.requirement_text,
        "question": row.next_question,
        "why": "这能判断该 JD 要求是否有真实经历支撑，而不是只做关键词改写。",
        "branch_hint": "如果有直接经历，请说明角色、动作、工具、规模、结果；如果没有，说明相邻经历或选择跳过。",
    }


def followup_for_branch(branch: str, requirement: str) -> str:
    branch = branch.upper()
    if branch == "YES":
        return f"请补充你围绕「{requirement}」做过的具体动作、使用工具、规模和结果。"
    if branch == "INDIRECT":
        return f"你虽然没有直接负责「{requirement}」，但你和相关工作如何协作、评审或交付？"
    if branch == "ADJACENT":
        return f"有没有相邻技术、相邻业务或相似问题可以迁移证明「{requirement}」？"
    if branch == "PERSONAL_LEARNING":
        return f"是否有课程、自学、个人项目、GitHub demo 可以作为「{requirement}」的入门证据？"
    return "如果确实没有相关证据，这条要求会保留为缺口，不会写进正式简历。"
