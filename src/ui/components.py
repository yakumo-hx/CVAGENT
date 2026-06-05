from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

import pandas as pd
import streamlit as st

from src.deepseek_client import DeepSeekClient
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


def token_summary() -> dict[str, int]:
    logs: list[TokenLog] = st.session_state.get("token_logs", [])
    return {
        "calls": len(logs),
        "input_tokens": sum(row.input_tokens for row in logs),
        "output_tokens": sum(row.output_tokens for row in logs),
        "total_tokens": sum(row.total_tokens for row in logs),
    }


def render_token_dashboard(compact: bool = False) -> None:
    summary = token_summary()
    if compact:
        st.caption(
            f"Token usage: {summary['total_tokens']} total "
            f"({summary['input_tokens']} in / {summary['output_tokens']} out), "
            f"{summary['calls']} calls"
        )
        return
    cols = st.columns(4)
    cols[0].metric("LLM calls", summary["calls"])
    cols[1].metric("Input tokens", summary["input_tokens"])
    cols[2].metric("Output tokens", summary["output_tokens"])
    cols[3].metric("Total tokens", summary["total_tokens"])


def render_token_log_table() -> None:
    logs: list[TokenLog] = st.session_state.get("token_logs", [])
    if not logs:
        st.info("No model calls yet.")
        return
    rows = [asdict(row) for row in logs]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_key_status() -> None:
    api_key = st.session_state.get("api_key", "")
    if api_key:
        st.success(f"API key loaded: {mask_secret(api_key)}")
    else:
        st.warning("No API key in this session. Local fallback parsing is available.")


def safe_download(label: str, content: str, file_name: str, mime: str = "text/plain") -> None:
    st.download_button(
        label,
        redact_secrets(content),
        file_name,
        mime=mime,
    )


def chips(items: Iterable[str]) -> str:
    return "".join(f'<span class="rea-chip">{item}</span>' for item in items if item)
