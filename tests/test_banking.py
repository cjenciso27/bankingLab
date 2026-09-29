"""Tests for the interactive banking menu."""

import pytest

from banking import menu


def test_menu_exits(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "0")

    menu()

    captured = capsys.readouterr()
    assert "Secure Banking System" in captured.out
    assert "Goodbye." in captured.out


def test_menu_creates_customer_account_and_deposit(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    responses = iter(
        [
            "1",
            "Ana Rojas",
            "1990-05-05",
            "2",
            "1",
            "1234567890",
            "USD",
            "checking",
            "50",
            "3",
            "1",
            "1234567890",
            "25",
            "7",
            "1",
            "0",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

    menu()

    captured = capsys.readouterr()
    assert "Customer created. User ID: 1" in captured.out
    assert "Account 1234567890 added" in captured.out
    assert "New balance: 75.00 USD" in captured.out
    assert "Total balance for Ana Rojas: 75.00" in captured.out


def test_menu_rejects_numeric_currency(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    responses = iter(
        [
            "1",
            "Ana Rojas",
            "1990-05-05",
            "2",
            "1",
            "1234567890",
            "100",
            "8",
            "0",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

    menu()

    captured = capsys.readouterr()
    assert "is not a currency code" in captured.out
    assert "No accounts." in captured.out
