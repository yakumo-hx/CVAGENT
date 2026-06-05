from src.agents.risk_auditor import audit_bullet
from src.schemas import ResumeBullet


def test_formal_bullet_requires_fact_id():
    bullet = ResumeBullet(
        variant="standard",
        text="负责构建简历证据挖掘流程。",
        fact_ids=[],
    )

    findings = audit_bullet(bullet, [])

    assert any(finding.code == "fact_id_required" for finding in findings)
