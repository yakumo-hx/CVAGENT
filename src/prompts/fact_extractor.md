# Fact Extractor Prompt

Convert a user answer into a fact card.

Rules:
- Do not write unsupported claims.
- Keep raw facts separate from resume-ready bullets.
- Extract role, tools, metrics, outcome, risk, and confidence.
- Default `needs_confirmation` to true.

Return JSON matching `FactCard`.
