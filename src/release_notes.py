from __future__ import annotations


RELEASE_NOTES: dict[str, dict[str, list[str]]] = {
    "0.1.1": {
        "zh": [
            "新增本地资料库：保存提交记录、文件快照和历史 token 消耗。",
            "新增本地引导：首次打开介绍页面用途，后续在右下角轮询简短提示。",
            "新增更新提示：拉取新版后会展示本次准备好的更新说明。",
            "兼容策略：本地资料库使用 schema_version 迁移，旧字段缺失会自动补齐。",
        ],
        "en": [
            "Added a local library for submission records, file snapshots, and historical token usage.",
            "Added local guidance with first-run page descriptions and rotating bottom-right tips.",
            "Added update notices shown after pulling a new version.",
            "Compatibility: local data uses schema_version migrations and fills missing fields automatically.",
        ],
    },
    "0.1.0": {
        "zh": ["MVP：DeepSeek 简历证据工作流，包含 Web 和桌面 exe 两个版本。"],
        "en": ["MVP: DeepSeek resume evidence workflow with Web and desktop exe versions."],
    },
}


def release_note_lines(version: str, lang: str) -> list[str]:
    notes = RELEASE_NOTES.get(version, {})
    return notes.get(lang) or notes.get("zh") or []
