from __future__ import annotations

import streamlit as st

from src.agents.fact_extractor import extract_fact_card_from_answer
from src.agents.llm_workflow import extract_fact_with_deepseek
from src.agents.question_planner import pick_next_gap, plan_question
from src.i18n import t
from src.ui.components import add_token_log, current_lang, get_client_from_state, render_key_status, render_token_dashboard
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    hero(t("nav.interview", lang), t("interview.subtitle", lang))
    render_key_status()
    render_token_dashboard(compact=True)
    rows = st.session_state.get("matrix_rows", [])
    target = pick_next_gap(rows)

    if not target:
        st.info(t("interview.no_gap", lang))
        return

    plan = plan_question(target, lang)
    st.markdown(
        f"""
        <div class="rea-panel">
          <b>{t("interview.current_gap", lang)}</b><br>{plan["requirement"]}<br><br>
          <b>{t("interview.question", lang)}</b><br>{plan["question"]}<br><br>
          <b>{t("interview.why", lang)}</b><br>{plan["why"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("fact_card_form"):
        answer = st.text_area(t("interview.answer", lang), height=180)
        use_llm = st.toggle(t("interview.use_llm", lang), value=bool(st.session_state.get("api_key")))
        submitted = st.form_submit_button(t("interview.create", lang))

    if submitted:
        if not answer.strip():
            st.warning(t("interview.empty", lang))
        else:
            fact_id = f"fact_{len(st.session_state.get('fact_cards', [])) + 1:03d}"
            client = get_client_from_state() if use_llm else None
            if client:
                fact, token_log, warning = extract_fact_with_deepseek(
                    answer,
                    fact_id=fact_id,
                    related_requirement=target.requirement_text,
                    related_experience=target.best_evidence_summary,
                    client=client,
                    lang=lang,
                )
                add_token_log(token_log)
                if warning:
                    st.warning(warning)
            else:
                fact = extract_fact_card_from_answer(
                    answer,
                    fact_id=fact_id,
                    related_requirement=target.requirement_text,
                    related_experience=target.best_evidence_summary,
                    lang=lang,
                )
            cards = st.session_state.setdefault("fact_cards", [])
            cards.append(fact)
            st.success(t("interview.created", lang, fact_id=fact_id))

    if st.session_state.get("fact_cards"):
        st.subheader(t("interview.recent", lang))
        for fact in st.session_state.get("fact_cards", [])[-3:]:
            st.json(fact.model_dump())
