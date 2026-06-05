from __future__ import annotations

import re

from src.schemas import MasterResume, ResumeItem


def parse_resume_text_fallback(text: str) -> MasterResume:
    """Best-effort parser used before the LLM parser is wired in."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    skills: list[str] = []
    projects: list[ResumeItem] = []
    experiences: list[ResumeItem] = []

    current_section = ""
    item_index = 1

    for line in lines:
        lower = line.lower()
        if any(token in lower for token in ("skill", "技能", "技术栈")):
            current_section = "skills"
            skills.extend(_split_keywords(line))
            continue
        if any(token in lower for token in ("project", "项目")):
            current_section = "projects"
            continue
        if any(token in lower for token in ("experience", "经历", "工作", "实习")):
            current_section = "experiences"
            continue

        if current_section == "skills":
            skills.extend(_split_keywords(line))
        elif current_section == "projects":
            projects.append(_item_from_line("project", item_index, line))
            item_index += 1
        elif current_section == "experiences":
            experiences.append(_item_from_line("experience", item_index, line))
            item_index += 1

    if not projects and not experiences and text.strip():
        projects.append(_item_from_line("project", 1, text.strip()[:300]))

    return MasterResume(
        projects=projects,
        experiences=experiences,
        skills=sorted(set(filter(None, skills))),
        raw_text=text,
    )


def _item_from_line(kind: str, index: int, line: str) -> ResumeItem:
    return ResumeItem(
        id=f"{kind}_{index:03d}",
        title=line[:80],
        description=line,
        tools=_extract_tools(line),
        metrics=[],
        risks=_infer_risks(line),
    )


def _split_keywords(line: str) -> list[str]:
    cleaned = re.sub(r"^[^:：]*[:：]?", "", line)
    return [part.strip(" -;；,，") for part in re.split(r"[,，/、;；]", cleaned) if part.strip()]


def _extract_tools(text: str) -> list[str]:
    known = ["Python", "Streamlit", "FastAPI", "React", "SQL", "DeepSeek", "LLM", "Agent", "Pandas"]
    return [tool for tool in known if tool.lower() in text.lower()]


def _infer_risks(text: str) -> list[str]:
    risks: list[str] = []
    if not re.search(r"\d", text):
        risks.append("缺少规模或指标")
    if "参与" in text and "负责" not in text and "主导" not in text:
        risks.append("角色边界不清")
    return risks
