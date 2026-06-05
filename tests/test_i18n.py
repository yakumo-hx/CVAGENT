from src.agents.bullet_generator import generate_bullet_variants
from src.agents.exporter import build_export_bundle
from src.i18n import DEFAULT_LANG, t
from src.schemas import FactCard, Metric


def test_default_language_is_chinese():
    assert DEFAULT_LANG == "zh"
    assert t("nav.settings") == "设置"


def test_english_generation_and_export_labels():
    fact = FactCard(
        fact_id="fact_001",
        claim="built a local resume evidence workflow",
        role="lead",
        tools=["Python"],
        metrics=[Metric(value="3 modules", status="provided")],
        can_use_in_resume=True,
        needs_confirmation=False,
    )

    bullets = generate_bullet_variants([fact], requirement="local agent workflow", lang="en")
    bundle = build_export_bundle(bullets=bullets, facts=[fact], jd=None, matrix_rows=[], lang="en")

    assert "[To fill]" not in bullets[0].text
    assert "Fact IDs" in bundle.tailored_resume_md
    assert "# Tailored Resume Bullets" in bundle.tailored_resume_md
