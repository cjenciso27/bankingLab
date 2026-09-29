"""Bank account model with encapsulated balance rules."""

import logging

from insufficient_funds_error import InsufficientFundsError

logger = logging.getLogger(__name__)


class BankAccount:
    """A single bank account with checking or savings rules.

    Public data is exposed through getters. The balance is private and can
    only change through its setter, deposits, and withdrawals.
    """

    SAVINGS_MINIMUM_BALANCE = 100.0

    def __init__(
        self,
        account_number: str,
        currency: str = "USD",
        account_type: str = "checking",
        balance: float = 0.0,
    ) -> None:
        self._account_number = str(account_number)
        if not self.is_valid_currency(currency):
            logger.error("Invalid currency code: %r", currency)
            raise ValueError(
                "Currency must be USD or CRC. "
                "Do not enter the balance in the currency field."
            )
        self._currency = currency.strip().upper()
        normalized_type = account_type.strip().lower()
        if normalized_type not in {"checking", "savings"}:
            logger.error("Unsupported account type: %s", account_type)
            raise ValueError("Account type must be 'checking' or 'savings'")
        self._account_type = normalized_type
        self.__balance = 0.0
        if self._account_type == "savings" and balance < self.minimum_savings_balance(
            self._currency
        ):
            logger.error(
                "Savings account requires an initial balance of at least %.2f %s. "
                "Received: %s",
                self.minimum_savings_balance(self._currency),
                self._currency,
                balance,
            )
            raise ValueError(
                "Savings account initial balance cannot be less than "
                f"{self.minimum_savings_balance(self._currency):.2f} {self._currency}"
            )
        self.balance = balance

    @property
    def account_number(self) -> str:
        """Return the public account number."""
        return self._account_number

    @property
    def currency(self) -> str:
        """Return the public currency code."""
        return self._currency

    @property
    def account_type(self) -> str:
        """Return the protected account type."""
        return self._account_type

    @property
    def balance(self) -> float:
        """Return the private balance."""
        return self.__balance

    @balance.setter
    def balance(self, value: float) -> None:
        """Set the balance when the target value is non-negative."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            logger.error("Balance must be a number. Received: %r", value)
            raise TypeError("Balance must be a number")
        if value < 0:
            logger.error("Rejected negative balance: %s", value)
            raise ValueError("Balance cannot be negative")
        self.__balance = round(float(value), 2)

    @classmethod
    def minimum_savings_balance(cls, currency: str = "USD") -> float:
        """Return the savings floor for a currency.

        A savings balance cannot fall below $100. The laboratory also applies
        that floor to other currencies. No exchange-rate feed is supplied, so
        the equivalent reserve is 100 units of the account currency.
        """
        if not isinstance(currency, str) or not currency.strip():
            logger.error("A currency code is required to calculate the savings minimum")
            raise ValueError("A currency code is required")
        return cls.SAVINGS_MINIMUM_BALANCE

    @classmethod
    def create_savings(
        cls,
        account_number: str,
        currency: str = "USD",
        balance: float = 0.0,
    ) -> "BankAccount":
        """Create a savings account.

        The initial balance cannot be lower than the savings minimum.
        """
        minimum = cls.minimum_savings_balance(currency)
        if isinstance(balance, bool) or not isinstance(balance, (int, float)):
            logger.error(
                "Savings initial balance must be a number. Received: %r", balance
            )
            raise TypeError("Savings initial balance must be a number")
        if balance < minimum:
            logger.error(
                "Savings account requires an initial balance of at least %.2f %s. "
                "Received: %s",
                minimum,
                currency,
                balance,
            )
            raise ValueError(
                "Savings account initial balance cannot be less than "
                f"{minimum:.2f} {currency.strip().upper()}"
            )
        return cls(account_number, currency, "savings", balance)

    @staticmethod
    def is_valid_currency(currency: str) -> bool:
        """Return True only for USD or CRC."""
        return isinstance(currency, str) and currency.strip().upper() in {"USD", "CRC"}

    @staticmethod
    def is_valid_account_number(account_number: str) -> bool:
        """Return True only when the account number is exactly 10 digits."""
        return (
            isinstance(account_number, str)
            and account_number.isdigit()
            and len(account_number) == 10
        )

    def deposit(self, amount: float) -> None:
        """Add a non-negative amount to the balance."""
        validated_amount = self._validate_amount(amount, "Deposit")
        self.balance += validated_amount
        logger.info(
            "Deposit of %.2f %s completed. Updated balance: %.2f",
            validated_amount,
            self.currency,
            self.balance,
        )

    def withdraw(self, amount: float) -> None:
        """Remove a non-negative amount when the account rules allow it."""
        validated_amount = self._validate_amount(amount, "Withdrawal")
        projected_balance = round(self.balance - validated_amount, 2)
        minimum = self.minimum_savings_balance(self.currency)
        if self._account_type == "savings" and projected_balance < minimum:
            message = (
                f"Withdrawal of {validated_amount:.2f} {self.currency} would leave "
                f"{projected_balance:.2f}, below the savings minimum of {minimum:.2f}"
            )
            logger.error(message)
            raise InsufficientFundsError(message, validated_amount)
        if validated_amount > self.balance:
            message = (
                f"Insufficient funds to withdraw {validated_amount:.2f} {self.currency}. "
                f"Current balance: {self.balance:.2f}"
            )
            logger.error(message)
            raise InsufficientFundsError(message, validated_amount)
        self.balance = projected_balance
        logger.info(
            "Withdrawal of %.2f %s completed. Updated balance: %.2f",
            validated_amount,
            self.currency,
            self.balance,
        )

    def convert_currency(self, target_currency: str, exchange_rate: float) -> float:
        """Print and return the balance converted with the given exchange rate."""
        if not self.is_valid_currency(target_currency):
            logger.error("Invalid target currency code: %r", target_currency)
            raise ValueError("Target currency must be USD or CRC")
        if isinstance(exchange_rate, bool) or not isinstance(
            exchange_rate, (int, float)
        ):
            logger.error("Exchange rate must be a number. Received: %r", exchange_rate)
            raise TypeError("Exchange rate must be a number")
        if exchange_rate <= 0:
            logger.error(
                "Exchange rate must be greater than zero. Received: %s",
                exchange_rate,
            )
            raise ValueError("Exchange rate must be greater than zero")
        converted = round(self.balance * float(exchange_rate), 2)
        normalized_currency = target_currency.strip().upper()
        print(f"Balance in {normalized_currency}: {converted:.2f}")
        return converted

    def _validate_amount(self, amount: float, operation: str) -> float:
        """Reject amounts that are not non-negative numbers."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            logger.error("%s amount must be a number. Received: %r", operation, amount)
            raise TypeError(f"{operation} amount must be a number")
        if amount < 0:
            logger.error(
                "%s amount must be non-negative. Received: %s",
                operation,
                amount,
            )
            raise ValueError(f"{operation} amount must be non-negative")
        return round(float(amount), 2)
