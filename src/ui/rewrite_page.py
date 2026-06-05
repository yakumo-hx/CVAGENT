from __future__ import annotations

import streamlit as st

from src.agents.bullet_generator import generate_bullet_variants
from src.agents.question_planner import pick_next_gap
from src.agents.risk_auditor import audit_bullet
from src.i18n import t
from src.ui.components import current_lang
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    hero(t("nav.writer", lang), t("writer.subtitle", lang))
    facts = st.session_state.get("fact_cards", [])

    st.subheader(t("writer.fact_cards", lang))
    for fact in facts:
        with st.expander(f"{fact.fact_id}: {fact.claim}"):
            fact.can_use_in_resume = st.checkbox(
                t("evidence.confirm", lang),
                value=fact.can_use_in_resume,
                key=f"use_{fact.fact_id}",
            )
            fact.needs_confirmation = not fact.can_use_in_resume
            st.json(fact.model_dump())

    confirmed_count = sum(1 for fact in facts if fact.can_use_in_resume and not fact.needs_confirmation)
    st.metric(t("writer.confirmed_available", lang), confirmed_count)
    if "writer_requirement" not in st.session_state:
        next_gap = pick_next_gap(st.session_state.get("matrix_rows", []))
        st.session_state["writer_requirement"] = next_gap.requirement_text if next_gap else ""

    if st.button(t("writer.use_gap", lang)):
        next_gap = pick_next_gap(st.session_state.get("matrix_rows", []))
        if next_gap:
            st.session_state["writer_requirement"] = next_gap.requirement_text
            st.rerun()

    with st.form("bullet_generation_form"):
        st.text_input(t("writer.target", lang), key="writer_requirement")
        submitted = st.form_submit_button(t("writer.generate", lang))

    requirement = st.session_state.get("writer_requirement", "")
    if submitted:
        if not facts:
            st.warning(t("writer.no_facts", lang))
        elif not requirement.strip():
            st.warning(t("writer.no_requirement", lang))
        else:
            st.session_state["bullets"] = generate_bullet_variants(facts, requirement=requirement, lang=lang)

    for bullet in st.session_state.get("bullets", []):
        variant_label = t(f"writer.variant.{bullet.variant}", lang)
        st.markdown(
            f"""
            <div class="rea-panel">
              <b>{variant_label}</b><br>
              {bullet.text}<br>
              <span style="color:#6b7280">{t("writer.fact_ids", lang)}: {', '.join(bullet.fact_ids) or t("common.none", lang)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        findings = audit_bullet(bullet, facts, lang)
        if findings:
            st.warning("\n".join(f"- {finding.message}" for finding in findings))
