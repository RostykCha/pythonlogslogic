from helper import trades_for_account

user_trades = trades_for_account("2|3")
for tr in user_trades:
    print(tr)
