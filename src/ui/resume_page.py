from __future__ import annotations

import streamlit as st

from src.agents.resume_parser import parse_resume_text_fallback
from src.agents.llm_workflow import parse_resume_with_deepseek
from src.ui.components import add_token_log, get_client_from_state, render_key_status, render_token_dashboard
from src.ui.style import hero


def render() -> None:
    hero("Resume Library", "粘贴或上传简历，生成可编辑的 master resume 结构。")
    render_key_status()
    render_token_dashboard(compact=True)

    left, right = st.columns([0.95, 1.05])
    with left:
        with st.form("resume_parse_form"):
            text = st.text_area("Paste resume text", value=st.session_state.get("resume_text", ""), height=320)
            uploaded = st.file_uploader("Or upload .md/.txt", type=["md", "txt"])
            use_llm = st.toggle("Use DeepSeek parser", value=bool(st.session_state.get("api_key")))
            submitted = st.form_submit_button("Parse resume")

        if submitted:
            if uploaded:
                text = uploaded.read().decode("utf-8", errors="ignore")

            if not text.strip():
                st.warning("请先粘贴或上传简历。")
            else:
                st.session_state["resume_text"] = text
                client = get_client_from_state() if use_llm else None
                if client:
                    resume, token_log, warning = parse_resume_with_deepseek(text, client)
                    add_token_log(token_log)
                    if warning:
                        st.warning(warning)
                else:
                    resume = parse_resume_text_fallback(text)
                st.session_state["master_resume"] = resume
                st.success("Resume parsed.")

    with right:
        resume = st.session_state.get("master_resume")
        if resume:
            st.subheader("Parsed resume")
            cols = st.columns(4)
            cols[0].metric("Projects", len(resume.projects))
            cols[1].metric("Experience", len(resume.experiences))
            cols[2].metric("Skills", len(resume.skills))
            cols[3].metric("Education", len(resume.education))
            with st.expander("Structured JSON", expanded=True):
                st.json(resume.model_dump())
        else:
            st.info("等待简历输入。解析后会显示项目、经历、技能和风险提示。")
