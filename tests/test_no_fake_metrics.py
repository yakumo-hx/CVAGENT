from src.agents.bullet_generator import generate_bullet_variants
from src.agents.risk_auditor import has_unsupported_metrics
from src.schemas import FactCard


def test_missing_metrics_use_placeholder_not_fake_numbers():
    fact = FactCard(
        fact_id="fact_001",
        claim="设计了本地简历证据挖掘流程",
        role="负责",
        tools=["Python"],
        can_use_in_resume=True,
        needs_confirmation=False,
    )

    bullets = generate_bullet_variants([fact], requirement="LLM Agent workflow")

    assert all("300%" not in bullet.text for bullet in bullets)
    assert any("[待补充结果/指标]" in bullet.text for bullet in bullets)
    assert all(not has_unsupported_metrics(bullet, [fact]) for bullet in bullets)
