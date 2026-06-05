from __future__ import annotations

import streamlit as st

from src.i18n import t
from src.schemas import FactCard, Metric
from src.ui.components import current_lang
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    hero(t("nav.evidence", lang), t("evidence.subtitle", lang))

    facts: list[FactCard] = st.session_state.get("fact_cards", [])
    if not facts:
        st.info(t("evidence.empty", lang))
        return

    confirmed = sum(1 for fact in facts if fact.can_use_in_resume and not fact.needs_confirmation)
    cols = st.columns(3)
    cols[0].metric(t("evidence.cards", lang), len(facts))
    cols[1].metric(t("evidence.confirmed", lang), confirmed)
    cols[2].metric(t("evidence.pending", lang), len(facts) - confirmed)

    bulk_cols = st.columns([0.25, 0.75])
    if bulk_cols[0].button(t("evidence.confirm_all", lang)):
        for fact in facts:
            fact.can_use_in_resume = True
            fact.needs_confirmation = False
        st.success(t("evidence.confirmed_all", lang))
        st.rerun()

    delete_ids: set[str] = set()
    role_value_to_label = {
        "": t("role.none", lang),
        "参与": t("role.participated", lang),
        "负责": t("role.responsible", lang),
        "主导": t("role.led", lang),
    }
    role_label_to_value = {label: value for value, label in role_value_to_label.items()}
    for index, fact in enumerate(facts):
        with st.expander(f"{fact.fact_id} | {fact.claim}", expanded=index == len(facts) - 1):
            fact.claim = st.text_area(t("evidence.claim", lang), value=fact.claim, key=f"claim_{fact.fact_id}", height=80)
            fact.related_experience = st.text_input(
                t("evidence.related", lang),
                value=fact.related_experience,
                key=f"exp_{fact.fact_id}",
            )
            current_role_label = role_value_to_label.get(fact.role, "")
            fact.role = st.selectbox(
                t("evidence.role", lang),
                list(role_label_to_value.keys()),
                index=list(role_label_to_value.keys()).index(current_role_label)
                if current_role_label in role_label_to_value
                else 0,
                key=f"role_{fact.fact_id}",
            )
            fact.role = role_label_to_value.get(fact.role, "")
            tools_text = st.text_input(
                t("evidence.tools", lang),
                value=", ".join(fact.tools),
                key=f"tools_{fact.fact_id}",
            )
            fact.tools = [item.strip() for item in tools_text.split(",") if item.strip()]
            metrics_text = st.text_input(
                t("evidence.metrics", lang),
                value=", ".join(metric.value or "" for metric in fact.metrics),
                key=f"metrics_{fact.fact_id}",
                help=t("evidence.metrics_help", lang),
            )
            fact.metrics = [
                Metric(type="user_metric", value=item.strip(), status="provided")
                for item in metrics_text.split(",")
                if item.strip()
            ]
            fact.outcome = st.text_input(t("evidence.outcome", lang), value=fact.outcome, key=f"outcome_{fact.fact_id}")
            fact.risk = st.text_input(t("evidence.risk", lang), value=fact.risk, key=f"risk_{fact.fact_id}")
            fact.can_use_in_resume = st.checkbox(
                t("evidence.confirm", lang),
                value=fact.can_use_in_resume and not fact.needs_confirmation,
                key=f"confirm_{fact.fact_id}",
            )
            fact.needs_confirmation = not fact.can_use_in_resume

            if st.button(t("evidence.delete", lang), key=f"delete_{fact.fact_id}"):
                delete_ids.add(fact.fact_id)

    if delete_ids:
        st.session_state["fact_cards"] = [fact for fact in facts if fact.fact_id not in delete_ids]
        st.success(t("evidence.deleted", lang))
        st.rerun()
