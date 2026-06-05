from __future__ import annotations

import streamlit as st

from src.config import SUPPORTED_MODELS
from src.deepseek_client import DeepSeekClient


def render() -> None:
    st.title("Settings")
    st.caption("输入自己的 DeepSeek API Key。本项目不会把 Key 提交到仓库。")

    api_key = st.text_input("DeepSeek API Key", value=st.session_state.get("api_key", ""), type="password")
    model = st.selectbox("Model", SUPPORTED_MODELS, index=0)

    if st.button("Save settings"):
        st.session_state["api_key"] = api_key
        st.session_state["model"] = model
        st.success("Settings saved for this session.")

    if st.button("Test connection", disabled=not api_key):
        try:
            client = DeepSeekClient(api_key=api_key, model=model)
            result = client.test_connection()
            st.success(f"DeepSeek replied: {result}")
        except Exception as exc:  # pragma: no cover - UI feedback
            st.error(f"Connection failed: {exc}")

    st.info("简历和 JD 会在你触发模型调用时发送到 DeepSeek API；本软件不上传到作者服务器。")
