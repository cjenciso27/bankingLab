# Secure Banking System

Python laboratory for SOFT-753, Automation with Python. The program manages customers and bank accounts with object-oriented design, custom errors, logging, and automated tests.

## Project layout

| Path | Responsibility |
| --- | --- |
| `src/insufficient_funds_error.py` | `InsufficientFundsError` |
| `src/bank_account.py` | `BankAccount` |
| `src/customer.py` | `Customer` |
| `src/banking.py` | Logging setup, menu, and program entry point |
| `tests/` | pytest suite |
| `.github/workflows/ci.yml` | Ruff and pytest on every pull request |

Each class lives in its own module. `src/banking.py` only coordinates the menu.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

`logging`, `time`, and `os` belong to the Python standard library, so they are not installed from PyPI. The third-party tools required by the laboratory are `pytest` and `ruff`.

## Setup

From the project folder:

```bash
uv sync
```

## Run the program

```bash
uv run python src/banking.py
```

The menu can register customers, open checking or savings accounts, deposit, withdraw, display a currency conversion, transfer between a customer's accounts, and show a customer's total balance.

A savings account must be opened with at least 100 units of its currency, and a withdrawal cannot leave it below that reserve. The laboratory describes this reserve as $100 or the equivalent amount in another currency. Because the activity does not provide an exchange-rate service, the reserve is 100 units of the account currency. `convert_currency()` uses the exchange rate entered by the caller and only prints the converted balance.

## Quality checks

Run the same commands that the GitHub Actions workflow runs:

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```

Use `uv run ruff format --check .` when you only want to verify formatting.

## Continuous integration

`.github/workflows/ci.yml` runs on pull requests. It installs the locked dependencies with `uv sync --frozen`, then executes:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```
