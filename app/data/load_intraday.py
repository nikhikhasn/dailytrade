import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")


def load_intraday_history(
    symbol: str,
    multiplier: int = 5,
    timespan: str = "minute",
    limit: int = 5000,
):
    """
    Fetch historical intraday bars from Polygon.
    Returns a DataFrame with columns:
    [date, time, low, high, close]
    """

    if not POLYGON_API_KEY:
        raise RuntimeError("POLYGON_API_KEY not set")

    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/"
        f"{multiplier}/{timespan}/2024-01-01/2026-12-31"
    )

    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": limit,
        "apiKey": POLYGON_API_KEY,
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    if "results" not in data:
        raise RuntimeError("No intraday data returned from Polygon")

    rows = []
    for bar in data["results"]:
        ts = datetime.fromtimestamp(bar["t"] / 1000)
        rows.append(
            {
                "date": ts.date(),
                "time": ts.time(),
                "low": bar["l"],
                "high": bar["h"],
                "close": bar["c"],
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError("Intraday dataframe is empty")

    return df
