from pathlib import Path
from dotenv import dotenv_values
from datetime import datetime

from alpaca.data.live import StockDataStream

from app.paper.broker import PaperBroker
from app.strategy.live_strategy import SimpleMomentumStrategy


def main():
    # --------------------------------------------------
    # Load Alpaca credentials directly from .env
    # --------------------------------------------------
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    ENV_PATH = PROJECT_ROOT / ".env"

    config = dotenv_values(ENV_PATH)

    api_key = config.get("ALPACA_API_KEY")
    secret_key = config.get("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise RuntimeError("Alpaca credentials not found in .env file")

    # --------------------------------------------------
    # Trading setup
    # --------------------------------------------------
    symbol = "AAPL"
    starting_cash = 10_000

    broker = PaperBroker(starting_cash=starting_cash)
    strategy = SimpleMomentumStrategy(window=5)

    # --------------------------------------------------
    # Live equity & drawdown tracking (Stage 4.3)
    # --------------------------------------------------
    equity_curve = []
    peak_equity = starting_cash

    # --------------------------------------------------
    # Alpaca live data stream
    # --------------------------------------------------
    stream = StockDataStream(api_key, secret_key)

    async def on_trade(trade):
        nonlocal peak_equity

        price = trade.price
        timestamp = trade.timestamp or datetime.utcnow()

        # Strategy signal
        signal = strategy.update(price)

        # Execute paper trades
        if signal == "BUY" and broker.position == 0:
            broker.buy(price)

        elif signal == "SELL" and broker.position > 0:
            broker.sell(price)

        # Portfolio state
        equity = broker.equity(price)
        peak_equity = max(peak_equity, equity)
        drawdown = (equity - peak_equity) / peak_equity

        # Store equity snapshot
        equity_curve.append({
            "timestamp": timestamp,
            "price": price,
            "equity": equity,
            "drawdown": drawdown,
        })

        # Console output (live monitoring)
        print(
            f"{symbol} | "
            f"Price: {price:8.2f} | "
            f"Signal: {signal:4s} | "
            f"Equity: {equity:9.2f} | "
            f"DD: {drawdown:6.2%}"
        )

    # --------------------------------------------------
    # Subscribe & run
    # --------------------------------------------------
    stream.subscribe_trades(on_trade, symbol)

    print(f"📡 Paper trading live for {symbol} (Ctrl+C to stop)")
    stream.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Paper trading stopped.")
