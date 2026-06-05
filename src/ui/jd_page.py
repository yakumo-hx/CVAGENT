from __future__ import annotations

import streamlit as st

from src.agents.jd_analyzer import analyze_jd_fallback


def render() -> None:
    st.title("JD Analyzer")
    text = st.text_area("Paste target JD", value=st.session_state.get("jd_text", ""), height=260)

    if st.button("Analyze JD", disabled=not text.strip()):
        st.session_state["jd_text"] = text
        st.session_state["jd_analysis"] = analyze_jd_fallback(text)

    jd = st.session_state.get("jd_analysis")
    if jd:
        st.subheader("JD analysis")
        st.json(jd.model_dump())
