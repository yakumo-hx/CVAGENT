from __future__ import annotations

import streamlit as st

from src.agents.fact_extractor import extract_fact_card_from_answer
from src.agents.question_planner import pick_next_gap, plan_question


def render() -> None:
    st.title("Branching Interview")
    rows = st.session_state.get("matrix_rows", [])
    target = pick_next_gap(rows)

    if not target:
        st.info("No weak or missing evidence gap found.")
        return

    plan = plan_question(target)
    st.subheader(plan["requirement"])
    st.write(plan["question"])
    st.caption(plan["why"])

    answer = st.text_area("Your answer", height=180)
    if st.button("Create fact card", disabled=not answer.strip()):
        fact_id = f"fact_{len(st.session_state.get('fact_cards', [])) + 1:03d}"
        fact = extract_fact_card_from_answer(
            answer,
            fact_id=fact_id,
            related_requirement=target.requirement_text,
            related_experience=target.best_evidence_summary,
        )
        cards = st.session_state.setdefault("fact_cards", [])
        cards.append(fact)
        st.success(f"Created {fact_id}. Confirm it in Evidence Cards / Resume Writer flow.")

    for fact in st.session_state.get("fact_cards", []):
        st.json(fact.model_dump())
