from pathlib import Path
from dotenv import dotenv_values
import joblib
from datetime import datetime

from alpaca.trading.client import TradingClient
from alpaca.data.live import StockDataStream

from app.paper.broker import PaperBroker
from app.strategy.live_strategy import SimpleMomentumStrategy
from app.ml.daily_gate import DailyGate
from app.data.load_intraday import load_intraday_history  # your Polygon loader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
MODEL_PATH = PROJECT_ROOT / "app/ml/model.joblib"


def check_market_open(api_key, secret_key):
    client = TradingClient(api_key, secret_key, paper=True)
    clock = client.get_clock()
    if not clock.is_open:
        print("🕒 Market is CLOSED")
        return False
    print("🟢 Market is OPEN")
    return True


def main():
    config = dotenv_values(ENV_PATH)
    api_key = config["ALPACA_API_KEY"]
    secret_key = config["ALPACA_SECRET_KEY"]

    if not check_market_open(api_key, secret_key):
        return

    symbol = "IONQ"

    # -----------------------------
    # Load intraday history (Polygon)
    # -----------------------------
    intraday_df = load_intraday_history(symbol)

    # -----------------------------
    # Optional ML confidence
    # -----------------------------
    model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    if model:
        print("🧠 ML confidence enabled")
    else:
        print("⚠️ ML confidence disabled")

    daily_gate = DailyGate(intraday_df, model=model)

    # -----------------------------
    # Print DAILY PLAN (once)
    # -----------------------------
    plan = daily_gate.plan

    # Helper to format window nicely
    def fmt_window(t):
        start = t.strftime("%H:%M")
        end_min = (t.minute + 15) % 60
        end_hr = t.hour + (1 if t.minute + 15 >= 60 else 0)
        end = f"{end_hr:02d}:{end_min:02d}"
        return f"{start} – {end}"

    best_buy = plan["buy_windows"][0]
    best_sell = plan["sell_windows"][0]

    print("🧠 Daily Plan (Layer A)")

    print(f"   Best BUY window : {fmt_window(best_buy)}")
    print(f"   Best SELL window: {fmt_window(best_sell)}")
    print(f"   Best profit     : ${plan['expected_profit']:.2f} per share")

    # Optional: show alternates (useful but secondary)
    if len(plan["buy_windows"]) > 1:
        print("   Other BUY windows:")
        for w in plan["buy_windows"][1:]:
            print(f"      • {fmt_window(w)}")

    if len(plan["sell_windows"]) > 1:
        print("   Other SELL windows:")
        for w in plan["sell_windows"][1:]:
            print(f"      • {fmt_window(w)}")

    print(f"   Expected profit : ${plan['expected_profit']:.2f} per share")

    print("🧠 Validation (Layer B)")
    print(f"   Status: {plan['status']}")


    # -----------------------------
    # Live stream (Layer C)
    # -----------------------------
    broker = PaperBroker(starting_cash=10_000)
    strategy = SimpleMomentumStrategy(daily_gate)

    stream = StockDataStream(api_key, secret_key)

    async def on_trade(trade):
        strategy.on_trade(trade, broker)

    stream.subscribe_trades(on_trade, symbol)
    print(f"📡 Paper trading live for {symbol}")
    stream.run()


if __name__ == "__main__":
    main()
