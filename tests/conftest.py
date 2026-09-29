"""Shared fixtures for the banking laboratory tests."""

from collections.abc import Iterator

import pytest

from customer import Customer


@pytest.fixture(autouse=True)
def reset_customer_counter() -> Iterator[None]:
    """Keep consecutive user ids independent between tests."""
    Customer.user_count = 0
    yield
    Customer.user_count = 0
