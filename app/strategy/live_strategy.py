from collections import deque


class SimpleMomentumStrategy:
    def __init__(self, window=5):
        self.prices = deque(maxlen=window)

    def update(self, price):
        self.prices.append(price)

        if len(self.prices) < self.prices.maxlen:
            return "HOLD"

        avg_price = sum(self.prices) / len(self.prices)

        if price > avg_price:
            return "BUY"
        elif price < avg_price:
            return "SELL"
        else:
            return "HOLD"
