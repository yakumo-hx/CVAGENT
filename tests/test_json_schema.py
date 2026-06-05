import pytest
from pydantic import ValidationError

from src.schemas import FactCard


def test_fact_card_rejects_empty_claim():
    with pytest.raises(ValidationError):
        FactCard(fact_id="fact_001", claim="  ")
