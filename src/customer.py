"""Customer model that owns one or more bank accounts."""

import logging
from datetime import UTC, date, datetime

from bank_account import BankAccount
from insufficient_funds_error import InsufficientFundsError

logger = logging.getLogger(__name__)


class Customer:
    """A bank customer who must be at least 18 years old.

    User identifiers come from the class-wide ``user_count`` counter.
    Accounts are stored in a private list.
    """

    user_count = 0

    def __init__(self, name: str, birth_date: date | datetime | str) -> None:
        if not isinstance(name, str):
            logger.error("Customer name must be a string. Received: %r", name)
            raise TypeError("Customer name must be a string")
        if not name.strip():
            logger.error("Customer name cannot be empty")
            raise ValueError("Customer name cannot be empty")
        parsed_birth_date = self.parse_birth_date(birth_date)
        if not self.is_of_legal_age(parsed_birth_date):
            logger.error(
                "Customer '%s' must be at least 18 years old. Birth date: %s",
                name.strip(),
                parsed_birth_date.isoformat(),
            )
            raise ValueError("Customer must be at least 18 years old")
        self._name = name.strip()
        self._birth_date = parsed_birth_date
        self._user_id = self._assign_user_id()
        self.__accounts: list[BankAccount] = []

    @property
    def name(self) -> str:
        """Return the customer name."""
        return self._name

    @property
    def birth_date(self) -> date:
        """Return the customer birth date."""
        return self._birth_date

    @property
    def user_id(self) -> int:
        """Return the protected consecutive user id."""
        return self._user_id

    @property
    def accounts(self) -> list[BankAccount]:
        """Return a copy of the private account list."""
        return list(self.__accounts)

    @classmethod
    def get_user_count(cls) -> int:
        """Return how many customers have been created."""
        return cls.user_count

    @classmethod
    def _assign_user_id(cls) -> int:
        """Reserve the next consecutive user id."""
        cls.user_count += 1
        return cls.user_count

    @staticmethod
    def parse_birth_date(birth_date: date | datetime | str) -> date:
        """Normalize a date, datetime, or ISO string into a date."""
        if isinstance(birth_date, datetime):
            return birth_date.date()
        if isinstance(birth_date, date):
            return birth_date
        if isinstance(birth_date, str):
            try:
                return date.fromisoformat(birth_date.strip())
            except ValueError as error:
                logger.error("Invalid birth date: %s", birth_date)
                raise ValueError("Birth date must use the YYYY-MM-DD format") from error
        logger.error("Unsupported birth date value: %r", birth_date)
        raise TypeError("Birth date must be a date or an ISO date string")

    @staticmethod
    def is_of_legal_age(birth_date: date, today: date | None = None) -> bool:
        """Return True when the birth date corresponds to a person 18 or older."""
        current_day = today or datetime.now(UTC).astimezone().date()
        if birth_date > current_day:
            return False
        age = (
            current_day.year
            - birth_date.year
            - (
                (current_day.month, current_day.day)
                < (birth_date.month, birth_date.day)
            )
        )
        return age >= 18

    def add_account(self, account: BankAccount) -> bool:
        """Append an account when its number contains exactly 10 digits."""
        if not isinstance(account, BankAccount):
            logger.error("Only BankAccount instances can be added")
            return False
        if not BankAccount.is_valid_account_number(account.account_number):
            logger.error(
                "Rejected account %s for customer %s: account number must contain exactly 10 digits",
                account.account_number,
                self._user_id,
            )
            return False
        if any(
            existing.account_number == account.account_number
            for existing in self.__accounts
        ):
            logger.error(
                "Customer %s already has account %s",
                self._user_id,
                account.account_number,
            )
            return False
        self.__accounts.append(account)
        logger.info(
            "Account %s added to customer %s",
            account.account_number,
            self._user_id,
        )
        return True

    def get_total_balance(self) -> float:
        """Return the sum of every account balance owned by this customer."""
        return round(sum(account.balance for account in self.__accounts), 2)

    def transfer(
        self,
        amount: float,
        source_account: BankAccount,
        target_account: BankAccount,
    ) -> None:
        """Move funds between two accounts owned by this customer.

        The withdrawal rules of the source account stay in force. If those
        rules reject the movement, the error is logged and no deposit is made.
        """
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            logger.error("Transfer amount must be a number. Received: %r", amount)
            raise TypeError("Transfer amount must be a number")
        if amount < 0:
            logger.error("Transfer amount must be non-negative. Received: %s", amount)
            raise ValueError("Transfer amount must be non-negative")
        if (
            source_account not in self.__accounts
            or target_account not in self.__accounts
        ):
            logger.error(
                "Transfer rejected for customer %s: both accounts must belong to the customer",
                self._user_id,
            )
            raise ValueError("Both accounts must belong to the customer")
        if source_account is target_account:
            logger.error(
                "Transfer rejected for customer %s: source and target are the same account",
                self._user_id,
            )
            raise ValueError("Cannot transfer to the same account")
        try:
            source_account.withdraw(amount)
        except (InsufficientFundsError, ValueError) as error:
            logger.error("Transfer rejected: %s", error)
            raise
        try:
            target_account.deposit(amount)
        except ValueError:
            source_account.deposit(amount)
            logger.error(
                "Transfer rejected while depositing into account %s",
                target_account.account_number,
            )
            raise
        logger.info(
            "Transferred %.2f from %s to %s for customer %s",
            round(float(amount), 2),
            source_account.account_number,
            target_account.account_number,
            self._user_id,
        )
