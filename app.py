from __future__ import annotations

import streamlit as st

from src.ui import (
    evidence_page,
    export_page,
    interview_page,
    jd_page,
    matrix_page,
    resume_page,
    rewrite_page,
    settings_page,
)
from src.ui.style import apply_style


PAGES = {
    "Settings": settings_page.render,
    "Resume Library": resume_page.render,
    "JD Analyzer": jd_page.render,
    "Evidence Matrix": matrix_page.render,
    "Branching Interview": interview_page.render,
    "Evidence Cards": evidence_page.render,
    "Resume Writer": rewrite_page.render,
    "Export": export_page.render,
}


def init_state() -> None:
    st.session_state.setdefault("api_key", "")
    st.session_state.setdefault("model", "deepseek-v4-flash")
    st.session_state.setdefault("resume_text", "")
    st.session_state.setdefault("jd_text", "")
    st.session_state.setdefault("master_resume", None)
    st.session_state.setdefault("jd_analysis", None)
    st.session_state.setdefault("matrix_rows", [])
    st.session_state.setdefault("fact_cards", [])
    st.session_state.setdefault("bullets", [])
    st.session_state.setdefault("token_logs", [])
    st.session_state.setdefault("last_guidance", "")
    st.session_state.setdefault("save_api_key", False)


def main() -> None:
    st.set_page_config(
        page_title="Resume Evidence Agent",
        page_icon="R",
        layout="wide",
    )
    init_state()
    apply_style()

    st.sidebar.markdown("### Resume Evidence Agent")
    st.sidebar.caption("Evidence-first resume workflow")
    selected = st.sidebar.radio("Workflow", list(PAGES.keys()), label_visibility="collapsed")
    PAGES[selected]()


if __name__ == "__main__":
    main()
