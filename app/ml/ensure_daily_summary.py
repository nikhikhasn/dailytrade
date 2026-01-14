from sqlalchemy import func
from app.db.session import SessionLocal
from app.db.models_daily import DailySummary


MIN_DAYS = 5


def ensure_daily_summary(symbol: str):
    """
    Ensures daily_summary has enough rows for Layer A.
    Currently does NOT fetch external data.
    This is intentional and safe.
    """

    session = SessionLocal()

    count = (
        session.query(func.count(DailySummary.trading_date))
        .filter(DailySummary.ticker == symbol)
        .scalar()
    )

    session.close()

    if count >= MIN_DAYS:
        return

    print(
        f"⚠️ {symbol} has only {count} daily rows. "
        "Layer A may be disabled until data is populated."
    )
