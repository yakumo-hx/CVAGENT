from __future__ import annotations

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from dotenv import find_dotenv, load_dotenv

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.bullet_generator import generate_bullet_variants
from src.agents.evidence_matcher import build_evidence_matrix, gap_text, status_label
from src.agents.exporter import build_export_bundle
from src.agents.fact_extractor import extract_fact_card_from_answer
from src.agents.jd_analyzer import analyze_jd_fallback
from src.agents.llm_workflow import analyze_jd_with_deepseek, extract_fact_with_deepseek, parse_resume_with_deepseek
from src.agents.question_planner import pick_next_gap, plan_question
from src.agents.resume_parser import parse_resume_text_fallback
from src.config import APP_VERSION, DEFAULT_MODEL, SUPPORTED_MODELS
from src.deepseek_client import DeepSeekClient
from src.i18n import DEFAULT_LANG, LANGUAGES, t
from src.local_store import LocalStore
from src.schemas import FactCard, Metric
from src.security import mask_secret, redact_secrets
from src.utils.token_logger import TokenLog


class DesktopApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.lang = DEFAULT_LANG
        self.api_key = ""
        self.model = DEFAULT_MODEL
        self.resume_text = ""
        self.jd_text = ""
        self.master_resume = None
        self.jd_analysis = None
        self.matrix_rows = []
        self.fact_cards: list[FactCard] = []
        self.bullets = []
        self.token_logs: list[TokenLog] = []
        self.store = LocalStore()
        self.guide_tip_index = 0

        self.title(t("app.title", self.lang))
        self.geometry("1180x780")
        self.minsize(980, 680)
        self.configure(bg="#f7f8fb")
        self._configure_style()
        self._build_ui()
        self.after(500, self._show_startup_guidance)
        self.after(1000, self._rotate_guide_tip)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f7f8fb")
        style.configure("Panel.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("TLabel", background="#f7f8fb", foreground="#1f2937", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#f7f8fb", foreground="#111827", font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", background="#f7f8fb", foreground="#4b5563", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TNotebook", background="#f7f8fb", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 7), font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _build_ui(self) -> None:
        for child in self.winfo_children():
            child.destroy()

        top = ttk.Frame(self, padding=(14, 10))
        top.pack(fill=tk.X)
        ttk.Label(top, text=t("app.title", self.lang), style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(top, text=f"  {t('desktop.version', self.lang)}", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(8, 0))
        lang_box = ttk.Combobox(top, values=list(LANGUAGES.values()), state="readonly", width=12)
        lang_box.set(LANGUAGES[self.lang])
        lang_box.pack(side=tk.RIGHT)
        ttk.Label(top, text=t("language", self.lang), style="Subtitle.TLabel").pack(side=tk.RIGHT, padx=(0, 8))
        lang_box.bind("<<ComboboxSelected>>", lambda _event: self._set_language(lang_box.get()))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

        self._settings_tab()
        self._resume_tab()
        self._jd_tab()
        self._matrix_tab()
        self._interview_tab()
        self._evidence_tab()
        self._writer_tab()
        self._export_tab()
        self._history_tab()
        self._guide_bar()

    def _set_language(self, language_name: str) -> None:
        for code, name in LANGUAGES.items():
            if name == language_name:
                self.lang = code
                break
        self._build_ui()

    def _tab(self, key: str) -> ttk.Frame:
        frame = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(frame, text=t(key, self.lang))
        return frame

    def _settings_tab(self) -> None:
        tab = self._tab("nav.settings")
        self._hero(tab, t("nav.settings", self.lang), t("settings.subtitle", self.lang))

        form = ttk.Frame(tab)
        form.pack(fill=tk.X, pady=(8, 12))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text=t("settings.key", self.lang)).grid(row=0, column=0, sticky=tk.W, pady=6)
        self.key_var = tk.StringVar(value=self.api_key)
        ttk.Entry(form, textvariable=self.key_var, show="*", width=70).grid(row=0, column=1, sticky=tk.EW, padx=8)

        ttk.Label(form, text=t("settings.model", self.lang)).grid(row=1, column=0, sticky=tk.W, pady=6)
        self.model_var = tk.StringVar(value=self.model)
        ttk.Combobox(form, textvariable=self.model_var, values=list(SUPPORTED_MODELS), state="readonly").grid(
            row=1, column=1, sticky=tk.W, padx=8
        )

        buttons = ttk.Frame(tab)
        buttons.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(buttons, text=t("settings.save", self.lang), command=self._save_settings).pack(side=tk.LEFT)
        ttk.Button(buttons, text=t("settings.load_env", self.lang), command=self._load_env_key).pack(side=tk.LEFT, padx=8)
        ttk.Button(buttons, text=t("settings.forget", self.lang), command=self._forget_key).pack(side=tk.LEFT)
        ttk.Button(buttons, text=t("settings.test", self.lang), command=self._test_connection).pack(side=tk.LEFT, padx=8)

        self.settings_status = tk.StringVar(value=t("desktop.ready", self.lang))
        ttk.Label(tab, textvariable=self.settings_status, style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 12))

        self.token_frame = ttk.Frame(tab)
        self.token_frame.pack(fill=tk.X)
        self._render_token_panel()

        ttk.Label(tab, text=t("settings.data_boundary_body", self.lang), wraplength=900, style="Subtitle.TLabel").pack(
            anchor=tk.W, pady=(12, 0)
        )

    def _resume_tab(self) -> None:
        tab = self._tab("nav.resume")
        self._hero(tab, t("nav.resume", self.lang), t("resume.subtitle", self.lang))
        self.resume_textbox = self._text(tab, height=13)
        self.resume_textbox.insert("1.0", self.resume_text)
        controls = ttk.Frame(tab)
        controls.pack(fill=tk.X, pady=8)
        self.resume_llm = tk.BooleanVar(value=bool(self.api_key))
        ttk.Checkbutton(controls, text=t("resume.use_llm", self.lang), variable=self.resume_llm).pack(side=tk.LEFT)
        ttk.Button(controls, text=t("desktop.select_file", self.lang), command=self._load_resume_file).pack(side=tk.LEFT, padx=8)
        ttk.Button(controls, text=t("resume.parse", self.lang), command=self._parse_resume).pack(side=tk.LEFT)
        self.resume_output = self._text(tab, height=15)

    def _jd_tab(self) -> None:
        tab = self._tab("nav.jd")
        self._hero(tab, t("nav.jd", self.lang), t("jd.subtitle", self.lang))
        self.jd_textbox = self._text(tab, height=13)
        self.jd_textbox.insert("1.0", self.jd_text)
        controls = ttk.Frame(tab)
        controls.pack(fill=tk.X, pady=8)
        self.jd_llm = tk.BooleanVar(value=bool(self.api_key))
        ttk.Checkbutton(controls, text=t("jd.use_llm", self.lang), variable=self.jd_llm).pack(side=tk.LEFT)
        ttk.Button(controls, text=t("jd.analyze", self.lang), command=self._analyze_jd).pack(side=tk.LEFT, padx=8)
        self.jd_output = self._text(tab, height=15)

    def _matrix_tab(self) -> None:
        tab = self._tab("nav.matrix")
        self._hero(tab, t("nav.matrix", self.lang), t("matrix.subtitle", self.lang))
        ttk.Button(tab, text=t("matrix.build", self.lang), command=self._build_matrix).pack(anchor=tk.W, pady=(0, 8))
        columns = ("req", "evidence", "direct", "transfer", "adjacent", "impact", "score", "status", "gap")
        self.matrix_tree = ttk.Treeview(tab, columns=columns, show="headings", height=18)
        headings = {
            "req": t("matrix.req", self.lang),
            "evidence": t("matrix.evidence", self.lang),
            "direct": t("matrix.direct", self.lang),
            "transfer": t("matrix.transferable", self.lang),
            "adjacent": t("matrix.adjacent", self.lang),
            "impact": t("matrix.impact", self.lang),
            "score": t("matrix.score", self.lang),
            "status": t("matrix.status", self.lang),
            "gap": t("matrix.gap", self.lang),
        }
        widths = {"req": 260, "evidence": 300, "direct": 70, "transfer": 90, "adjacent": 80, "impact": 70, "score": 70, "status": 100, "gap": 230}
        for col in columns:
            self.matrix_tree.heading(col, text=headings[col])
            self.matrix_tree.column(col, width=widths[col], anchor=tk.W)
        self.matrix_tree.pack(fill=tk.BOTH, expand=True)
        self._refresh_matrix_tree()

    def _interview_tab(self) -> None:
        tab = self._tab("nav.interview")
        self._hero(tab, t("nav.interview", self.lang), t("interview.subtitle", self.lang))
        self.interview_prompt = tk.StringVar()
        ttk.Label(tab, textvariable=self.interview_prompt, wraplength=980, style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self._update_interview_prompt()
        self.answer_textbox = self._text(tab, height=8)
        controls = ttk.Frame(tab)
        controls.pack(fill=tk.X, pady=8)
        self.fact_llm = tk.BooleanVar(value=bool(self.api_key))
        ttk.Checkbutton(controls, text=t("interview.use_llm", self.lang), variable=self.fact_llm).pack(side=tk.LEFT)
        ttk.Button(controls, text=t("interview.create", self.lang), command=self._create_fact_card).pack(side=tk.LEFT, padx=8)
        self.fact_preview = self._text(tab, height=12)

    def _evidence_tab(self) -> None:
        tab = self._tab("nav.evidence")
        self._hero(tab, t("nav.evidence", self.lang), t("evidence.subtitle", self.lang))
        top = ttk.Frame(tab)
        top.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(top, text=t("evidence.confirm_all", self.lang), command=self._confirm_all_facts).pack(side=tk.LEFT)
        ttk.Button(top, text=t("evidence.delete", self.lang), command=self._delete_selected_fact).pack(side=tk.LEFT, padx=8)
        self.fact_list = tk.Listbox(tab, height=9, exportselection=False)
        self.fact_list.pack(fill=tk.X)
        self.fact_list.bind("<<ListboxSelect>>", lambda _event: self._load_selected_fact())
        editor = ttk.Frame(tab)
        editor.pack(fill=tk.BOTH, expand=True, pady=8)
        editor.columnconfigure(1, weight=1)
        self.fact_claim = tk.StringVar()
        self.fact_role = tk.StringVar()
        self.fact_tools = tk.StringVar()
        self.fact_metrics = tk.StringVar()
        self.fact_confirmed = tk.BooleanVar()
        ttk.Label(editor, text=t("evidence.claim", self.lang)).grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Entry(editor, textvariable=self.fact_claim).grid(row=0, column=1, sticky=tk.EW, pady=4)
        ttk.Label(editor, text=t("evidence.role", self.lang)).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.role_label_to_value = {
            t("role.none", self.lang): "",
            t("role.participated", self.lang): "参与",
            t("role.responsible", self.lang): "负责",
            t("role.led", self.lang): "主导",
        }
        ttk.Combobox(editor, textvariable=self.fact_role, values=list(self.role_label_to_value.keys()), state="readonly").grid(row=1, column=1, sticky=tk.W, pady=4)
        ttk.Label(editor, text=t("evidence.tools", self.lang)).grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(editor, textvariable=self.fact_tools).grid(row=2, column=1, sticky=tk.EW, pady=4)
        ttk.Label(editor, text=t("evidence.metrics", self.lang)).grid(row=3, column=0, sticky=tk.W, pady=4)
        ttk.Entry(editor, textvariable=self.fact_metrics).grid(row=3, column=1, sticky=tk.EW, pady=4)
        ttk.Checkbutton(editor, text=t("evidence.confirm", self.lang), variable=self.fact_confirmed).grid(row=4, column=1, sticky=tk.W, pady=4)
        ttk.Button(editor, text=t("settings.save", self.lang), command=self._save_fact_edits).grid(row=5, column=1, sticky=tk.W, pady=6)
        self._refresh_fact_list()

    def _writer_tab(self) -> None:
        tab = self._tab("nav.writer")
        self._hero(tab, t("nav.writer", self.lang), t("writer.subtitle", self.lang))
        controls = ttk.Frame(tab)
        controls.pack(fill=tk.X, pady=(0, 8))
        self.writer_requirement = tk.StringVar(value=self._default_writer_requirement())
        ttk.Entry(controls, textvariable=self.writer_requirement, width=90).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(controls, text=t("writer.use_gap", self.lang), command=self._use_next_gap_requirement).pack(side=tk.LEFT, padx=8)
        ttk.Button(controls, text=t("writer.generate", self.lang), command=self._generate_bullets).pack(side=tk.LEFT)
        self.writer_output = self._text(tab, height=24)
        self._render_bullets()

    def _export_tab(self) -> None:
        tab = self._tab("nav.export")
        self._hero(tab, t("nav.export", self.lang), t("export.subtitle", self.lang))
        ttk.Button(tab, text=t("desktop.export_dir", self.lang), command=self._export_files).pack(anchor=tk.W, pady=(0, 8))
        self.export_preview = self._text(tab, height=28)
        self._render_export_preview()

    def _history_tab(self) -> None:
        tab = self._tab("nav.history")
        self._hero(tab, t("nav.history", self.lang), t("history.subtitle", self.lang))
        summary = self.store.summary()
        ttk.Label(tab, text=f"{t('history.profile', self.lang)}: {summary['profile_id']}", style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Label(tab, text=f"{t('history.data_dir', self.lang)}: {summary['data_dir']}", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(2, 8))

        panels = ttk.Frame(tab)
        panels.pack(fill=tk.X, pady=(0, 10))
        values = [
            (t("history.records", self.lang), summary["records"]),
            (t("history.files", self.lang), summary["files"]),
            (t("token.lifetime_calls", self.lang), summary["lifetime_calls"]),
            (t("token.lifetime_total", self.lang), summary["lifetime_total_tokens"]),
        ]
        for label, value in values:
            panel = ttk.Frame(panels, style="Panel.TFrame", padding=10)
            panel.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
            ttk.Label(panel, text=label, background="#ffffff").pack(anchor=tk.W)
            ttk.Label(panel, text=str(value), background="#ffffff", font=("Segoe UI", 14, "bold")).pack(anchor=tk.W)

        text = self._text(tab, height=24)
        lines = [t("history.compat", self.lang), ""]
        if self.store.update_notice_needed():
            lines.extend([self.store.update_notice_text(self.lang), ""])
        lines.append(f"== {t('history.records', self.lang)} ==")
        records = self.store.recent_records(12)
        if records:
            for record in records:
                lines.append(f"- {record.get('created_at', '')} [{record.get('event_type', '')}] {record.get('title', '')} :: {record.get('summary', '')}")
        else:
            lines.append(t("history.empty_records", self.lang))
        lines.extend(["", f"== {t('history.files', self.lang)} =="])
        files = self.store.recent_files(12)
        if files:
            for item in files:
                lines.append(f"- {item.get('created_at', '')} {item.get('label', '')}: {item.get('path', '')}")
        else:
            lines.append(t("history.empty_files", self.lang))
        lines.extend(["", f"== {t('history.tokens', self.lang)} =="])
        tokens = self.store.recent_tokens(12)
        if tokens:
            for row in tokens:
                lines.append(f"- {row.get('created_at', '')} {row.get('prompt_name', '')}: {row.get('total_tokens', 0)} tokens")
        else:
            lines.append(t("token.none", self.lang))
        self._set_text(text, "\n".join(lines))

    def _guide_bar(self) -> None:
        bar = ttk.Frame(self, padding=(14, 0, 14, 8))
        bar.pack(fill=tk.X)
        self.guide_tip_var = tk.StringVar(value=t("guide.tip.1", self.lang))
        ttk.Button(bar, text=t("guide.mouse", self.lang), command=self._show_full_guide).pack(side=tk.RIGHT)
        ttk.Label(bar, textvariable=self.guide_tip_var, style="Subtitle.TLabel").pack(side=tk.RIGHT, padx=(0, 10))

    def _hero(self, parent: ttk.Frame, title: str, subtitle: str) -> None:
        ttk.Label(parent, text=title, style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(parent, text=subtitle, style="Subtitle.TLabel", wraplength=980).pack(anchor=tk.W, pady=(2, 14))

    def _text(self, parent: ttk.Frame, height: int) -> tk.Text:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=False)
        text = tk.Text(frame, height=height, wrap=tk.WORD, font=("Consolas", 10), undo=True)
        scroll = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        return text

    def _client(self) -> DeepSeekClient | None:
        if not self.api_key:
            return None
        return DeepSeekClient(api_key=self.api_key, model=self.model)

    def _save_settings(self) -> None:
        self.api_key = self.key_var.get().strip()
        self.model = self.model_var.get().strip() or DEFAULT_MODEL
        key_state = mask_secret(self.api_key) if self.api_key else t("key.missing", self.lang)
        self.settings_status.set(t("key.loaded", self.lang, key=key_state) if self.api_key else key_state)

    def _load_env_key(self) -> None:
        env_path = find_dotenv(usecwd=True)
        if env_path:
            load_dotenv(env_path, override=False)
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.key_var.set(self.api_key)
        self.settings_status.set(t("settings.loaded_env", self.lang, key=mask_secret(self.api_key)) if self.api_key else t("key.missing", self.lang))

    def _forget_key(self) -> None:
        self.api_key = ""
        self.key_var.set("")
        self.settings_status.set(t("settings.forgot", self.lang))

    def _test_connection(self) -> None:
        self._save_settings()
        client = self._client()
        if not client:
            messagebox.showwarning(t("desktop.info", self.lang), t("key.missing", self.lang))
            return
        try:
            result = client.guidance_message(self.lang)
            self._add_token_log(result.token_log)
            self.settings_status.set(result.content)
        except Exception as exc:
            messagebox.showerror(t("desktop.error", self.lang), t("settings.failed", self.lang, error=exc))

    def _add_token_log(self, log: TokenLog | None) -> None:
        if log:
            self.token_logs.append(log)
            self.store.append_token_log(log, surface="desktop")
            if hasattr(self, "token_frame"):
                self._render_token_panel()

    def _render_token_panel(self) -> None:
        for child in self.token_frame.winfo_children():
            child.destroy()
        total = sum(row.total_tokens for row in self.token_logs)
        input_tokens = sum(row.input_tokens for row in self.token_logs)
        output_tokens = sum(row.output_tokens for row in self.token_logs)
        calls = len(self.token_logs)
        values = [
            (t("token.calls", self.lang), calls),
            (t("token.input", self.lang), input_tokens),
            (t("token.output", self.lang), output_tokens),
            (t("token.total", self.lang), total),
            (t("token.lifetime_total", self.lang), self.store.token_summary()["lifetime_total_tokens"]),
        ]
        for label, value in values:
            panel = ttk.Frame(self.token_frame, style="Panel.TFrame", padding=12)
            panel.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
            ttk.Label(panel, text=label, background="#ffffff").pack(anchor=tk.W)
            ttk.Label(panel, text=str(value), background="#ffffff", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W)

    def _load_resume_file(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[(t("desktop.file_text", self.lang), "*.md *.txt"), (t("desktop.file_all", self.lang), "*.*")]
        )
        if not path:
            return
        self.store.copy_file(path, label="resume_file", surface="desktop")
        content = Path(path).read_text(encoding="utf-8", errors="ignore")
        self.resume_textbox.delete("1.0", tk.END)
        self.resume_textbox.insert("1.0", content)

    def _parse_resume(self) -> None:
        self.resume_text = self.resume_textbox.get("1.0", tk.END).strip()
        if not self.resume_text:
            messagebox.showwarning(t("desktop.info", self.lang), t("resume.empty", self.lang))
            return
        client = self._client() if self.resume_llm.get() else None
        if client:
            resume, log, warning = parse_resume_with_deepseek(self.resume_text, client, self.lang)
            self._add_token_log(log)
            if warning:
                messagebox.showwarning(t("desktop.info", self.lang), warning)
        else:
            resume = parse_resume_text_fallback(self.resume_text, self.lang)
        self.master_resume = resume
        file_id = self.store.save_text_snapshot("resume_parse", self.resume_text, surface="desktop")
        self.store.record_event(
            "resume_parse",
            t("resume.parsed", self.lang),
            f"{len(self.resume_text)} chars, projects={len(resume.projects)}, experiences={len(resume.experiences)}",
            surface="desktop",
            files=[file_id],
            metadata={"projects": len(resume.projects), "experiences": len(resume.experiences), "skills": len(resume.skills)},
        )
        self._set_text(self.resume_output, resume.model_dump_json(indent=2))

    def _analyze_jd(self) -> None:
        self.jd_text = self.jd_textbox.get("1.0", tk.END).strip()
        if not self.jd_text:
            messagebox.showwarning(t("desktop.info", self.lang), t("jd.empty", self.lang))
            return
        client = self._client() if self.jd_llm.get() else None
        if client:
            jd, log, warning = analyze_jd_with_deepseek(self.jd_text, client, self.lang)
            self._add_token_log(log)
            if warning:
                messagebox.showwarning(t("desktop.info", self.lang), warning)
        else:
            jd = analyze_jd_fallback(self.jd_text, self.lang)
        self.jd_analysis = jd
        file_id = self.store.save_text_snapshot("jd_analyze", self.jd_text, surface="desktop")
        self.store.record_event(
            "jd_analyze",
            t("jd.done", self.lang),
            f"{len(self.jd_text)} chars, must={len(jd.must_have_requirements)}, nice={len(jd.nice_to_have_requirements)}",
            surface="desktop",
            files=[file_id],
            metadata={"must_have": len(jd.must_have_requirements), "nice_to_have": len(jd.nice_to_have_requirements)},
        )
        self._set_text(self.jd_output, jd.model_dump_json(indent=2))

    def _build_matrix(self) -> None:
        if not self.master_resume or not self.jd_analysis:
            messagebox.showwarning(t("desktop.info", self.lang), t("desktop.run_workflow_first", self.lang))
            return
        self.matrix_rows = build_evidence_matrix(self.master_resume, self.jd_analysis, self.lang)
        self.store.record_event(
            "matrix_build",
            t("matrix.build", self.lang),
            f"{len(self.matrix_rows)} rows",
            surface="desktop",
            metadata={"rows": len(self.matrix_rows), "gaps": sum(1 for row in self.matrix_rows if row.score.status == "GAP")},
        )
        self._refresh_matrix_tree()
        self._update_interview_prompt()

    def _refresh_matrix_tree(self) -> None:
        if not hasattr(self, "matrix_tree"):
            return
        for item in self.matrix_tree.get_children():
            self.matrix_tree.delete(item)
        for row in self.matrix_rows:
            self.matrix_tree.insert(
                "",
                tk.END,
                values=(
                    row.requirement_text,
                    row.best_evidence_summary,
                    row.score.direct,
                    row.score.transferable,
                    row.score.adjacent,
                    row.score.impact,
                    row.score.total,
                    status_label(row.score.status, self.lang),
                    gap_text(row.score.status, self.lang),
                ),
            )

    def _update_interview_prompt(self) -> None:
        if not hasattr(self, "interview_prompt"):
            return
        target = pick_next_gap(self.matrix_rows)
        if not target:
            self.interview_prompt.set(t("interview.no_gap", self.lang))
            return
        plan = plan_question(target, self.lang)
        self.interview_prompt.set(
            f"{t('interview.current_gap', self.lang)}: {plan['requirement']}\n"
            f"{t('interview.question', self.lang)}: {plan['question']}\n"
            f"{t('interview.why', self.lang)}: {plan['why']}"
        )

    def _create_fact_card(self) -> None:
        target = pick_next_gap(self.matrix_rows)
        if not target:
            messagebox.showinfo(t("desktop.info", self.lang), t("interview.no_gap", self.lang))
            return
        answer = self.answer_textbox.get("1.0", tk.END).strip()
        if not answer:
            messagebox.showwarning(t("desktop.info", self.lang), t("interview.empty", self.lang))
            return
        fact_id = f"fact_{len(self.fact_cards) + 1:03d}"
        client = self._client() if self.fact_llm.get() else None
        if client:
            fact, log, warning = extract_fact_with_deepseek(
                answer,
                fact_id=fact_id,
                related_requirement=target.requirement_text,
                related_experience=target.best_evidence_summary,
                client=client,
                lang=self.lang,
            )
            self._add_token_log(log)
            if warning:
                messagebox.showwarning(t("desktop.info", self.lang), warning)
        else:
            fact = extract_fact_card_from_answer(
                answer,
                fact_id=fact_id,
                related_requirement=target.requirement_text,
                related_experience=target.best_evidence_summary,
                lang=self.lang,
            )
        self.fact_cards.append(fact)
        self.store.record_event(
            "fact_card",
            t("interview.created", self.lang, fact_id=fact_id),
            fact.claim,
            surface="desktop",
            metadata={"fact_id": fact_id, "requirement": target.requirement_text},
        )
        self._set_text(self.fact_preview, fact.model_dump_json(indent=2))
        self._refresh_fact_list()

    def _refresh_fact_list(self) -> None:
        if not hasattr(self, "fact_list"):
            return
        self.fact_list.delete(0, tk.END)
        for fact in self.fact_cards:
            marker = "✓" if fact.can_use_in_resume and not fact.needs_confirmation else "?"
            self.fact_list.insert(tk.END, f"{marker} {fact.fact_id} | {fact.claim}")

    def _selected_fact_index(self) -> int | None:
        if not hasattr(self, "fact_list"):
            return None
        selection = self.fact_list.curselection()
        return selection[0] if selection else None

    def _load_selected_fact(self) -> None:
        index = self._selected_fact_index()
        if index is None:
            return
        fact = self.fact_cards[index]
        self.fact_claim.set(fact.claim)
        value_to_label = {value: label for label, value in self.role_label_to_value.items()}
        self.fact_role.set(value_to_label.get(fact.role, ""))
        self.fact_tools.set(", ".join(fact.tools))
        self.fact_metrics.set(", ".join(metric.value or "" for metric in fact.metrics))
        self.fact_confirmed.set(fact.can_use_in_resume and not fact.needs_confirmation)

    def _save_fact_edits(self) -> None:
        index = self._selected_fact_index()
        if index is None:
            return
        fact = self.fact_cards[index]
        fact.claim = self.fact_claim.get().strip() or fact.claim
        fact.role = self.role_label_to_value.get(self.fact_role.get(), self.fact_role.get())
        fact.tools = [item.strip() for item in self.fact_tools.get().split(",") if item.strip()]
        fact.metrics = [
            Metric(type="user_metric", value=item.strip(), status="provided")
            for item in self.fact_metrics.get().split(",")
            if item.strip()
        ]
        fact.can_use_in_resume = self.fact_confirmed.get()
        fact.needs_confirmation = not fact.can_use_in_resume
        self._refresh_fact_list()

    def _confirm_all_facts(self) -> None:
        for fact in self.fact_cards:
            fact.can_use_in_resume = True
            fact.needs_confirmation = False
        self._refresh_fact_list()

    def _delete_selected_fact(self) -> None:
        index = self._selected_fact_index()
        if index is None:
            return
        del self.fact_cards[index]
        self._refresh_fact_list()

    def _default_writer_requirement(self) -> str:
        target = pick_next_gap(self.matrix_rows)
        return target.requirement_text if target else ""

    def _use_next_gap_requirement(self) -> None:
        self.writer_requirement.set(self._default_writer_requirement())

    def _generate_bullets(self) -> None:
        requirement = self.writer_requirement.get().strip()
        if not requirement:
            messagebox.showwarning(t("desktop.info", self.lang), t("writer.no_requirement", self.lang))
            return
        self.bullets = generate_bullet_variants(self.fact_cards, requirement=requirement, lang=self.lang)
        self.store.record_event(
            "bullet_generation",
            t("writer.generate", self.lang),
            requirement,
            surface="desktop",
            metadata={"bullets": len(self.bullets), "facts": len(self.fact_cards)},
        )
        self._render_bullets()
        self._render_export_preview()

    def _render_bullets(self) -> None:
        if not hasattr(self, "writer_output"):
            return
        lines = []
        for bullet in self.bullets:
            variant_label = t(f"writer.variant.{bullet.variant}", self.lang)
            lines.append(f"[{variant_label}] {bullet.text}")
            lines.append(f"{t('writer.fact_ids', self.lang)}: {', '.join(bullet.fact_ids) or t('common.none', self.lang)}")
            if bullet.risk:
                lines.append(f"{t('evidence.risk', self.lang)}: {bullet.risk}")
            lines.append("")
        self._set_text(self.writer_output, "\n".join(lines))

    def _export_bundle(self):
        return build_export_bundle(
            bullets=self.bullets,
            facts=self.fact_cards,
            jd=self.jd_analysis,
            matrix_rows=self.matrix_rows,
            lang=self.lang,
        )

    def _render_export_preview(self) -> None:
        if not hasattr(self, "export_preview"):
            return
        self._set_text(self.export_preview, self._export_bundle().tailored_resume_md)

    def _export_files(self) -> None:
        folder = filedialog.askdirectory()
        if not folder:
            return
        bundle = self._export_bundle()
        outputs = {
            "tailored_resume.md": bundle.tailored_resume_md,
            "evidence_cards.json": bundle.evidence_cards_json,
            "jd_analysis.json": bundle.jd_analysis_json,
            "gap_report.md": bundle.gap_report_md,
            "interview_prep.md": bundle.interview_prep_md,
        }
        export_path = Path(folder)
        for name, content in outputs.items():
            (export_path / name).write_text(redact_secrets(content), encoding="utf-8")
        file_ids = self.store.save_export_bundle(outputs, surface="desktop")
        self.store.record_event(
            "export_bundle",
            t("nav.export", self.lang),
            str(export_path),
            surface="desktop",
            files=file_ids,
            metadata={"file_count": len(outputs)},
        )
        messagebox.showinfo(t("desktop.info", self.lang), t("desktop.export_done", self.lang, path=export_path))

    def _set_text(self, widget: tk.Text, content: str) -> None:
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)

    def _show_startup_guidance(self) -> None:
        if not self.store.onboarding_seen("desktop"):
            self._show_full_guide()
            self.store.mark_onboarding_seen("desktop")
            return
        if self.store.update_notice_needed():
            messagebox.showinfo(
                t("guide.update_title", self.lang),
                f"{self.store.update_notice_text(self.lang)}\n\nCVAGENT {APP_VERSION}",
            )
            self.store.mark_version_seen()

    def _show_full_guide(self) -> None:
        messagebox.showinfo(
            t("guide.welcome_title", self.lang),
            f"{t('guide.welcome_body', self.lang)}\n\n{t('guide.feedback', self.lang)}",
        )

    def _rotate_guide_tip(self) -> None:
        if hasattr(self, "guide_tip_var"):
            keys = ["guide.tip.1", "guide.tip.2", "guide.tip.3", "guide.tip.4"]
            self.guide_tip_var.set(f"{t(keys[self.guide_tip_index % len(keys)], self.lang)}  {t('guide.feedback', self.lang)}")
            self.guide_tip_index += 1
        self.after(12000, self._rotate_guide_tip)


def main() -> None:
    app = DesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
