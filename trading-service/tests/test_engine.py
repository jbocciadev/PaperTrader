import pytest

from app.engine import calculate_buy_order

def test_calculate_buy_order_success():
    """Given enough balanec, the order should succeed and return the new balance."""
    current_cash = 1000.0
    shares = 5
    execution_price = 100.0

    new_balance, total_cost = calculate_buy_order(current_cash, shares, execution_price)

    assert total_cost == 500.0
    assert new_balance == 500.0

def test_calculate_buy_order_insufficient_funds():
    """If total cost exceeds current balance, it must raise a ValueError."""
    current_cash = 100.0
    shares = 5
    execution_price = 100.0

    with pytest.raises(ValueError, match="Insufficient funds"):
        calculate_buy_order(current_cash, shares, execution_price)