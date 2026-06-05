from __future__ import annotations

import pandas as pd
import streamlit as st

from src.agents.evidence_matcher import build_evidence_matrix
from src.ui.style import hero


def render() -> None:
    hero("Evidence Matrix", "生成 JD 要求与简历证据的匹配矩阵，优先暴露弱证据和缺证据。")
    resume = st.session_state.get("master_resume")
    jd = st.session_state.get("jd_analysis")

    if st.button("Build matrix", disabled=not resume or not jd):
        st.session_state["matrix_rows"] = build_evidence_matrix(resume, jd)

    rows = st.session_state.get("matrix_rows", [])
    if rows:
        cols = st.columns(5)
        statuses = [row.score.status for row in rows]
        for idx, status in enumerate(["DIRECT", "TRANSFERABLE", "ADJACENT", "WEAK", "GAP"]):
            cols[idx].metric(status, statuses.count(status))
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "JD requirement": row.requirement_text,
                        "Best evidence": row.best_evidence_summary,
                        "Direct": row.score.direct,
                        "Transferable": row.score.transferable,
                        "Adjacent": row.score.adjacent,
                        "Impact": row.score.impact,
                        "Score": row.score.total,
                        "Status": row.score.status,
                        "Gap": row.gap,
                        "Next question": row.next_question,
                    }
                    for row in rows
                ]
            ),
            use_container_width=True,
        )
    else:
        st.info("Parse a resume and JD first, then build the evidence matrix.")
