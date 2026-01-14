from pathlib import Path
from datetime import datetime
import requests
from dotenv import dotenv_values

from app.db.session import SessionLocal
from app.db.models_daily import DailySummary


# --------------------------------------------------
# Config
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
config = dotenv_values(ENV_PATH)

POLYGON_API_KEY = config.get("POLYGON_API_KEY")
if not POLYGON_API_KEY:
    raise RuntimeError("POLYGON_API_KEY missing from .env")

MIN_DAYS = 10


def populate_daily_summary_for_ticker(ticker: str):
    session = SessionLocal()

    existing = (
        session.query(DailySummary)
        .filter(DailySummary.ticker == ticker)
        .count()
    )

    if existing >= MIN_DAYS:
        session.close()
        return

    print(f"📥 Fetching Polygon daily history for {ticker}...")

    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/"
        f"2020-01-01/{datetime.utcnow().date()}?"
        f"adjusted=true&sort=asc&limit=50000&apiKey={POLYGON_API_KEY}"
    )

    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json().get("results", [])

    if not data:
        print(f"⚠️ Polygon returned no daily data for {ticker}")
        session.close()
        return

    inserted = 0

    for bar in data:
        trading_date = datetime.utcfromtimestamp(bar["t"] / 1000).date()

        exists = (
            session.query(DailySummary)
            .filter(
                DailySummary.ticker == ticker,
                DailySummary.trading_date == trading_date,
            )
            .first()
        )
        if exists:
            continue

        open_p = bar["o"]
        high = bar["h"]
        low = bar["l"]
        close = bar["c"]

        range_pct = ((high - low) / open_p) * 100

        session.add(
            DailySummary(
                ticker=ticker,
                trading_date=trading_date,
                open=open_p,
                high=high,
                low=low,
                close=close,
                range_pct=range_pct,
                low_bucket=int(range_pct // 1),
                high_bucket=int(range_pct // 1),
            )
        )
        inserted += 1

    session.commit()
    session.close()

    print(f"✅ Inserted {inserted} daily rows for {ticker}")
