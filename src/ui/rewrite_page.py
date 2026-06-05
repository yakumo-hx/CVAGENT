from __future__ import annotations

import streamlit as st

from src.agents.bullet_generator import generate_bullet_variants
from src.agents.risk_auditor import audit_bullet


def render() -> None:
    st.title("Resume Writer")
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

    requirement = st.text_input("Target requirement", value="")
    if st.button("Generate bullets", disabled=not facts or not requirement.strip()):
        st.session_state["bullets"] = generate_bullet_variants(facts, requirement=requirement)

    for bullet in st.session_state.get("bullets", []):
        st.markdown(f"- {bullet.text}")
        st.caption(f"fact_ids: {', '.join(bullet.fact_ids) or 'none'}")
        findings = audit_bullet(bullet, facts)
        if findings:
            st.warning([finding.model_dump() for finding in findings])
