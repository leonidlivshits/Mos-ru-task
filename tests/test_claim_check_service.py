from app.services.claim_check import ClaimCheckService


def test_claim_check_verifies_private_feature() -> None:
    result = ClaimCheckService().verify(
        answer="Внутри была синяя папка",
        private_features=["синяя папка", "зарядное устройство"],
    )

    assert result.verified is True
    assert result.matched_count == 1


def test_claim_check_rejects_unrelated_answer() -> None:
    result = ClaimCheckService().verify(
        answer="Это был черный рюкзак",
        private_features=["синяя папка", "зарядное устройство"],
    )

    assert result.verified is False
    assert result.matched_count == 0
