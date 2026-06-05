from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def load_text_file(path: str | Path) -> str:
    path = Path(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def load_pdf_text(path: str | Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)
