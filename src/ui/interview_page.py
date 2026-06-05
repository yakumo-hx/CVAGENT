from __future__ import annotations

import streamlit as st

from src.agents.fact_extractor import extract_fact_card_from_answer
from src.agents.llm_workflow import extract_fact_with_deepseek
from src.agents.question_planner import pick_next_gap, plan_question
from src.ui.components import add_token_log, get_client_from_state, render_key_status, render_token_dashboard
from src.ui.style import hero


def render() -> None:
    hero("Branching Interview", "针对弱证据或缺证据逐步追问；每次只问一个主问题。")
    render_key_status()
    render_token_dashboard(compact=True)
    rows = st.session_state.get("matrix_rows", [])
    target = pick_next_gap(rows)

    if not target:
        st.info("No weak or missing evidence gap found.")
        return

    plan = plan_question(target)
    st.markdown(
        f"""
        <div class="rea-panel">
          <b>当前 gap</b><br>{plan["requirement"]}<br><br>
          <b>问题</b><br>{plan["question"]}<br><br>
          <b>为什么问</b><br>{plan["why"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("fact_card_form"):
        answer = st.text_area("Your answer", height=180)
        use_llm = st.toggle("Use DeepSeek fact extractor", value=bool(st.session_state.get("api_key")))
        submitted = st.form_submit_button("Create fact card")

    if submitted:
        if not answer.strip():
            st.warning("请先回答这个追问。")
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
                )
            cards = st.session_state.setdefault("fact_cards", [])
            cards.append(fact)
            st.success(f"Created {fact_id}. Confirm it in Evidence Cards / Resume Writer flow.")

    if st.session_state.get("fact_cards"):
        st.subheader("Recent fact cards")
        for fact in st.session_state.get("fact_cards", [])[-3:]:
            st.json(fact.model_dump())
