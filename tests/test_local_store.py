import json

from src.config import APP_VERSION
from src.local_store import LocalStore, SCHEMA_VERSION
from src.utils.token_logger import TokenLog


def test_local_store_migrates_legacy_data(tmp_path):
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps({"schema_version": 0, "token_logs": []}), encoding="utf-8")

    store = LocalStore(tmp_path)
    data = store.load()

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["app_version"] == APP_VERSION
    assert data["profile"]["local_id"]
    assert isinstance(data["records"], list)
    assert isinstance(data["files"], list)


def test_local_store_records_tokens_events_and_files(tmp_path):
    store = LocalStore(tmp_path)
    store.append_token_log(TokenLog(prompt_name="unit", model="deepseek", input_tokens=3, output_tokens=4, total_tokens=7), surface="test")
    file_id = store.save_text_snapshot("resume", "hello", surface="test")
    record = store.record_event("resume_parse", "Parsed", "hello", surface="test", files=[file_id])

    summary = store.summary()

    assert summary["lifetime_calls"] == 1
    assert summary["lifetime_total_tokens"] == 7
    assert summary["records"] == 1
    assert summary["files"] == 1
    assert store.recent_records()[0]["id"] == record["id"]
    assert store.recent_files()[0]["id"] == file_id


def test_local_store_update_notice(tmp_path):
    store = LocalStore(tmp_path)

    assert store.update_notice_needed()
    assert "本次更新" in store.update_notice_text("zh")

    store.mark_version_seen()

    assert not store.update_notice_needed()
