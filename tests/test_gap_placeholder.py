from src.agents.bullet_generator import generate_bullet_variants


def test_gap_outputs_placeholder_instead_of_formal_bullet():
    bullets = generate_bullet_variants([], requirement="DeepSeek API integration")

    assert len(bullets) == 1
    assert bullets[0].variant == "placeholder"
    assert "[待补充]" in bullets[0].text
    assert bullets[0].fact_ids == []
