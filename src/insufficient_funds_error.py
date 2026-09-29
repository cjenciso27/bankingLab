"""Custom exception raised when a withdrawal cannot be completed."""


class InsufficientFundsError(Exception):
    """Raised when an account cannot cover the requested withdrawal.

    Args:
        message: Explanation of why the withdrawal was rejected.
        amount: Withdrawal amount that could not be completed.
    """

    def __init__(self, message: str, amount: float) -> None:
        self.amount = amount
        super().__init__(message)
