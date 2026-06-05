from __future__ import annotations

import os

import streamlit as st

from src.config import SUPPORTED_MODELS
from src.deepseek_client import DeepSeekClient
from src.security import mask_secret
from src.ui.components import add_token_log, render_token_dashboard, render_token_log_table
from src.ui.state import load_env_without_echo
from src.ui.style import hero


def render() -> None:
    hero("Settings", "配置 DeepSeek API，测试连接，并查看 token 使用情况。")
    load_env_without_echo()

    env_key_available = bool(os.getenv("DEEPSEEK_API_KEY"))
    current_key = st.session_state.get("api_key", "")

    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("DeepSeek")
        api_key = st.text_input(
            "DeepSeek API Key",
            value=current_key,
            type="password",
            help="默认只保存在当前 Streamlit session；不会写入仓库或导出文件。",
        )
        model = st.selectbox(
            "Model",
            SUPPORTED_MODELS,
            index=SUPPORTED_MODELS.index(st.session_state.get("model", SUPPORTED_MODELS[0]))
            if st.session_state.get("model", SUPPORTED_MODELS[0]) in SUPPORTED_MODELS
            else 0,
        )
        st.session_state["save_api_key"] = st.checkbox(
            "Keep key in this browser session",
            value=st.session_state.get("save_api_key", False),
            help="只保留在 Streamlit session_state。刷新或重启服务后可能丢失。",
        )

        cols = st.columns(3)
        if cols[0].button("Save settings"):
            st.session_state["api_key"] = api_key
            st.session_state["model"] = model
            st.success("Settings saved for this session.")

        if cols[1].button("Load env key", disabled=not env_key_available):
            st.session_state["api_key"] = os.getenv("DEEPSEEK_API_KEY", "")
            st.session_state["model"] = model
            st.success(f"Loaded environment key: {mask_secret(st.session_state['api_key'])}")

        if cols[2].button("Forget key"):
            st.session_state["api_key"] = ""
            st.success("API key removed from session.")

        if st.button("Test connection and get guide", disabled=not (api_key or st.session_state.get("api_key"))):
            try:
                key_to_test = api_key or st.session_state.get("api_key", "")
                client = DeepSeekClient(api_key=key_to_test, model=model)
                result = client.guidance_message()
                add_token_log(result.token_log)
                st.session_state["last_guidance"] = result.content
                st.session_state["api_key"] = key_to_test
                st.session_state["model"] = model
                st.success(result.content)
            except Exception as exc:  # pragma: no cover - UI feedback
                st.error(f"Connection failed: {exc}")

    with right:
        st.subheader("Protection")
        st.markdown(
            """
            <div class="rea-panel">
            <b>Key handling</b><br>
            API Key 使用密码框输入，默认只存于当前 session。token 日志和导出内容会做密钥脱敏。
            </div>
            <div class="rea-panel">
            <b>Data boundary</b><br>
            简历和 JD 只会在你点击模型按钮时发送到 DeepSeek API。本项目不连接招聘网站，不自动投递。
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.get("last_guidance"):
            st.info(st.session_state["last_guidance"])

    st.subheader("Token monitor")
    render_token_dashboard()
    with st.expander("Token call log"):
        render_token_log_table()
