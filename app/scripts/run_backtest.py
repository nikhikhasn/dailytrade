"""
Stage 2: Backtesting
Stage 3.1: Timestamp-based equity & drawdown
Stage 3.2: Minimal risk metrics
"""

import matplotlib.pyplot as plt

from app.scripts.load_mock_minute_bars import load_mock_minute_bars
from app.backtest.engine import run_backtest
from app.analysis.equity_curve import build_equity_curve_timestamped


def main():
    # --------------------------------------------------
    # 1. Load mock historical price data
    # --------------------------------------------------
    price_df = load_mock_minute_bars()

    # --------------------------------------------------
    # 2. Run backtest (Stage 2)
    # --------------------------------------------------
    trades_df, stats = run_backtest(price_df)

    print("\n📊 Backtest Summary")
    for k, v in stats.items():
        print(f"{k}: {v}")

    # --------------------------------------------------
    # 3. Build equity curve (Stage 3.1)
    # --------------------------------------------------
    equity_df = build_equity_curve_timestamped(
        price_df=price_df,
        trades_df=trades_df,
        starting_capital=10_000,
    )

    # --------------------------------------------------
    # 4. Risk metrics (Stage 3.2 – minimal)
    # --------------------------------------------------
    max_drawdown = equity_df["drawdown"].min()
    peak_equity = equity_df["equity"].max()
    max_drawdown_pct = (max_drawdown / peak_equity) * 100

    print("\n📉 Risk Metrics")
    print(f"Max Drawdown: {max_drawdown:.2f}")
    print(f"Max Drawdown %: {max_drawdown_pct:.2f}%")
    print(f"Expectancy per trade: {stats['expectancy']:.2f}")

    # --------------------------------------------------
    # 5. Debug plot (temporary)
    # --------------------------------------------------
    plt.figure(figsize=(12, 5))
    plt.plot(equity_df["timestamp"], equity_df["equity"])
    plt.title("Equity Curve (Timestamp-Based)")
    plt.xlabel("Time")
    plt.ylabel("Equity ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(30)   # show figure for 30 seconds
    plt.close()


if __name__ == "__main__":
    main()
