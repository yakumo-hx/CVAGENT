from __future__ import annotations

import streamlit as st

from src.schemas import FactCard, Metric
from src.ui.style import hero


def render() -> None:
    hero("Evidence Cards", "管理从追问中沉淀出的事实卡；只有确认后的事实卡才能进入正式 bullet。")

    facts: list[FactCard] = st.session_state.get("fact_cards", [])
    if not facts:
        st.info("暂无事实卡。请先在 Branching Interview 页面回答追问。")
        return

    confirmed = sum(1 for fact in facts if fact.can_use_in_resume and not fact.needs_confirmation)
    cols = st.columns(3)
    cols[0].metric("Fact cards", len(facts))
    cols[1].metric("Confirmed", confirmed)
    cols[2].metric("Pending", len(facts) - confirmed)

    bulk_cols = st.columns([0.25, 0.75])
    if bulk_cols[0].button("Confirm all pending"):
        for fact in facts:
            fact.can_use_in_resume = True
            fact.needs_confirmation = False
        st.success("All pending fact cards confirmed.")
        st.rerun()

    delete_ids: set[str] = set()
    for index, fact in enumerate(facts):
        with st.expander(f"{fact.fact_id} | {fact.claim}", expanded=index == len(facts) - 1):
            fact.claim = st.text_area("Claim", value=fact.claim, key=f"claim_{fact.fact_id}", height=80)
            fact.related_experience = st.text_input(
                "Related experience",
                value=fact.related_experience,
                key=f"exp_{fact.fact_id}",
            )
            fact.role = st.selectbox(
                "Role",
                ["", "参与", "负责", "主导"],
                index=["", "参与", "负责", "主导"].index(fact.role)
                if fact.role in ["", "参与", "负责", "主导"]
                else 0,
                key=f"role_{fact.fact_id}",
            )
            tools_text = st.text_input(
                "Tools",
                value=", ".join(fact.tools),
                key=f"tools_{fact.fact_id}",
            )
            fact.tools = [item.strip() for item in tools_text.split(",") if item.strip()]
            metrics_text = st.text_input(
                "Metrics",
                value=", ".join(metric.value or "" for metric in fact.metrics),
                key=f"metrics_{fact.fact_id}",
                help="只写真实可解释的数字；没有就留空。",
            )
            fact.metrics = [
                Metric(type="user_metric", value=item.strip(), status="provided")
                for item in metrics_text.split(",")
                if item.strip()
            ]
            fact.outcome = st.text_input("Outcome", value=fact.outcome, key=f"outcome_{fact.fact_id}")
            fact.risk = st.text_input("Risk", value=fact.risk, key=f"risk_{fact.fact_id}")
            fact.can_use_in_resume = st.checkbox(
                "Confirmed and usable in resume",
                value=fact.can_use_in_resume and not fact.needs_confirmation,
                key=f"confirm_{fact.fact_id}",
            )
            fact.needs_confirmation = not fact.can_use_in_resume

            if st.button("Delete fact card", key=f"delete_{fact.fact_id}"):
                delete_ids.add(fact.fact_id)

    if delete_ids:
        st.session_state["fact_cards"] = [fact for fact in facts if fact.fact_id not in delete_ids]
        st.success("Deleted selected fact card.")
        st.rerun()
