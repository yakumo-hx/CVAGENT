from __future__ import annotations

import streamlit as st

from src.agents.resume_parser import parse_resume_text_fallback


def render() -> None:
    st.title("Resume Library")
    text = st.text_area("Paste resume text", value=st.session_state.get("resume_text", ""), height=260)
    uploaded = st.file_uploader("Or upload .md/.txt", type=["md", "txt"])

    if uploaded:
        text = uploaded.read().decode("utf-8", errors="ignore")

    if st.button("Parse resume", disabled=not text.strip()):
        st.session_state["resume_text"] = text
        st.session_state["master_resume"] = parse_resume_text_fallback(text)

    resume = st.session_state.get("master_resume")
    if resume:
        st.subheader("Parsed resume")
        st.json(resume.model_dump())
