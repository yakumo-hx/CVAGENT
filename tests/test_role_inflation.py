from src.agents.risk_auditor import has_role_inflation
from src.schemas import FactCard, ResumeBullet


def test_participation_cannot_become_leadership():
    fact = FactCard(
        fact_id="fact_001",
        claim="参与了项目资料整理",
        role="参与",
        can_use_in_resume=True,
        needs_confirmation=False,
    )
    bullet = ResumeBullet(
        variant="standard",
        text="主导项目资料整理并推动团队交付。",
        fact_ids=["fact_001"],
    )

    assert has_role_inflation(bullet, [fact])
