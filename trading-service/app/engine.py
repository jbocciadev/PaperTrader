
# Calculates outcome of a buy order
def calculate_buy_order(current_cash, shares, execution_price):
    total_cost = shares * execution_price
    if total_cost > current_cash:
        raise ValueError("Insufficient funds.")
    else:
        new_balance = current_cash - total_cost
        return (new_balance, total_cost)

# Retrieves the latest price from the Redis cache
def get_cached_price(redis_client, ticker):
    key = f"stock:{ticker}:price"
    cached_price = redis_client.get(key)
    # Check if the server can't find the ticker
    if cached_price is None:
        raise ValueError("Ticker price unavailable.")
    else:
        cached_price = float(cached_price)
        return cached_price

#  
def execute_buy_transaction(redis_client, current_cash, shares, ticker):
    cached_price = get_cached_price(redis_client, ticker)
    new_balance, total_cost = calculate_buy_order(current_cash, shares, cached_price)
    return new_balance, total_cost, cached_price

# Calculates outcome of a buy order
def calculate_sell_order(current_cash, held_shares, shares_to_sell, execution_price):
    if held_shares < shares_to_sell:
        raise ValueError("Insufficient shares to execute sell order.")
    
    total_proceeds = shares_to_sell * execution_price
    new_cash_balance = current_cash + total_proceeds
    return new_cash_balance, total_proceeds

def execute_sell_order(redis_client, current_cash, held_shares, shares_to_sell, ticker):
    cached_price = get_cached_price(redis_client, ticker)
    new_balance, total_proceeds = calculate_sell_order(current_cash, held_shares, shares_to_sell, cached_price)
    return new_balance, total_proceeds, cached_price
