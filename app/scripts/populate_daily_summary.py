import pandas as pd

from app.db.engine import create_engine
from app.ml.build_features import build_features


def populate_daily_summary():
    engine = create_engine()

    print("📊 Building daily features...")
    df = build_features()

    if df.empty:
        raise RuntimeError("No features generated")

    cols = [
        "ticker",
        "trading_date",
        "range_pct",
        "avg_volume",
        "intraday_volatility",
        "range_lag1",
        "volatility_lag1",
        "volume_lag1",
        "range_mean_3",
        "range_std_3",
    ]

    df = df[cols]

    print(f"⬆️ Inserting {len(df)} rows into daily_summary")

    with engine.begin() as conn:
        df.to_sql(
            "daily_summary",
            conn,
            if_exists="append",
            index=False,
            method="multi",
        )

    print("✅ daily_summary populated successfully")


if __name__ == "__main__":
    populate_daily_summary()
