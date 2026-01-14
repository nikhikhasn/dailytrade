from datetime import datetime

class SimpleMomentumStrategy:
    def __init__(self, daily_gate):
        self.daily_gate = daily_gate
        self.last_signal = None

    def on_trade(self, trade, broker):
        now = datetime.fromtimestamp(trade.timestamp.timestamp())
        window = self.daily_gate.get_active_window(now)

        if not window or window == self.last_signal:
            return

        if window == "BUY":
            print("🟢 BUY WINDOW ACTIVE")
        elif window == "SELL":
            print("🔴 SELL WINDOW ACTIVE")

        self.last_signal = window
