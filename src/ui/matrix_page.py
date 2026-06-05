from __future__ import annotations

import pandas as pd
import streamlit as st

from src.agents.evidence_matcher import build_evidence_matrix


def render() -> None:
    st.title("Evidence Matrix")
    resume = st.session_state.get("master_resume")
    jd = st.session_state.get("jd_analysis")

    if st.button("Build matrix", disabled=not resume or not jd):
        st.session_state["matrix_rows"] = build_evidence_matrix(resume, jd)

    rows = st.session_state.get("matrix_rows", [])
    if rows:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "JD requirement": row.requirement_text,
                        "Best evidence": row.best_evidence_summary,
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
