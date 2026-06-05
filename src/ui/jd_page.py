from __future__ import annotations

import streamlit as st

from src.agents.jd_analyzer import analyze_jd_fallback
from src.agents.llm_workflow import analyze_jd_with_deepseek
from src.i18n import t
from src.local_store import LocalStore
from src.ui.components import add_token_log, chips, current_lang, get_client_from_state, render_key_status, render_token_dashboard
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    store = LocalStore()
    hero(t("nav.jd", lang), t("jd.subtitle", lang))
    render_key_status()
    render_token_dashboard(compact=True)

    left, right = st.columns([0.95, 1.05])
    with left:
        with st.form("jd_analyze_form"):
            text = st.text_area(t("jd.paste", lang), value=st.session_state.get("jd_text", ""), height=320)
            use_llm = st.toggle(t("jd.use_llm", lang), value=bool(st.session_state.get("api_key")))
            submitted = st.form_submit_button(t("jd.analyze", lang))

        if submitted:
            if not text.strip():
                st.warning(t("jd.empty", lang))
            else:
                st.session_state["jd_text"] = text
                client = get_client_from_state() if use_llm else None
                if client:
                    jd, token_log, warning = analyze_jd_with_deepseek(text, client, lang)
                    add_token_log(token_log)
                    if warning:
                        st.warning(warning)
                else:
                    jd = analyze_jd_fallback(text, lang)
                st.session_state["jd_analysis"] = jd
                file_id = store.save_text_snapshot("jd_paste", text, surface="web")
                store.record_event(
                    "jd_analyze",
                    t("jd.done", lang),
                    f"{len(text)} chars, must={len(jd.must_have_requirements)}, nice={len(jd.nice_to_have_requirements)}",
                    surface="web",
                    files=[file_id],
                    metadata={
                        "must_have": len(jd.must_have_requirements),
                        "nice_to_have": len(jd.nice_to_have_requirements),
                        "responsibilities": len(jd.responsibilities),
                    },
                )
                st.success(t("jd.done", lang))

    with right:
        jd = st.session_state.get("jd_analysis")
        if jd:
            st.subheader(jd.job_title or t("jd.target", lang))
            cols = st.columns(4)
            cols[0].metric(t("jd.must", lang), len(jd.must_have_requirements))
            cols[1].metric(t("jd.nice", lang), len(jd.nice_to_have_requirements))
            cols[2].metric(t("jd.responsibilities", lang), len(jd.responsibilities))
            cols[3].metric(t("jd.risks", lang), len(jd.interview_risks))
            if jd.keywords:
                st.markdown(chips(jd.keywords), unsafe_allow_html=True)
            with st.expander(t("resume.json", lang), expanded=True):
                st.json(jd.model_dump())
        else:
            st.info(t("jd.waiting", lang))
