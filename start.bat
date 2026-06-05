@echo off
setlocal

if not exist .venv (
  python -m venv .venv
)

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run apps\web\app.py --server.port 8501

endlocal
