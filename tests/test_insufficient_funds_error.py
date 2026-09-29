"""Tests for the custom insufficient-funds exception."""

import pytest

from insufficient_funds_error import InsufficientFundsError


def test_exception_stores_message_and_amount() -> None:
    error = InsufficientFundsError("Not enough funds", 80.0)

    assert isinstance(error, Exception)
    assert str(error) == "Not enough funds"
    assert error.amount == 80.0


def test_exception_can_be_raised() -> None:
    with pytest.raises(InsufficientFundsError) as error_info:
        raise InsufficientFundsError("Withdrawal rejected", 25.5)

    assert error_info.value.amount == 25.5
