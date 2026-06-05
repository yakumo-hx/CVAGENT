from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

import pandas as pd
import streamlit as st

from src.deepseek_client import DeepSeekClient
from src.i18n import DEFAULT_LANG, t
from src.local_store import LocalStore
from src.security import mask_secret, redact_secrets
from src.utils.token_logger import TokenLog


def get_client_from_state() -> DeepSeekClient | None:
    api_key = st.session_state.get("api_key", "")
    model = st.session_state.get("model", "deepseek-v4-flash")
    if not api_key:
        return None
    return DeepSeekClient(api_key=api_key, model=model)


def add_token_log(log: TokenLog | None) -> None:
    if log is None:
        return
    st.session_state.setdefault("token_logs", []).append(log)
    LocalStore().append_token_log(log, surface="web")


def token_summary() -> dict[str, int]:
    logs: list[TokenLog] = st.session_state.get("token_logs", [])
    return {
        "calls": len(logs),
        "input_tokens": sum(row.input_tokens for row in logs),
        "output_tokens": sum(row.output_tokens for row in logs),
        "total_tokens": sum(row.total_tokens for row in logs),
    }


def current_lang() -> str:
    return st.session_state.get("lang", DEFAULT_LANG)


def render_token_dashboard(compact: bool = False) -> None:
    lang = current_lang()
    summary = token_summary()
    lifetime = LocalStore().token_summary()
    if compact:
        st.caption(
            t(
                "token.compact",
                lang,
                total=summary["total_tokens"],
                input=summary["input_tokens"],
                output=summary["output_tokens"],
                calls=summary["calls"],
            )
        )
        if lifetime["lifetime_calls"]:
            st.caption(
                t(
                    "token.compact",
                    lang,
                    total=lifetime["lifetime_total_tokens"],
                    input=lifetime["lifetime_input_tokens"],
                    output=lifetime["lifetime_output_tokens"],
                    calls=lifetime["lifetime_calls"],
                )
                + f" · {t('token.lifetime', lang)}"
            )
        return
    st.caption(t("token.session", lang))
    cols = st.columns(4)
    cols[0].metric(t("token.calls", lang), summary["calls"])
    cols[1].metric(t("token.input", lang), summary["input_tokens"])
    cols[2].metric(t("token.output", lang), summary["output_tokens"])
    cols[3].metric(t("token.total", lang), summary["total_tokens"])
    st.caption(t("token.lifetime", lang))
    all_cols = st.columns(4)
    all_cols[0].metric(t("token.lifetime_calls", lang), lifetime["lifetime_calls"])
    all_cols[1].metric(t("token.input", lang), lifetime["lifetime_input_tokens"])
    all_cols[2].metric(t("token.output", lang), lifetime["lifetime_output_tokens"])
    all_cols[3].metric(t("token.lifetime_total", lang), lifetime["lifetime_total_tokens"])


def render_token_log_table() -> None:
    logs: list[TokenLog] = st.session_state.get("token_logs", [])
    if not logs:
        st.info(t("token.none", current_lang()))
        return
    rows = [asdict(row) for row in logs]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_key_status() -> None:
    lang = current_lang()
    api_key = st.session_state.get("api_key", "")
    if api_key:
        st.success(t("key.loaded", lang, key=mask_secret(api_key)))
    else:
        st.warning(t("key.missing", lang))


def safe_download(label: str, content: str, file_name: str, mime: str = "text/plain") -> None:
    st.download_button(
        label,
        redact_secrets(content),
        file_name,
        mime=mime,
    )


def chips(items: Iterable[str]) -> str:
    return "".join(f'<span class="rea-chip">{item}</span>' for item in items if item)
