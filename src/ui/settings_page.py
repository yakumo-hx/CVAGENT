from __future__ import annotations

import os

import streamlit as st

from src.config import SUPPORTED_MODELS
from src.deepseek_client import DeepSeekClient
from src.i18n import t
from src.security import mask_secret
from src.ui.components import add_token_log, current_lang, render_token_dashboard, render_token_log_table
from src.ui.state import load_env_without_echo
from src.ui.style import hero


def render() -> None:
    lang = current_lang()
    hero(t("nav.settings", lang), t("settings.subtitle", lang))
    load_env_without_echo()

    env_key_available = bool(os.getenv("DEEPSEEK_API_KEY"))
    current_key = st.session_state.get("api_key", "")

    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader(t("settings.deepseek", lang))
        api_key = st.text_input(
            t("settings.key", lang),
            value=current_key,
            type="password",
            help=t("settings.key_help", lang),
        )
        model = st.selectbox(
            t("settings.model", lang),
            SUPPORTED_MODELS,
            index=SUPPORTED_MODELS.index(st.session_state.get("model", SUPPORTED_MODELS[0]))
            if st.session_state.get("model", SUPPORTED_MODELS[0]) in SUPPORTED_MODELS
            else 0,
        )
        st.session_state["save_api_key"] = st.checkbox(
            t("settings.keep_session", lang),
            value=st.session_state.get("save_api_key", False),
            help=t("settings.key_help", lang),
        )

        cols = st.columns(3)
        if cols[0].button(t("settings.save", lang)):
            st.session_state["api_key"] = api_key
            st.session_state["model"] = model
            st.success(t("settings.saved", lang))

        if cols[1].button(t("settings.load_env", lang), disabled=not env_key_available):
            st.session_state["api_key"] = os.getenv("DEEPSEEK_API_KEY", "")
            st.session_state["model"] = model
            st.success(t("settings.loaded_env", lang, key=mask_secret(st.session_state["api_key"])))

        if cols[2].button(t("settings.forget", lang)):
            st.session_state["api_key"] = ""
            st.success(t("settings.forgot", lang))

        if st.button(t("settings.test", lang), disabled=not (api_key or st.session_state.get("api_key"))):
            try:
                key_to_test = api_key or st.session_state.get("api_key", "")
                client = DeepSeekClient(api_key=key_to_test, model=model)
                result = client.guidance_message(lang)
                add_token_log(result.token_log)
                st.session_state["last_guidance"] = result.content
                st.session_state["api_key"] = key_to_test
                st.session_state["model"] = model
                st.success(result.content)
            except Exception as exc:  # pragma: no cover - UI feedback
                st.error(t("settings.failed", lang, error=exc))

    with right:
        st.subheader(t("settings.protection", lang))
        st.markdown(
            f"""
            <div class="rea-panel">
            <b>{t("settings.key_handling", lang)}</b><br>
            {t("settings.key_handling_body", lang)}
            </div>
            <div class="rea-panel">
            <b>{t("settings.data_boundary", lang)}</b><br>
            {t("settings.data_boundary_body", lang)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.get("last_guidance"):
            st.info(st.session_state["last_guidance"])

    st.subheader(t("token.monitor", lang))
    render_token_dashboard()
    with st.expander(t("token.log", lang)):
        render_token_log_table()
