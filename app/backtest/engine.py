from datetime import datetime
from sqlalchemy.orm import Session

from app.backtest.models import Trade
from app.db.models import MinuteBar
from app.report.daily_recommendation import generate_recommendation


def simulate_day(
    db: Session,
    ticker: str,
    trading_date,
    capital: float
):
    rec = generate_recommendation(ticker, capital)
    if not rec:
        return None

    required_keys = [
        "buy_time",
        "sell_time",
        "buy_price",
        "sell_price",
        "shares",
    ]

    if not all(k in rec for k in required_keys):
        return None

    buy_time = datetime.combine(trading_date, rec["buy_time"])
    sell_time = datetime.combine(trading_date, rec["sell_time"])
    shares = rec["shares"]

    if shares <= 0:
        return None

    buy_bar = db.query(MinuteBar).filter(
        MinuteBar.ticker == ticker,
        MinuteBar.ts == buy_time
    ).first()

    sell_bar = db.query(MinuteBar).filter(
        MinuteBar.ticker == ticker,
        MinuteBar.ts == sell_time
    ).first()

    if not buy_bar or not sell_bar:
        return None

    return Trade(
        ticker=ticker,
        buy_time=buy_time,
        buy_price=float(buy_bar.close),
        sell_time=sell_time,
        sell_price=float(sell_bar.close),
        shares=shares,
    )
