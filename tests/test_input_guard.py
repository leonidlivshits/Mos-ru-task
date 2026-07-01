from datetime import date, timedelta

import pytest

from app.services.input_guard import InputGuard, InputGuardError


def test_input_guard_cleans_description_whitespace() -> None:
    guard = InputGuard()

    description = guard.clean_description("  черный    рюкзак   Nike  ")

    assert description == "черный рюкзак Nike"


def test_input_guard_rejects_too_short_description() -> None:
    guard = InputGuard()

    with pytest.raises(InputGuardError):
        guard.clean_description("рюкзак")


def test_input_guard_rejects_future_date() -> None:
    guard = InputGuard()

    with pytest.raises(InputGuardError):
        guard.validate_lost_date(date.today() + timedelta(days=1))


def test_input_guard_rejects_obvious_injection_patterns() -> None:
    guard = InputGuard()

    with pytest.raises(InputGuardError):
        guard.clean_description("черный рюкзак Nike; drop table found_items")
