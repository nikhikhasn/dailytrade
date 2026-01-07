from sqlalchemy import func
from datetime import time

from app.db.engine import init_engine
from app.db.session import SessionLocal
from app.db.models import MinuteBar
from app.db.models_daily import DailySummary


def minute_to_bucket(ts):
    """
    Convert time to 15-minute bucket index.
    Market opens at 9:30 → bucket 0
    """
    minutes_since_open = (ts.hour * 60 + ts.minute) - (9 * 60 + 30)
    return max(0, min(25, minutes_since_open // 15))


def main():
    init_engine()
    db = SessionLocal()

    try:
        rows = (
            db.query(
                MinuteBar.ticker,
                func.date(MinuteBar.ts).label("trading_date"),
            )
            .distinct()
            .all()
        )

        for ticker, trading_date in rows:
            bars = (
                db.query(MinuteBar)
                .filter(
                    MinuteBar.ticker == ticker,
                    func.date(MinuteBar.ts) == trading_date,
                )
                .order_by(MinuteBar.ts)
                .all()
            )

            opens = bars[0]
            closes = bars[-1]

            high_bar = max(bars, key=lambda b: b.high)
            low_bar = min(bars, key=lambda b: b.low)

            range_pct = float((high_bar.high - low_bar.low) / opens.open)

            summary = DailySummary(
                ticker=ticker,
                trading_date=trading_date,
                open=opens.open,
                high=high_bar.high,
                low=low_bar.low,
                close=closes.close,
                range_pct=range_pct,
                low_bucket=minute_to_bucket(low_bar.ts),
                high_bucket=minute_to_bucket(high_bar.ts),
            )

            db.merge(summary)

        db.commit()
        print("✅ Daily summaries generated")

    finally:
        db.close()


if __name__ == "__main__":
    main()
