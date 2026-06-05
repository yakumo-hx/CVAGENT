from __future__ import annotations

import streamlit as st

from src.agents.resume_parser import parse_resume_text_fallback
from src.agents.llm_workflow import parse_resume_with_deepseek
from src.i18n import t
from src.local_store import LocalStore
from src.ui.components import add_token_log, current_lang, get_client_from_state, render_key_status, render_token_dashboard
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    store = LocalStore()
    hero(t("nav.resume", lang), t("resume.subtitle", lang))
    render_key_status()
    render_token_dashboard(compact=True)

    left, right = st.columns([0.95, 1.05])
    with left:
        with st.form("resume_parse_form"):
            text = st.text_area(t("resume.paste", lang), value=st.session_state.get("resume_text", ""), height=320)
            uploaded = st.file_uploader(t("resume.upload", lang), type=["md", "txt"])
            use_llm = st.toggle(t("resume.use_llm", lang), value=bool(st.session_state.get("api_key")))
            submitted = st.form_submit_button(t("resume.parse", lang))

        if submitted:
            file_ids: list[str] = []
            if uploaded:
                uploaded_bytes = uploaded.read()
                file_ids.append(store.save_file_bytes(uploaded.name, uploaded_bytes, label="resume_upload", surface="web"))
                text = uploaded_bytes.decode("utf-8", errors="ignore")

            if not text.strip():
                st.warning(t("resume.empty", lang))
            else:
                st.session_state["resume_text"] = text
                client = get_client_from_state() if use_llm else None
                if client:
                    resume, token_log, warning = parse_resume_with_deepseek(text, client, lang)
                    add_token_log(token_log)
                    if warning:
                        st.warning(warning)
                else:
                    resume = parse_resume_text_fallback(text, lang)
                st.session_state["master_resume"] = resume
                if not uploaded:
                    file_ids.append(store.save_text_snapshot("resume_paste", text, surface="web"))
                store.record_event(
                    "resume_parse",
                    t("resume.parsed", lang),
                    f"{len(text)} chars, projects={len(resume.projects)}, experiences={len(resume.experiences)}",
                    surface="web",
                    files=file_ids,
                    metadata={"projects": len(resume.projects), "experiences": len(resume.experiences), "skills": len(resume.skills)},
                )
                st.success(t("resume.parsed", lang))

    with right:
        resume = st.session_state.get("master_resume")
        if resume:
            st.subheader(t("resume.parsed_title", lang))
            cols = st.columns(4)
            cols[0].metric(t("resume.projects", lang), len(resume.projects))
            cols[1].metric(t("resume.experience", lang), len(resume.experiences))
            cols[2].metric(t("resume.skills", lang), len(resume.skills))
            cols[3].metric(t("resume.education", lang), len(resume.education))
            with st.expander(t("resume.json", lang), expanded=True):
                st.json(resume.model_dump())
        else:
            st.info(t("resume.waiting", lang))
