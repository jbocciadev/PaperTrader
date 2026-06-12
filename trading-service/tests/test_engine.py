import pytest
from unittest.mock import MagicMock

from app.engine import calculate_buy_order
from app.engine import get_cached_price
from app.engine import execute_buy_transaction

# Test happy path
def test_get_cached_price_success():
    """Given a ticker, this funcion should query it from Redis and return the price as a float."""

    # Create the fake Redis server
    mock_redis = MagicMock()
    # Configure the fake server to return a fake string payload
    mock_redis.get.return_value = b"150.25" # Return data as bytes

    # Call the fuction
    price = get_cached_price(mock_redis, "AAPL")

    # Compare results
    assert price == 150.25
    # Check the fake server was queried correctly
    mock_redis.get.assert_called_once_with("stock:AAPL:price")

# Test for server missing ticker
def test_get_cached_price_missing_ticker():
    """Given a ticker that is not present in the Redis server, it should raise a Value error to be handled gracefully."""

    # Set up mock server
    mock_redis = MagicMock()
    mock_redis.get.return_value = None # Simulating a payload for a missing ticker

    # Check if this raises an error
    with pytest.raises(ValueError, match="Ticker price unavailable."):
        get_cached_price(mock_redis, "INVALID_TICKER")


# Test for happy path scenario, funds are sufficiant
def test_calculate_buy_order_success():
    """Given enough balanec, the order should succeed and return the new balance."""
    # Set up test variables
    current_cash = 1000.0
    shares = 5
    execution_price = 100.0

    # Call the function to be tested
    new_balance, total_cost = calculate_buy_order(current_cash, shares, execution_price)

    # Compare returned values with expected result
    assert total_cost == 500.0
    assert new_balance == 500.0

# Test for ValueError due to insufficient funds
def test_calculate_buy_order_insufficient_funds():
    """If total cost exceeds current balance, it must raise a ValueError."""
    # Set up vars
    current_cash = 100.0
    shares = 5
    execution_price = 100.0

    # Check if these values raise an error
    with pytest.raises(ValueError, match="Insufficient funds"):
        calculate_buy_order(current_cash, shares, execution_price)

def test_execute_buy_transaction():
    """This should fetch the latest price from Redis and execute the transaction."""

    # Create the fake Redis server
    mock_redis = MagicMock()
    # Configure the fake server to return a fake string payload
    mock_redis.get.return_value = b"100.0" # Return data as bytes

    # Set up variables for test
    current_cash = 1000.0
    shares = 5
    ticker = "AAPL"

    # Call function to e tested
    new_balance, total_cost = execute_buy_transaction(mock_redis, current_cash, shares, ticker)

    # Assertions
    assert total_cost == 500.0
    assert new_balance == 500.0
