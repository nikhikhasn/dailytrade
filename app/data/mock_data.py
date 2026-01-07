import random
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")

def generate_intraday_minutes(trading_date):
    """Generate all NYSE minute timestamps for one trading day."""
    start = datetime.combine(trading_date, time(9, 30), tzinfo=NY)
    minutes = []
    for i in range(390):  # 6.5 trading hours
        minutes.append(start + timedelta(minutes=i))
    return minutes


def generate_mock_day(ticker: str, trading_date):
    """
    Generate realistic OHLCV minute bars for a single day.
    """
    minutes = generate_intraday_minutes(trading_date)

    price = random.uniform(10, 30)  # <$30 universe
    daily_vol = random.uniform(0.5, 2.5) / 100  # 0.5%–2.5%

    rows = []
    for ts in minutes:
        drift = random.uniform(-daily_vol, daily_vol)
        open_p = price
        close_p = max(1.0, price * (1 + drift))
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.001))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.001))
        volume = random.randint(500, 5000)

        rows.append({
            "ticker": ticker,
            "ts": ts,
            "open": round(open_p, 4),
            "high": round(high_p, 4),
            "low": round(low_p, 4),
            "close": round(close_p, 4),
            "volume": volume,
        })

        price = close_p

    return rows
