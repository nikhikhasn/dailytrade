import pandas as pd
import numpy as np
from sqlalchemy import text

from app.db.session import SessionLocal
from app.db.engine import init_engine


def load_daily_data():
    engine = init_engine()
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT
                    d.ticker,
                    d.trading_date,
                    d.range_pct,
                    d.low_bucket,
                    d.high_bucket,
                    COUNT(m.ts) AS bars,
                    AVG(m.volume) AS avg_volume,
                    STDDEV(m.close) AS intraday_volatility
                FROM daily_summary d
                JOIN minute_bars m
                  ON d.ticker = m.ticker
                 AND DATE(m.ts) = d.trading_date
                GROUP BY d.ticker, d.trading_date, d.range_pct,
                         d.low_bucket, d.high_bucket
                ORDER BY d.trading_date
            """),
            conn
        )
    return df


def build_features():
    df = load_daily_data()

    # Lag features (previous day behavior)
    df["range_lag1"] = df.groupby("ticker")["range_pct"].shift(1)
    df["volatility_lag1"] = df.groupby("ticker")["intraday_volatility"].shift(1)
    df["volume_lag1"] = df.groupby("ticker")["avg_volume"].shift(1)

    # Rolling stats
    df["range_mean_3"] = df.groupby("ticker")["range_pct"].rolling(3).mean().reset_index(0, drop=True)
    df["range_std_3"] = df.groupby("ticker")["range_pct"].rolling(3).std().reset_index(0, drop=True)

    df = df.dropna().reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = build_features()
    print(df.head())
