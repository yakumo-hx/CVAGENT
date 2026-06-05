from __future__ import annotations

import pandas as pd
import streamlit as st

from src.i18n import t
from src.local_store import LocalStore
from src.ui.components import current_lang
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    store = LocalStore()
    summary = store.summary()
    hero(t("nav.history", lang), t("history.subtitle", lang))

    cols = st.columns(4)
    cols[0].metric(t("history.records", lang), summary["records"])
    cols[1].metric(t("history.files", lang), summary["files"])
    cols[2].metric(t("token.lifetime_calls", lang), summary["lifetime_calls"])
    cols[3].metric(t("token.lifetime_total", lang), summary["lifetime_total_tokens"])

    with st.expander(t("history.profile", lang), expanded=True):
        st.code(summary["profile_id"])
        st.caption(f"{t('history.data_dir', lang)}: {summary['data_dir']}")
        st.info(t("history.compat", lang))
        if store.update_notice_needed():
            st.warning(store.update_notice_text(lang))

    st.subheader(t("history.records", lang))
    records = store.recent_records()
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
    else:
        st.info(t("history.empty_records", lang))

    st.subheader(t("history.files", lang))
    files = store.recent_files()
    if files:
        st.dataframe(pd.DataFrame(files), use_container_width=True, hide_index=True)
    else:
        st.info(t("history.empty_files", lang))

    st.subheader(t("history.tokens", lang))
    tokens = store.recent_tokens()
    if tokens:
        st.dataframe(pd.DataFrame(tokens), use_container_width=True, hide_index=True)
    else:
        st.info(t("token.none", lang))
