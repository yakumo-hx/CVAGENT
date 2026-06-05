from __future__ import annotations

import streamlit as st

from src.i18n import DEFAULT_LANG, LANGUAGES, t
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


PAGES = [
    ("settings", "nav.settings", settings_page.render),
    ("resume", "nav.resume", resume_page.render),
    ("jd", "nav.jd", jd_page.render),
    ("matrix", "nav.matrix", matrix_page.render),
    ("interview", "nav.interview", interview_page.render),
    ("evidence", "nav.evidence", evidence_page.render),
    ("writer", "nav.writer", rewrite_page.render),
    ("export", "nav.export", export_page.render),
]


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
    st.session_state.setdefault("lang", DEFAULT_LANG)
    st.session_state.setdefault("language_name", LANGUAGES[DEFAULT_LANG])
    st.session_state.setdefault("page_id", "settings")


def main() -> None:
    st.set_page_config(
        page_title=t("app.title", DEFAULT_LANG),
        page_icon="R",
        layout="wide",
    )
    init_state()
    apply_style()

    lang_name_to_code = {name: code for code, name in LANGUAGES.items()}
    selected_language = st.sidebar.selectbox(
        t("language", st.session_state["lang"]),
        list(lang_name_to_code.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state["lang"]),
        key="language_name",
    )
    selected_lang = lang_name_to_code[selected_language]
    if selected_lang != st.session_state["lang"]:
        st.session_state["lang"] = selected_lang
        st.rerun()
    lang = st.session_state["lang"]

    st.sidebar.markdown(f"### {t('app.title', lang)}")
    st.sidebar.caption(t("app.subtitle", lang))
    page_labels = [t(label_key, lang) for _, label_key, _ in PAGES]
    page_ids = [page_id for page_id, _, _ in PAGES]
    current_index = page_ids.index(st.session_state.get("page_id", "settings"))
    selected_label = st.sidebar.radio(
        t("workflow", lang),
        page_labels,
        index=current_index,
        label_visibility="collapsed",
    )
    selected_index = page_labels.index(selected_label)
    st.session_state["page_id"] = page_ids[selected_index]
    PAGES[selected_index][2]()
