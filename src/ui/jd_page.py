from __future__ import annotations

import streamlit as st

from src.agents.jd_analyzer import analyze_jd_fallback
from src.agents.llm_workflow import analyze_jd_with_deepseek
from src.ui.components import add_token_log, chips, get_client_from_state, render_key_status, render_token_dashboard
from src.ui.style import hero


def render() -> None:
    hero("JD Analyzer", "粘贴目标岗位 JD，拆解必须条件、职责、关键词、隐性要求和面试风险。")
    render_key_status()
    render_token_dashboard(compact=True)

    left, right = st.columns([0.95, 1.05])
    with left:
        with st.form("jd_analyze_form"):
            text = st.text_area("Paste target JD", value=st.session_state.get("jd_text", ""), height=320)
            use_llm = st.toggle("Use DeepSeek analyzer", value=bool(st.session_state.get("api_key")))
            submitted = st.form_submit_button("Analyze JD")

        if submitted:
            if not text.strip():
                st.warning("请先粘贴目标岗位 JD。")
            else:
                st.session_state["jd_text"] = text
                client = get_client_from_state() if use_llm else None
                if client:
                    jd, token_log, warning = analyze_jd_with_deepseek(text, client)
                    add_token_log(token_log)
                    if warning:
                        st.warning(warning)
                else:
                    jd = analyze_jd_fallback(text)
                st.session_state["jd_analysis"] = jd
                st.success("JD analyzed.")

    with right:
        jd = st.session_state.get("jd_analysis")
        if jd:
            st.subheader(jd.job_title or "Target role")
            cols = st.columns(4)
            cols[0].metric("Must-have", len(jd.must_have_requirements))
            cols[1].metric("Nice-to-have", len(jd.nice_to_have_requirements))
            cols[2].metric("Responsibilities", len(jd.responsibilities))
            cols[3].metric("Risks", len(jd.interview_risks))
            if jd.keywords:
                st.markdown(chips(jd.keywords), unsafe_allow_html=True)
            with st.expander("Structured JSON", expanded=True):
                st.json(jd.model_dump())
        else:
            st.info("等待 JD 输入。解析后会展示岗位要求和关键词。")
