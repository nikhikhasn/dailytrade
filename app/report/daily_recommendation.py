import joblib
import pandas as pd
from datetime import timedelta

from app.ml.build_features import build_features

# ============================
# Time / Market Configuration
# ============================

BUCKET_MINUTES = 15
MARKET_OPEN = pd.Timestamp("09:30")

MIN_BUY_BUCKET = 1      # Only buy after 9:40 AM
MAX_BUY_BUCKET = 23     # Never buy after 3:30 PM
MIN_HOLD_BUCKETS = 1    # Minimum hold ≈ 10 minutes
LAST_SELL_BUCKET = 25  # Last sell window (3:45–4:00 PM)


def bucket_to_time(bucket: int):
    return (MARKET_OPEN + timedelta(minutes=bucket * BUCKET_MINUTES)).time()


def generate_recommendation(ticker: str, capital: float):
    """
    Generate a daily trading recommendation for a single ticker.
    """

    # ----------------------------
    # Load latest ML-ready features
    # ----------------------------
    df = build_features()
    latest = df[df["ticker"] == ticker].iloc[-1:]

    if latest.empty:
        raise ValueError(f"No data available for ticker {ticker}")

    X = latest[
        [
            "range_lag1",
            "volatility_lag1",
            "volume_lag1",
            "range_mean_3",
            "range_std_3",
        ]
    ]

    # ----------------------------
    # Load trained models
    # ----------------------------
    buy_model = joblib.load("app/ml/models/buy_time_model.joblib")
    sell_model = joblib.load("app/ml/models/sell_time_model.joblib")

    buy_bucket = int(buy_model.predict(X)[0])
    sell_bucket = int(sell_model.predict(X)[0])

    # ============================
    # Trading Rules (Hard Constraints)
    # ============================

    # Rule 4 — Only buy after 9:40 AM
    if buy_bucket < MIN_BUY_BUCKET:
        buy_bucket = MIN_BUY_BUCKET

    # Rule 3 — Never buy after 3:30 PM
    if buy_bucket > MAX_BUY_BUCKET:
        buy_bucket = MAX_BUY_BUCKET

    # Rule 1 + Rule 2 — Sell after buy with minimum hold
    min_sell_bucket = buy_bucket + MIN_HOLD_BUCKETS
    if sell_bucket < min_sell_bucket:
        sell_bucket = min_sell_bucket

    # Cap sell to market close
    if sell_bucket > LAST_SELL_BUCKET:
        sell_bucket = LAST_SELL_BUCKET

    # ----------------------------
    # Convert buckets → clock times
    # ----------------------------
    buy_time = bucket_to_time(buy_bucket)
    sell_time = bucket_to_time(sell_bucket)

    # ============================
    # Price & Profit Estimation
    # ============================

    expected_range_pct = float(latest["range_pct"].values[0])

    # Stage 1 assumption: approximate current price
    # (later replaced with real minute-bar prices)
    estimated_mid_price = 20.0

    # Approximate low/high capture
    buy_price_estimate = round(
        estimated_mid_price * (1 - expected_range_pct * 0.5), 2
    )
    sell_price_estimate = round(
        estimated_mid_price * (1 + expected_range_pct * 0.5), 2
    )

    # Position sizing
    shares = int(capital // buy_price_estimate)
    initial_buy_value = round(shares * buy_price_estimate, 2)

    # Profit estimation
    profit_per_share = sell_price_estimate - buy_price_estimate
    estimated_profit = round(shares * profit_per_share, 2)

    # ============================
    # Final Report (User-Facing)
    # ============================

    report = {
        "Ticker": ticker,
        "Capital allocated ($)": round(capital, 2),
        "Initial buy value ($)": initial_buy_value,
        "Number of shares": shares,
        "Buy window": f"{buy_time} (${buy_price_estimate})",
        "Sell window": f"{sell_time} (${sell_price_estimate})",
        "Expected intraday range (%)": round(expected_range_pct * 100, 2),
        "Estimated net profit ($)": estimated_profit,
    }

    return report


if __name__ == "__main__":
    recommendation = generate_recommendation("PLTR", 50)

    print("\n📈 Daily Trading Recommendation\n")
    for key, value in recommendation.items():
        print(f"{key}: {value}")
