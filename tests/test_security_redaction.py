from src.agents.exporter import build_export_bundle
from src.security import contains_secret, mask_secret, redact_secrets
from src.schemas import FactCard


def test_redacts_deepseek_key_pattern():
    fake_key = "ds-" + "1234567890abcdef"
    text = f"my key is {fake_key}"

    assert "[REDACTED_SECRET]" in redact_secrets(text)
    assert contains_secret(text)


def test_mask_secret_keeps_edges_only():
    masked = mask_secret("ds-" + "1234567890abcdef")

    assert masked.startswith("ds-123")
    assert masked.endswith("cdef")
    assert "7890" not in masked


def test_export_bundle_redacts_secret_like_fact_content():
    fake_key = "ds-" + "1234567890abcdef"
    fact = FactCard(
        fact_id="fact_001",
        claim=f"accidentally pasted {fake_key}",
        can_use_in_resume=True,
        needs_confirmation=False,
    )

    bundle = build_export_bundle(bullets=[], facts=[fact], jd=None, matrix_rows=[])

    assert fake_key not in bundle.evidence_cards_json
    assert "[REDACTED_SECRET]" in bundle.evidence_cards_json
