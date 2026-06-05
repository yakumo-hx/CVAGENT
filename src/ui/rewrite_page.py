from __future__ import annotations

import streamlit as st

from src.agents.bullet_generator import generate_bullet_variants
from src.agents.question_planner import pick_next_gap
from src.agents.risk_auditor import audit_bullet
from src.ui.style import hero


def render() -> None:
    hero("Resume Writer", "只基于已确认事实卡生成保守版、标准版和 JD 强匹配版 bullet。")
    facts = st.session_state.get("fact_cards", [])

    st.subheader("Fact cards")
    for fact in facts:
        with st.expander(f"{fact.fact_id}: {fact.claim}"):
            fact.can_use_in_resume = st.checkbox(
                "Confirmed and usable",
                value=fact.can_use_in_resume,
                key=f"use_{fact.fact_id}",
            )
            fact.needs_confirmation = not fact.can_use_in_resume
            st.json(fact.model_dump())

    confirmed_count = sum(1 for fact in facts if fact.can_use_in_resume and not fact.needs_confirmation)
    st.metric("Confirmed facts available", confirmed_count)
    if "writer_requirement" not in st.session_state:
        next_gap = pick_next_gap(st.session_state.get("matrix_rows", []))
        st.session_state["writer_requirement"] = next_gap.requirement_text if next_gap else ""

    if st.button("Use next gap requirement"):
        next_gap = pick_next_gap(st.session_state.get("matrix_rows", []))
        if next_gap:
            st.session_state["writer_requirement"] = next_gap.requirement_text
            st.rerun()

    with st.form("bullet_generation_form"):
        st.text_input("Target requirement", key="writer_requirement")
        submitted = st.form_submit_button("Generate bullets")

    requirement = st.session_state.get("writer_requirement", "")
    if submitted:
        if not facts:
            st.warning("还没有事实卡。请先完成追问并确认事实卡。")
        elif not requirement.strip():
            st.warning("请先输入或带入目标 JD 要求。")
        else:
            st.session_state["bullets"] = generate_bullet_variants(facts, requirement=requirement)

    for bullet in st.session_state.get("bullets", []):
        st.markdown(
            f"""
            <div class="rea-panel">
              <b>{bullet.variant}</b><br>
              {bullet.text}<br>
              <span style="color:#6b7280">fact_ids: {', '.join(bullet.fact_ids) or 'none'}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        findings = audit_bullet(bullet, facts)
        if findings:
            st.warning([finding.model_dump() for finding in findings])
