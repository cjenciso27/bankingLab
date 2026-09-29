"""Interactive secure banking system."""

import logging

from bank_account import BankAccount
from customer import Customer
from insufficient_funds_error import InsufficientFundsError


def configure_logging() -> None:
    """Show timestamps, log levels, and messages for INFO and ERROR events."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def menu() -> None:
    """Run the banking menu until the user chooses to exit."""
    configure_logging()
    customers: list[Customer] = []
    actions = {
        "1": lambda: _add_customer(customers),
        "2": lambda: _add_account(customers),
        "3": lambda: _deposit(customers),
        "4": lambda: _withdraw(customers),
        "5": lambda: _convert_currency(customers),
        "6": lambda: _transfer(customers),
        "7": lambda: _show_total_balance(customers),
        "8": lambda: _list_customers(customers),
    }
    while True:
        print(
            "\nSecure Banking System\n"
            "1. Add customer\n"
            "   Register a person. The program assigns a User ID. Write that number down.\n"
            "2. Add bank account\n"
            "   Open a checking or savings account for an existing User ID.\n"
            "3. Deposit\n"
            "   Add money to one account.\n"
            "4. Withdraw\n"
            "   Take money from one account.\n"
            "5. Convert currency\n"
            "   Show the balance in another currency. The account balance does not change.\n"
            "6. Transfer\n"
            "   Move money between two accounts of the same customer.\n"
            "7. Show total balance\n"
            "   Add up every account owned by one customer.\n"
            "8. List customers\n"
            "   Show each User ID and that customer's accounts.\n"
            "0. Exit"
        )
        choice = input("Select an option (0-8): ").strip()
        if choice == "0":
            print("Goodbye.")
            break
        action = actions.get(choice)
        if action is None:
            print("Invalid option.")
            continue
        try:
            action()
        except (TypeError, ValueError, InsufficientFundsError) as error:
            print(f"Operation failed: {error}")


def _add_customer(customers: list[Customer]) -> None:
    print(
        "\nAdd a customer\n"
        "Enter the full name, then the birth date as year-month-day.\n"
        "Example birth date: 1996-11-27. The customer must be 18 or older.\n"
        "After this step, use the User ID shown on screen. It is not the account number."
    )
    name = input("Full name: ").strip()
    birth_date = input("Birth date (YYYY-MM-DD): ").strip()
    customer = Customer(name, birth_date)
    customers.append(customer)
    print(f"Customer created. User ID: {customer.user_id}")


def _add_account(customers: list[Customer]) -> None:
    print(
        "\nAdd a bank account\n"
        "User ID: the number assigned when the customer was created, for example 1.\n"
        "Account number: exactly 10 digits, for example 1234567890.\n"
        "Currency: USD or CRC. Press Enter to use USD.\n"
        "This field is the kind of money, not the amount. Do not type 100 here.\n"
        "Account type: checking, or savings. Press Enter to use checking.\n"
        "Initial balance: the amount of money. A savings account requires at least 100."
    )
    customer = _prompt_customer(customers)
    account_number = input("Account number (exactly 10 digits): ").strip()
    currency = _prompt_currency()
    account_type = (
        input("Account type (checking or savings) [checking]: ").strip().lower()
        or "checking"
    )
    initial_balance = float(
        input("Initial balance (amount of money, for example 100.00): ").strip() or "0"
    )
    if account_type == "savings":
        account = BankAccount.create_savings(account_number, currency, initial_balance)
    elif account_type == "checking":
        account = BankAccount(account_number, currency, account_type, initial_balance)
    else:
        raise ValueError("Account type must be 'checking' or 'savings'")
    if customer.add_account(account):
        print(f"Account {account.account_number} added to user {customer.user_id}.")
        return
    print("Account was not added. The account number must contain exactly 10 digits.")


def _deposit(customers: list[Customer]) -> None:
    print("\nDeposit\nAdd a positive amount of money to an existing account.")
    customer = _prompt_customer(customers)
    account = _prompt_account(customer)
    amount = float(input("Amount to deposit (for example 25.00): ").strip())
    account.deposit(amount)
    print(f"New balance: {account.balance:.2f} {account.currency}")


def _withdraw(customers: list[Customer]) -> None:
    print(
        "\nWithdraw\n"
        "Take money out of an existing account.\n"
        "A savings account must keep at least 100 in its currency."
    )
    customer = _prompt_customer(customers)
    account = _prompt_account(customer)
    amount = float(input("Amount to withdraw (for example 25.00): ").strip())
    account.withdraw(amount)
    print(f"New balance: {account.balance:.2f} {account.currency}")


def _convert_currency(customers: list[Customer]) -> None:
    print(
        "\nConvert currency\n"
        "This only displays the balance in another currency. It does not move money.\n"
        "Target currency: USD or CRC.\n"
        "Exchange rate: how many units of the target currency equal 1 unit "
        "of the account currency. Example: 0.92"
    )
    customer = _prompt_customer(customers)
    account = _prompt_account(customer)
    target_currency = input("Target currency (USD or CRC): ").strip()
    if not BankAccount.is_valid_currency(target_currency):
        raise ValueError("Target currency must be USD or CRC")
    exchange_rate = float(
        input("Exchange rate (number greater than 0, for example 0.92): ").strip()
    )
    account.convert_currency(target_currency, exchange_rate)


def _transfer(customers: list[Customer]) -> None:
    print(
        "\nTransfer\n"
        "Move money from one account to another account of the same customer.\n"
        "Both account numbers must already belong to that User ID."
    )
    customer = _prompt_customer(customers)
    print("Source account: the account that sends the money.")
    source_account = _prompt_account(customer)
    print("Target account: the account that receives the money.")
    target_account = _prompt_account(customer)
    amount = float(input("Amount to transfer (for example 25.00): ").strip())
    customer.transfer(amount, source_account, target_account)
    print(
        "Transfer completed. "
        f"Source balance: {source_account.balance:.2f} {source_account.currency}. "
        f"Target balance: {target_account.balance:.2f} {target_account.currency}."
    )


def _show_total_balance(customers: list[Customer]) -> None:
    customer = _prompt_customer(customers)
    print(f"Total balance for {customer.name}: {customer.get_total_balance():.2f}")


def _list_customers(customers: list[Customer]) -> None:
    if not customers:
        print("No customers registered.")
        return
    for customer in customers:
        print(
            f"User {customer.user_id}: {customer.name} "
            f"(born {customer.birth_date.isoformat()})"
        )
        if not customer.accounts:
            print("  No accounts.")
            continue
        for account in customer.accounts:
            print(
                f"  {account.account_number} | {account.account_type} | "
                f"{account.balance:.2f} {account.currency}"
            )


def _prompt_currency() -> str:
    """Read USD or CRC, using USD when the field is left blank."""
    currency_input = input("Currency (USD or CRC) [USD]: ").strip()
    currency = currency_input or "USD"
    if BankAccount.is_valid_currency(currency):
        return currency
    raise ValueError(
        "Currency must be USD or CRC. "
        f"'{currency_input}' is not a currency code. "
        "Type the amount of money in Initial balance, not in Currency."
    )


def _prompt_customer(customers: list[Customer]) -> Customer:
    user_id = int(
        input("User ID (number assigned when the customer was created): ").strip()
    )
    for customer in customers:
        if customer.user_id == user_id:
            return customer
    raise ValueError(f"No customer found with user ID {user_id}")


def _prompt_account(customer: Customer) -> BankAccount:
    account_number = input("Account number (exactly 10 digits): ").strip()
    for account in customer.accounts:
        if account.account_number == account_number:
            return account
    raise ValueError(f"Customer {customer.user_id} has no account {account_number}")


if __name__ == "__main__":
    menu()
