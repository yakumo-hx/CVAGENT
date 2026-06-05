from __future__ import annotations

import re

from src.schemas import JDAnalysis, JDRequirement


def analyze_jd_fallback(text: str) -> JDAnalysis:
    """Heuristic JD parser used as a local fallback."""

    lines = [line.strip("- •\t ") for line in text.splitlines() if line.strip()]
    requirements: list[JDRequirement] = []

    for index, line in enumerate(lines[:20], start=1):
        category = "must_have"
        if any(token in line for token in ("加分", "优先", "nice", "plus")):
            category = "nice_to_have"
        elif any(token in line for token in ("负责", "工作内容", "职责")):
            category = "responsibility"
        requirements.append(
            JDRequirement(
                id=f"req_{index:03d}",
                text=line,
                category=category,  # type: ignore[arg-type]
                keywords=_extract_keywords(line),
                evidence_needed=_evidence_needed(line),
            )
        )

    return JDAnalysis(
        job_title=_guess_title(lines),
        must_have_requirements=[item for item in requirements if item.category == "must_have"],
        nice_to_have_requirements=[item for item in requirements if item.category == "nice_to_have"],
        responsibilities=[item for item in requirements if item.category == "responsibility"],
        hidden_expectations=[],
        keywords=sorted({kw for item in requirements for kw in item.keywords}),
        interview_risks=["需要能解释简历中每条强匹配 bullet 的事实来源"],
    )


def flatten_requirements(jd: JDAnalysis) -> list[JDRequirement]:
    return (
        jd.must_have_requirements
        + jd.nice_to_have_requirements
        + jd.responsibilities
        + jd.hidden_expectations
    )


def _guess_title(lines: list[str]) -> str:
    for line in lines[:5]:
        if any(token in line.lower() for token in ("engineer", "agent", "开发", "产品", "运营")):
            return line[:60]
    return ""


def _extract_keywords(text: str) -> list[str]:
    known = [
        "Python",
        "SQL",
        "DeepSeek",
        "LLM",
        "Agent",
        "Prompt",
        "React",
        "Streamlit",
        "FastAPI",
        "日志",
        "评估",
        "成本",
        "状态管理",
        "工作流",
    ]
    found = [kw for kw in known if kw.lower() in text.lower()]
    found.extend(re.findall(r"[A-Za-z][A-Za-z0-9_+#.-]{2,}", text))
    return sorted(set(found))


def _evidence_needed(text: str) -> list[str]:
    needs = ["具体角色", "实际动作"]
    if any(token in text for token in ("指标", "增长", "提升", "优化", "成本", "效率")):
        needs.append("结果指标")
    if any(token in text for token in ("Agent", "工作流", "系统", "平台", "开发")):
        needs.extend(["技术栈", "架构细节"])
    return needs
