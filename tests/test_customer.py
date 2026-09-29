"""Tests for Customer behavior."""

import logging
from datetime import UTC, date, datetime, timedelta

import pytest

from bank_account import BankAccount
from customer import Customer
from insufficient_funds_error import InsufficientFundsError


def _system_today() -> date:
    return datetime.now(UTC).astimezone().date()


def _birth_date_for_age(years: int, extra_days: int = 0) -> date:
    today = _system_today()
    try:
        birthday = today.replace(year=today.year - years)
    except ValueError:
        birthday = today.replace(year=today.year - years, day=28)
    return birthday + timedelta(days=extra_days)


@pytest.fixture
def adult() -> Customer:
    return Customer("Ana Rojas", _birth_date_for_age(30))


def test_adult_customer_receives_consecutive_user_id(adult: Customer) -> None:
    second = Customer("Luis Mora", "1998-04-12")

    assert adult.user_id == 1
    assert second.user_id == 2
    assert adult.name == "Ana Rojas"
    assert adult.accounts == []
    assert Customer.get_user_count() == 2


def test_customer_must_be_at_least_18(caplog: pytest.LogCaptureFixture) -> None:
    underage = _birth_date_for_age(18, extra_days=1)

    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match="at least 18"),
    ):
        Customer("Minor", underage)

    assert "at least 18" in caplog.text
    assert Customer.get_user_count() == 0


def test_customer_is_accepted_on_18th_birthday() -> None:
    customer = Customer("Adult", _birth_date_for_age(18))

    assert customer.user_id == 1
    assert Customer.is_of_legal_age(customer.birth_date)


def test_add_account_accepts_valid_number(adult: Customer) -> None:
    account = BankAccount("1234567890", balance=80)

    assert adult.add_account(account) is True
    assert adult.accounts == [account]


def test_add_account_rejects_invalid_number(
    adult: Customer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    account = BankAccount("123", balance=80)

    with caplog.at_level(logging.ERROR):
        added = adult.add_account(account)

    assert added is False
    assert adult.accounts == []
    assert "exactly 10 digits" in caplog.text


def test_get_total_balance_sums_accounts(adult: Customer) -> None:
    adult.add_account(BankAccount("1234567890", balance=80))
    adult.add_account(BankAccount.create_savings("0987654321", "USD", 120))

    assert adult.get_total_balance() == 200


def test_transfer_moves_funds_between_customer_accounts(adult: Customer) -> None:
    source = BankAccount("1234567890", balance=200)
    target = BankAccount("0987654321", balance=40)
    adult.add_account(source)
    adult.add_account(target)

    adult.transfer(70, source, target)

    assert source.balance == 130
    assert target.balance == 110
    assert adult.get_total_balance() == 240


def test_transfer_keeps_balances_when_funds_are_insufficient(
    adult: Customer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = BankAccount("1234567890", balance=30)
    target = BankAccount("0987654321", balance=40)
    adult.add_account(source)
    adult.add_account(target)

    with caplog.at_level(logging.ERROR), pytest.raises(InsufficientFundsError):
        adult.transfer(80, source, target)

    assert source.balance == 30
    assert target.balance == 40
    assert "Transfer rejected" in caplog.text


def test_transfer_respects_savings_minimum(
    adult: Customer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = BankAccount.create_savings("1234567890", "USD", 150)
    target = BankAccount("0987654321", balance=10)
    adult.add_account(source)
    adult.add_account(target)

    with caplog.at_level(logging.ERROR), pytest.raises(InsufficientFundsError):
        adult.transfer(60, source, target)

    assert source.balance == 150
    assert target.balance == 10
    assert "Transfer rejected" in caplog.text


def test_transfer_rejects_accounts_that_do_not_belong_to_customer(
    adult: Customer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    owned = BankAccount("1234567890", balance=200)
    external = BankAccount("0987654321", balance=20)
    adult.add_account(owned)

    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ValueError, match="belong to the customer"),
    ):
        adult.transfer(15, owned, external)

    assert owned.balance == 200
    assert external.balance == 20
