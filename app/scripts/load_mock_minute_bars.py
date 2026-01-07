import pandas as pd
from datetime import date, timedelta

from app.data.mock_data import generate_mock_day


def load_mock_minute_bars(
    ticker: str = "AAPL",
    start_date: date = date(2024, 1, 2),
    num_days: int = 5,
):
    """
    Load mock intraday minute bars for multiple trading days.
    Uses generate_mock_day from app.data.mock_data.
    """

    all_rows = []

    current_date = start_date
    days_generated = 0

    while days_generated < num_days:
        # Skip weekends
        if current_date.weekday() < 5:
            day_rows = generate_mock_day(ticker, current_date)
            all_rows.extend(day_rows)
            days_generated += 1

        current_date += timedelta(days=1)

    df = pd.DataFrame(all_rows)

    # Align column names with backtest engine
    df = df.rename(columns={"ts": "timestamp"})

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    return df
