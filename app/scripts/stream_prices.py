import os
from pathlib import Path
from dotenv import dotenv_values
import joblib

from alpaca.trading.client import TradingClient
from alpaca.data.live import StockDataStream

from app.paper.broker import PaperBroker
from app.strategy.live_strategy import SimpleMomentumStrategy

# --------------------------------------------------
# Paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
MODEL_PATH = PROJECT_ROOT / "app" / "ml" / "model.joblib"


# --------------------------------------------------
# Market status check
# --------------------------------------------------
def check_market_open(api_key: str, secret_key: str) -> bool:
    client = TradingClient(api_key, secret_key, paper=True)
    clock = client.get_clock()

    if not clock.is_open:
        print("🕒 Market is CLOSED")
        print(f"Next open: {clock.next_open}")
        print(f"Current time: {clock.timestamp}")
        return False

    print("🟢 Market is OPEN")
    return True


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    # -------------------------------
    # Load environment
    # -------------------------------
    if not ENV_PATH.exists():
        raise RuntimeError(f".env file not found at {ENV_PATH}")

    config = dotenv_values(ENV_PATH)

    api_key = config.get("ALPACA_API_KEY")
    secret_key = config.get("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise RuntimeError(
            "Alpaca credentials not found. "
            "Check ALPACA_API_KEY and ALPACA_SECRET_KEY in .env"
        )

    # -------------------------------
    # Check market status
    # -------------------------------
    if not check_market_open(api_key, secret_key):
        return  # Exit cleanly if market closed

    # -------------------------------
    # Load ML model
    # -------------------------------
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found at {MODEL_PATH}. "
            "Train the model or disable ML temporarily."
        )

    model = joblib.load(MODEL_PATH)

    # -------------------------------
    # Setup trading components
    # -------------------------------
    symbol = "AAPL"

    broker = PaperBroker(starting_cash=10_000)
    strategy = SimpleMomentumStrategy(model=model)

    stream = StockDataStream(api_key, secret_key)

    # -------------------------------
    # Trade handler
    # -------------------------------
    async def on_trade(trade):
        strategy.on_trade(trade, broker)

    stream.subscribe_trades(on_trade, symbol)

    print(f"📡 Paper trading (ML) live for {symbol} (Ctrl+C to stop)")

    try:
        stream.run()
    except KeyboardInterrupt:
        print("\n🛑 Paper trading stopped.")


# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    main()
