"""Tests for BankAccount behavior."""

import logging

import pytest

from bank_account import BankAccount
from insufficient_funds_error import InsufficientFundsError


@pytest.fixture
def checking_account() -> BankAccount:
    return BankAccount("1234567890", "USD", "checking", 250)


def test_currency_must_be_usd_or_crc(caplog: pytest.LogCaptureFixture) -> None:
    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match="USD or CRC"),
    ):
        BankAccount("1234567890", "100", "checking", 50)

    assert "Invalid currency code" in caplog.text
    with pytest.raises(ValueError, match="USD or CRC"):
        BankAccount("1234567890", "EUR", "checking", 50)


def test_constructor_defaults_and_getters() -> None:
    account = BankAccount("1234567890")

    assert account.account_number == "1234567890"
    assert account.currency == "USD"
    assert account.account_type == "checking"
    assert account.balance == 0.0


def test_balance_setter_rejects_negative_values(
    caplog: pytest.LogCaptureFixture,
) -> None:
    account = BankAccount("1234567890", balance=40)

    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match="cannot be negative"),
    ):
        account.balance = -1

    assert account.balance == 40
    assert "Rejected negative balance" in caplog.text


def test_deposit_updates_balance_and_logs_info(
    checking_account: BankAccount,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        checking_account.deposit(25)

    assert checking_account.balance == 275
    assert "Updated balance: 275.00" in caplog.text


def test_deposit_rejects_negative_amount(
    checking_account: BankAccount,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match="non-negative"),
    ):
        checking_account.deposit(-10)

    assert checking_account.balance == 250
    assert "Deposit amount must be non-negative" in caplog.text


def test_withdraw_updates_balance(
    checking_account: BankAccount,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        checking_account.withdraw(50)

    assert checking_account.balance == 200
    assert "Updated balance: 200.00" in caplog.text


def test_withdraw_rejects_insufficient_funds(
    checking_account: BankAccount,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(InsufficientFundsError) as error_info,
    ):
        checking_account.withdraw(300)

    assert error_info.value.amount == 300
    assert checking_account.balance == 250
    assert "Insufficient funds" in caplog.text


def test_withdraw_rejects_negative_amount(checking_account: BankAccount) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        checking_account.withdraw(-5)

    assert checking_account.balance == 250


def test_checking_account_can_fall_below_savings_minimum() -> None:
    account = BankAccount("1234567890", balance=150)

    account.withdraw(80)

    assert account.balance == 70


def test_savings_withdrawal_cannot_fall_below_minimum(
    caplog: pytest.LogCaptureFixture,
) -> None:
    account = BankAccount.create_savings("1234567890", "USD", 150)

    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(InsufficientFundsError) as error_info,
    ):
        account.withdraw(60)

    assert error_info.value.amount == 60
    assert account.balance == 150
    assert "savings minimum" in caplog.text


def test_savings_withdrawal_can_leave_exactly_the_minimum() -> None:
    account = BankAccount.create_savings("1234567890", "crc", 180)

    account.withdraw(80)

    assert account.account_type == "savings"
    assert account.currency == "CRC"
    assert account.balance == 100


def test_create_savings_rejects_opening_balance_below_minimum(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match="cannot be less than"),
    ):
        BankAccount.create_savings("1234567890", "USD", 99.99)

    assert "initial balance" in caplog.text


def test_direct_savings_constructor_also_enforces_minimum() -> None:
    with pytest.raises(ValueError, match="cannot be less than"):
        BankAccount("1234567890", "CRC", "savings", 50)


def test_convert_currency_prints_converted_balance(
    checking_account: BankAccount,
    capsys: pytest.CaptureFixture[str],
) -> None:
    converted = checking_account.convert_currency("crc", 0.9)
    captured = capsys.readouterr()

    assert converted == 225
    assert captured.out.strip() == "Balance in CRC: 225.00"


def test_convert_currency_rejects_non_positive_rate(
    checking_account: BankAccount,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match="greater than zero"),
    ):
        checking_account.convert_currency("CRC", 0)

    assert "Exchange rate" in caplog.text
    with pytest.raises(ValueError, match="USD or CRC"):
        checking_account.convert_currency("100", 0.9)
    with pytest.raises(ValueError, match="greater than zero"):
        checking_account.convert_currency("CRC", -1.5)


@pytest.mark.parametrize(
    ("account_number", "expected"),
    [
        ("1234567890", True),
        ("0000000001", True),
        ("123456789", False),
        ("12345678901", False),
        ("12345abcde", False),
        ("", False),
        (None, False),
        (1234567890, False),
    ],
)
def test_is_valid_account_number(account_number: object, expected: bool) -> None:
    assert BankAccount.is_valid_account_number(account_number) is expected
