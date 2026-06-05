from __future__ import annotations

import streamlit as st

from src.agents.exporter import build_export_bundle
from src.i18n import t
from src.security import contains_secret
from src.ui.components import current_lang, safe_download
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    hero(t("nav.export", lang), t("export.subtitle", lang))
    bundle = build_export_bundle(
        bullets=st.session_state.get("bullets", []),
        facts=st.session_state.get("fact_cards", []),
        jd=st.session_state.get("jd_analysis"),
        matrix_rows=st.session_state.get("matrix_rows", []),
        lang=lang,
    )

    outputs = {
        "tailored_resume.md": bundle.tailored_resume_md,
        "evidence_cards.json": bundle.evidence_cards_json,
        "jd_analysis.json": bundle.jd_analysis_json,
        "gap_report.md": bundle.gap_report_md,
        "interview_prep.md": bundle.interview_prep_md,
    }

    if any(contains_secret(content) for content in outputs.values()):
        st.error(t("export.secret", lang))
        return

    cols = st.columns(2)
    with cols[0]:
        safe_download(t("export.download_resume", lang), bundle.tailored_resume_md, "tailored_resume.md")
        safe_download(t("export.download_facts", lang), bundle.evidence_cards_json, "evidence_cards.json", "application/json")
        safe_download(t("export.download_jd", lang), bundle.jd_analysis_json, "jd_analysis.json", "application/json")
    with cols[1]:
        safe_download(t("export.download_gap", lang), bundle.gap_report_md, "gap_report.md")
        safe_download(t("export.download_interview", lang), bundle.interview_prep_md, "interview_prep.md")

    with st.expander(t("export.preview", lang), expanded=True):
        st.code(bundle.tailored_resume_md, language="markdown")
