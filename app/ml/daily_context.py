import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.db.session import SessionLocal


def load_daily_context(ticker: str):
    """
    Attempt to load daily features for Layer A.
    If unavailable, return None and allow system to continue.
    """

    session = SessionLocal()

    query = text("""
        SELECT
            range_lag1,
            volatility_lag1,
            volume_lag1,
            range_mean_3,
            range_std_3
        FROM daily_features
        WHERE ticker = :ticker
        ORDER BY trading_date DESC
        LIMIT 1
    """)

    try:
        df = pd.read_sql(query, session.bind, params={"ticker": ticker})
    except ProgrammingError:
        print("⚠️ Daily features table not found — Layer A disabled")
        session.close()
        return None
    finally:
        session.close()

    if df.empty:
        print("⚠️ No daily features for today — Layer A disabled")
        return None

    return df
