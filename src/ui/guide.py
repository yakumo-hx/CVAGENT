from __future__ import annotations

import time

import streamlit as st

from src.config import APP_VERSION
from src.i18n import t
from src.local_store import LocalStore


TIP_KEYS = ["guide.tip.1", "guide.tip.2", "guide.tip.3", "guide.tip.4"]


def render_web_guide(lang: str, store: LocalStore | None = None) -> None:
    store = store or LocalStore()
    _render_pending_dialog(lang, store)
    tip = t(TIP_KEYS[int(time.time() // 18) % len(TIP_KEYS)], lang)
    st.markdown(
        f"""
        <div class="rea-floating-guide" title="{t("guide.open", lang)}">
          <div class="rea-floating-guide-row">
            <div class="rea-mouse-shape" aria-label="{t("guide.mouse", lang)}"></div>
            <div class="rea-floating-guide-tip">{tip}</div>
          </div>
          <div class="rea-floating-guide-feedback">{t("guide.feedback", lang)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_pending_dialog(lang: str, store: LocalStore) -> None:
    if not store.onboarding_seen("web"):
        _show_dialog(
            t("guide.welcome_title", lang),
            t("guide.welcome_body", lang),
            lambda: store.mark_onboarding_seen("web"),
            lang,
        )
        return
    if store.update_notice_needed():
        text = store.update_notice_text(lang)
        _show_dialog(
            t("guide.update_title", lang),
            f"{text}\n\nCVAGENT {APP_VERSION}",
            store.mark_version_seen,
            lang,
        )


def _show_dialog(title: str, body: str, on_confirm, lang: str) -> None:
    @st.dialog(title)
    def dialog() -> None:
        st.write(body)
        if st.button(t("guide.got_it", lang)):
            on_confirm()
            st.rerun()

    dialog()
