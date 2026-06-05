from __future__ import annotations

import streamlit as st


def apply_style() -> None:
    st.markdown(
        """
        <style>
        :root {
          --rea-bg: #f7f8fb;
          --rea-panel: #ffffff;
          --rea-text: #1f2937;
          --rea-muted: #6b7280;
          --rea-line: #d9dee7;
          --rea-blue: #2563eb;
          --rea-green: #12805c;
          --rea-amber: #b45309;
          --rea-red: #b91c1c;
        }
        .stApp {
          background: var(--rea-bg);
          color: var(--rea-text);
        }
        section[data-testid="stSidebar"] {
          background: #ffffff;
          border-right: 1px solid var(--rea-line);
        }
        section[data-testid="stSidebar"] * {
          color: #1f2937;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label {
          color: #1f2937;
          opacity: 1;
        }
        div[data-testid="stMetric"] {
          background: #ffffff;
          border: 1px solid var(--rea-line);
          border-radius: 8px;
          padding: 12px 14px;
        }
        .rea-hero {
          background: #ffffff;
          border: 1px solid var(--rea-line);
          border-radius: 8px;
          padding: 18px 20px;
          margin-bottom: 16px;
        }
        .rea-hero h1 {
          font-size: 28px;
          line-height: 1.2;
          margin: 0 0 6px 0;
          letter-spacing: 0;
        }
        .rea-hero p {
          color: var(--rea-muted);
          margin: 0;
          font-size: 14px;
        }
        .rea-panel {
          background: #ffffff;
          border: 1px solid var(--rea-line);
          border-radius: 8px;
          padding: 14px 16px;
          margin: 10px 0;
        }
        .rea-chip {
          display: inline-block;
          border: 1px solid var(--rea-line);
          border-radius: 999px;
          padding: 2px 9px;
          margin: 2px 4px 2px 0;
          font-size: 12px;
          color: #374151;
          background: #f9fafb;
        }
        .rea-status-direct { color: var(--rea-green); font-weight: 700; }
        .rea-status-transferable { color: var(--rea-blue); font-weight: 700; }
        .rea-status-adjacent { color: var(--rea-amber); font-weight: 700; }
        .rea-status-weak { color: #92400e; font-weight: 700; }
        .rea-status-gap { color: var(--rea-red); font-weight: 700; }
        .stButton button, .stDownloadButton button {
          border-radius: 7px;
          border: 1px solid var(--rea-line);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="rea-hero">
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
