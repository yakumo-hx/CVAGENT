# Risk Auditor Prompt

Audit generated bullets for unsupported claims.

Flag:
- missing `fact_ids`
- unsupported metrics
- role inflation
- unsupported tools
- unsupported outcomes
- vague or unverifiable claims

Return JSON matching a list of `RiskFinding`.
