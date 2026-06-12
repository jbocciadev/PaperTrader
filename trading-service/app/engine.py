

def calculate_buy_order(current_cash, shares, execution_price):
    total_cost = shares * execution_price
    if total_cost > current_cash:
        raise ValueError("Insufficient funds.")
    else:
        new_balance = current_cash - total_cost
        return (new_balance, total_cost)

def get_cached_price(redis_client, ticker):
    key = f"stock:{ticker}:price"
    cached_price = redis_client.get(key)
    # Check if the server can't find the ticker
    if cached_price is None:
        raise ValueError("Ticker price unavailable.")
    else:
        cached_price = float(cached_price)
        return cached_price
    
def execute_buy_transaction(redis_client, current_cash, shares, ticker):
    cached_price = get_cached_price(redis_client, ticker)
    return calculate_buy_order(current_cash, shares, cached_price)