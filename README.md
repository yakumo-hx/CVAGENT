# Resume Evidence Agent

一个中文优先、本地运行、DeepSeek-only 的简历证据挖掘 Agent。

它不是普通的 AI 简历模板工具，而是一个 evidence-first workflow：

```text
JD analysis -> evidence gap matrix -> branching interview -> fact cards -> grounded resume bullets
```

## Why This Project

多数 AI 简历工具会直接改写文本。这个项目先追问事实，再生成简历内容：

- 分析目标 JD 的显性要求、隐性要求和面试风险
- 对照简历经历，识别强证据、弱证据和缺证据
- 对弱证据逐步追问 scope、role、tools、metrics、outcomes
- 把用户回答沉淀为可确认的 fact cards
- 只使用已确认事实生成简历 bullet
- 每条 bullet 绑定 `fact_id`，避免无证据夸大

## Features

- Bring your own DeepSeek API key
- Single resume + single JD MVP workflow
- Resume library parsing scaffold
- JD analyzer scaffold
- Evidence matrix with confidence scoring
- Branching interview design
- Fact cards with confirmation state
- Grounded bullet generator
- Risk auditor for unsupported metrics and role inflation
- Markdown / JSON / HTML export scaffold

## Quick Start

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The current workspace has Python 3.10-compatible scaffolding. Python 3.11+ is recommended for development.

## Privacy

- This project runs locally.
- The user provides their own DeepSeek API key.
- Resume and JD text are sent to DeepSeek API only when the user triggers model calls.
- This project does not upload data to any author-owned server.
- Local databases, logs, uploads, exports, and private research notes are ignored by git.

## Limitations

- No BOSS / 58 / Zhaopin / Liepin crawler.
- No automatic job application.
- No automatic recruiter messaging.
- No OpenAI, Claude, Gemini, or multi-model provider in MVP.
- No DOCX/PDF export in v0.1.
- AI output must be reviewed and confirmed by the user.

## Roadmap

```text
v0.1
- single JD workflow
- DeepSeek settings
- resume/JD parsing
- evidence matrix
- branching interview
- fact cards
- grounded bullets
- Markdown/JSON/HTML export

v0.2
- multi-JD batch workflow
- shared discovery
- token/cost logs
- DOCX export
- versioned resume library

v0.3
- browser extension for user-visible JD capture
- interview story library
- STAR answer generation
- public portfolio/demo mode
```

## Attribution

This project is inspired by the workflow ideas of `resume-tailoring-skill` and the evidence-first UX pattern seen in AI interview style resume products. It does not copy proprietary product code or data.
