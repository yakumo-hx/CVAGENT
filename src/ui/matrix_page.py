from __future__ import annotations

import pandas as pd
import streamlit as st

from src.agents.evidence_matcher import build_evidence_matrix, gap_text, next_question, status_label
from src.i18n import t
from src.ui.components import current_lang
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    hero(t("nav.matrix", lang), t("matrix.subtitle", lang))
    resume = st.session_state.get("master_resume")
    jd = st.session_state.get("jd_analysis")

    if st.button(t("matrix.build", lang), disabled=not resume or not jd):
        st.session_state["matrix_rows"] = build_evidence_matrix(resume, jd, lang)

    rows = st.session_state.get("matrix_rows", [])
    if rows:
        cols = st.columns(5)
        statuses = [row.score.status for row in rows]
        for idx, status in enumerate(["DIRECT", "TRANSFERABLE", "ADJACENT", "WEAK", "GAP"]):
            cols[idx].metric(status_label(status, lang), statuses.count(status))
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        t("matrix.req", lang): row.requirement_text,
                        t("matrix.evidence", lang): row.best_evidence_summary,
                        t("matrix.direct", lang): row.score.direct,
                        t("matrix.transferable", lang): row.score.transferable,
                        t("matrix.adjacent", lang): row.score.adjacent,
                        t("matrix.impact", lang): row.score.impact,
                        t("matrix.score", lang): row.score.total,
                        t("matrix.status", lang): status_label(row.score.status, lang),
                        t("matrix.gap", lang): gap_text(row.score.status, lang),
                        t("matrix.question", lang): next_question(
                            row.requirement_text,
                            row.best_evidence_summary,
                            row.score.status,
                            lang,
                        ),
                    }
                    for row in rows
                ]
            ),
            use_container_width=True,
        )
    else:
        st.info(t("matrix.waiting", lang))
