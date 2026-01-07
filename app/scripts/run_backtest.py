from datetime import date, timedelta

from app.db.session import SessionLocal
from app.backtest.engine import simulate_day
from app.backtest.metrics import summarize


def main():
    db = SessionLocal()

    tickers = ["PLTR", "SOFI", "F"]
    capital = 50

    start = date(2026, 1, 2)
    end = date(2026, 1, 6)

    trades = []

    d = start
    while d <= end:
        for ticker in tickers:
            trade = simulate_day(db, ticker, d, capital)
            if trade:
                trades.append(trade)
        d += timedelta(days=1)

    summary = summarize(trades)

    print("\n📊 Backtest Summary\n")
    for k, v in summary.items():
        print(f"{k}: {v}")

    db.close()


if __name__ == "__main__":
    main()
