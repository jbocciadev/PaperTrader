

def calculate_buy_order(current_cash, shares, execution_price):
    total_cost = shares * execution_price
    if total_cost > current_cash:
        raise ValueError("Insufficient funds")
    else:
        new_balance = current_cash - total_cost
        return (new_balance, total_cost)
