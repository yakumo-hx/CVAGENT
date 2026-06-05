# Bullet Generator Prompt

Generate resume bullets only from confirmed fact cards.

Rules:
- Every bullet must cite `fact_ids`.
- If metrics are missing, use placeholders such as `[待补充指标]`.
- Do not invent numbers, dates, users, revenue, rankings, or awards.
- Do not turn participation into leadership unless the fact card confirms it.

Return JSON matching a list of `ResumeBullet`.
