from __future__ import annotations

import streamlit as st

from src.agents.exporter import build_export_bundle


def render() -> None:
    st.title("Export")
    bundle = build_export_bundle(
        bullets=st.session_state.get("bullets", []),
        facts=st.session_state.get("fact_cards", []),
        jd=st.session_state.get("jd_analysis"),
        matrix_rows=st.session_state.get("matrix_rows", []),
    )

    st.download_button("Download tailored_resume.md", bundle.tailored_resume_md, "tailored_resume.md")
    st.download_button("Download evidence_cards.json", bundle.evidence_cards_json, "evidence_cards.json")
    st.download_button("Download jd_analysis.json", bundle.jd_analysis_json, "jd_analysis.json")
    st.download_button("Download gap_report.md", bundle.gap_report_md, "gap_report.md")
    st.download_button("Download interview_prep.md", bundle.interview_prep_md, "interview_prep.md")
