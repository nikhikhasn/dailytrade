from dataclasses import dataclass
from datetime import datetime

@dataclass
class Trade:
    ticker: str
    buy_time: datetime
    buy_price: float
    sell_time: datetime
    sell_price: float
    shares: int

    @property
    def pnl(self) -> float:
        return (self.sell_price - self.buy_price) * self.shares

    @property
    def return_pct(self) -> float:
        return (self.sell_price - self.buy_price) / self.buy_price
