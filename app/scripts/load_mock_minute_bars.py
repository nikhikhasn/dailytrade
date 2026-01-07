from datetime import date, timedelta

from app.db.engine import init_engine
from app.db.session import SessionLocal
from app.db.models import MinuteBar
from app.data.mock_data import generate_mock_day


def main():
    # 🔹 IMPORTANT: bind SessionLocal to the engine
    init_engine()

    tickers = ["F", "SOFI", "PLTR"]
    start_date = date.today() - timedelta(days=5)

    db = SessionLocal()
    try:
        for d in range(5):
            trading_date = start_date + timedelta(days=d)
            for ticker in tickers:
                rows = generate_mock_day(ticker, trading_date)

                for r in rows:
                    db.merge(MinuteBar(**r))

            print(f"Inserted mock data for {trading_date}")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
