class PaperBroker:
    def __init__(self, starting_cash=10_000):
        self.cash = starting_cash
        self.position = 0        # number of shares
        self.entry_price = None
        self.trades = []

    def buy(self, price, shares=1):
        cost = price * shares
        if self.cash < cost:
            return False

        self.cash -= cost
        self.position += shares
        self.entry_price = price

        self.trades.append({
            "type": "BUY",
            "price": price,
            "shares": shares,
        })

        print(f"🟢 BUY {shares} @ {price:.2f}")
        return True

    def sell(self, price):
        if self.position == 0:
            return False

        shares = self.position
        pnl = (price - self.entry_price) * shares

        self.cash += price * shares
        self.position = 0
        self.entry_price = None

        self.trades.append({
            "type": "SELL",
            "price": price,
            "shares": shares,
            "pnl": pnl,
        })

        print(f"🔴 SELL {shares} @ {price:.2f} | PnL: {pnl:.2f}")
        return pnl

    def equity(self, current_price):
        return self.cash + self.position * current_price
