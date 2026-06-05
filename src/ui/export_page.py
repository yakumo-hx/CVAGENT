from __future__ import annotations

import streamlit as st

from src.agents.exporter import build_export_bundle
from src.security import contains_secret
from src.ui.components import safe_download
from src.ui.style import hero


def render() -> None:
    hero("Export", "导出 Markdown 简历、证据卡 JSON、JD 分析 JSON、gap report 和面试追问清单。")
    bundle = build_export_bundle(
        bullets=st.session_state.get("bullets", []),
        facts=st.session_state.get("fact_cards", []),
        jd=st.session_state.get("jd_analysis"),
        matrix_rows=st.session_state.get("matrix_rows", []),
    )

    outputs = {
        "tailored_resume.md": bundle.tailored_resume_md,
        "evidence_cards.json": bundle.evidence_cards_json,
        "jd_analysis.json": bundle.jd_analysis_json,
        "gap_report.md": bundle.gap_report_md,
        "interview_prep.md": bundle.interview_prep_md,
    }

    if any(contains_secret(content) for content in outputs.values()):
        st.error("Export contains secret-like text. Downloads are disabled until content is redacted.")
        return

    cols = st.columns(2)
    with cols[0]:
        safe_download("Download tailored_resume.md", bundle.tailored_resume_md, "tailored_resume.md")
        safe_download("Download evidence_cards.json", bundle.evidence_cards_json, "evidence_cards.json", "application/json")
        safe_download("Download jd_analysis.json", bundle.jd_analysis_json, "jd_analysis.json", "application/json")
    with cols[1]:
        safe_download("Download gap_report.md", bundle.gap_report_md, "gap_report.md")
        safe_download("Download interview_prep.md", bundle.interview_prep_md, "interview_prep.md")

    with st.expander("Preview tailored_resume.md", expanded=True):
        st.code(bundle.tailored_resume_md, language="markdown")
