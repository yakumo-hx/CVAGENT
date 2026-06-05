from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any
from uuid import uuid4

from src.config import APP_VERSION
from src.release_notes import release_note_lines
from src.security import redact_secrets
from src.utils.token_logger import TokenLog


SCHEMA_VERSION = 1
MAX_RECORDS = 500
MAX_TOKEN_LOGS = 5000
MAX_FILES = 1000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def app_data_dir() -> Path:
    override = os.getenv("CVAGENT_HOME")
    if override:
        return Path(override)
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "CVAGENT"
    return Path.home() / ".cvagent"


def safe_filename(name: str, fallback: str = "snapshot.txt") -> str:
    cleaned = re.sub(r"[^\w.\-]+", "_", name, flags=re.UNICODE).strip("._")
    return cleaned or fallback


class LocalStore:
    """Versioned local record store shared by Web and desktop builds."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else app_data_dir()
        self.data_path = self.root / "data.json"
        self.files_dir = self.root / "files"

    def load(self) -> dict[str, Any]:
        if not self.data_path.exists():
            data = self._default_data()
            self.save(data)
            return data
        try:
            raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            raw = {}
        data, changed = self._migrate(raw)
        if changed:
            self.save(data)
        return data

    def save(self, data: dict[str, Any]) -> None:
        data["updated_at"] = utc_now()
        self.root.mkdir(parents=True, exist_ok=True)
        tmp_path = self.data_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(self.data_path)

    def profile_id(self) -> str:
        return str(self.load()["profile"]["local_id"])

    def summary(self) -> dict[str, Any]:
        data = self.load()
        token_summary = self.token_summary()
        return {
            "profile_id": data["profile"]["local_id"],
            "data_dir": str(self.root),
            "records": len(data["records"]),
            "files": len(data["files"]),
            **token_summary,
        }

    def append_token_log(self, log: TokenLog | dict[str, Any], surface: str = "unknown") -> None:
        row = self._to_plain_dict(log)
        row["surface"] = surface
        row.setdefault("created_at", utc_now())
        data = self.load()
        data["token_logs"].append(row)
        data["token_logs"] = data["token_logs"][-MAX_TOKEN_LOGS:]
        self.save(data)

    def token_summary(self) -> dict[str, int]:
        logs = self.load()["token_logs"]
        return {
            "lifetime_calls": len(logs),
            "lifetime_input_tokens": sum(int(row.get("input_tokens", 0) or 0) for row in logs),
            "lifetime_output_tokens": sum(int(row.get("output_tokens", 0) or 0) for row in logs),
            "lifetime_total_tokens": sum(int(row.get("total_tokens", 0) or 0) for row in logs),
        }

    def record_event(
        self,
        event_type: str,
        title: str,
        summary: str = "",
        *,
        surface: str = "unknown",
        files: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "id": uuid4().hex,
            "event_type": event_type,
            "title": redact_secrets(title),
            "summary": redact_secrets(summary),
            "surface": surface,
            "files": files or [],
            "metadata": self._redacted_jsonable(metadata or {}),
            "created_at": utc_now(),
            "app_version": APP_VERSION,
        }
        data = self.load()
        data["records"].append(record)
        data["records"] = data["records"][-MAX_RECORDS:]
        self.save(data)
        return record

    def save_text_snapshot(self, label: str, content: str, *, surface: str = "unknown", suffix: str = ".txt") -> str:
        name = safe_filename(label, "snapshot") + suffix
        target = self._dated_file_path(name)
        target.write_text(redact_secrets(content), encoding="utf-8")
        return self._record_file(target, label=label, source="text_snapshot", surface=surface)

    def save_file_bytes(self, filename: str, content: bytes, *, label: str, surface: str = "unknown") -> str:
        target = self._dated_file_path(safe_filename(filename))
        target.write_bytes(content)
        return self._record_file(target, label=label, source="uploaded_file", surface=surface)

    def copy_file(self, source_path: str | Path, *, label: str, surface: str = "unknown") -> str:
        source = Path(source_path)
        target = self._dated_file_path(safe_filename(source.name))
        shutil.copy2(source, target)
        return self._record_file(target, label=label, source="local_file", surface=surface)

    def save_export_bundle(self, files: dict[str, str], *, surface: str = "unknown") -> list[str]:
        ids: list[str] = []
        for filename, content in files.items():
            ids.append(self.save_text_snapshot(filename, content, surface=surface, suffix=""))
        return ids

    def recent_records(self, limit: int = 30) -> list[dict[str, Any]]:
        return list(reversed(self.load()["records"][-limit:]))

    def recent_tokens(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(reversed(self.load()["token_logs"][-limit:]))

    def recent_files(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(reversed(self.load()["files"][-limit:]))

    def onboarding_seen(self, surface: str) -> bool:
        state = self.load()["state"]
        return bool(state.get("onboarding_seen_surfaces", {}).get(surface))

    def mark_onboarding_seen(self, surface: str) -> None:
        data = self.load()
        data["state"].setdefault("onboarding_seen_surfaces", {})[surface] = utc_now()
        self.save(data)

    def update_notice_needed(self) -> bool:
        data = self.load()
        return data["state"].get("last_seen_version") != APP_VERSION

    def update_notice_text(self, lang: str) -> str:
        lines = release_note_lines(APP_VERSION, lang)
        if not lines:
            return ""
        prefix = "本次更新：" if lang == "zh" else "Update:"
        return prefix + "\n" + "\n".join(f"- {line}" for line in lines)

    def mark_version_seen(self) -> None:
        data = self.load()
        data["state"]["last_seen_version"] = APP_VERSION
        self.save(data)

    def _default_data(self) -> dict[str, Any]:
        now = utc_now()
        return {
            "schema_version": SCHEMA_VERSION,
            "app_version": APP_VERSION,
            "created_at": now,
            "updated_at": now,
            "profile": {"local_id": uuid4().hex},
            "state": {
                "onboarding_seen_surfaces": {},
                "last_seen_version": "",
            },
            "records": [],
            "token_logs": [],
            "files": [],
        }

    def _migrate(self, raw: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        data = raw if isinstance(raw, dict) else {}
        changed = False
        default = self._default_data()
        for key, value in default.items():
            if key not in data:
                data[key] = value
                changed = True
        if not isinstance(data.get("profile"), dict):
            data["profile"] = default["profile"]
            changed = True
        if not data["profile"].get("local_id"):
            data["profile"]["local_id"] = uuid4().hex
            changed = True
        if not isinstance(data.get("state"), dict):
            data["state"] = default["state"]
            changed = True
        data["state"].setdefault("onboarding_seen_surfaces", {})
        data["state"].setdefault("last_seen_version", "")
        for list_key in ("records", "token_logs", "files"):
            if not isinstance(data.get(list_key), list):
                data[list_key] = []
                changed = True
        if int(data.get("schema_version", 0) or 0) < SCHEMA_VERSION:
            data["schema_version"] = SCHEMA_VERSION
            changed = True
        data["app_version"] = APP_VERSION
        return data, changed

    def _dated_file_path(self, name: str) -> Path:
        date_dir = self.files_dir / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)
        return date_dir / f"{datetime.now().strftime('%H%M%S')}_{uuid4().hex[:8]}_{name}"

    def _record_file(self, path: Path, *, label: str, source: str, surface: str) -> str:
        file_record = {
            "id": uuid4().hex,
            "label": redact_secrets(label),
            "path": str(path),
            "name": path.name,
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "source": source,
            "surface": surface,
            "created_at": utc_now(),
            "app_version": APP_VERSION,
        }
        data = self.load()
        data["files"].append(file_record)
        data["files"] = data["files"][-MAX_FILES:]
        self.save(data)
        return file_record["id"]

    def _to_plain_dict(self, value: TokenLog | dict[str, Any]) -> dict[str, Any]:
        if is_dataclass(value):
            return self._redacted_jsonable(asdict(value))
        if isinstance(value, dict):
            return self._redacted_jsonable(value)
        return {}

    def _redacted_jsonable(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): self._redacted_jsonable(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._redacted_jsonable(item) for item in value]
        if isinstance(value, str):
            return redact_secrets(value)
        return value
