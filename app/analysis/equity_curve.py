import pandas as pd


def build_equity_curve_timestamped(
    price_df: pd.DataFrame,
    trades_df: pd.DataFrame,
    starting_capital: float = 10000.0
):
    """
    Builds equity & drawdown at every timestamp using trade exit events.
    """

    # --- 1. Copy & sort ---
    prices = price_df.copy()
    prices = prices.sort_values("timestamp")

    trades = trades_df.copy()
    trades = trades.sort_values("exit_time")

    # --- 2. Create empty PnL column ---
    prices["pnl"] = 0.0

    # --- 3. Inject trade PnL at exit timestamps ---
    for _, trade in trades.iterrows():
        exit_time = trade["exit_time"]
        pnl = trade["pnl"]

        # Find the closest timestamp <= exit_time
        idx = prices[prices["timestamp"] <= exit_time].index.max()

        if pd.notna(idx):
            prices.loc[idx, "pnl"] += pnl

    # --- 4. Equity calculation ---
    prices["equity"] = starting_capital + prices["pnl"].cumsum()

    # --- 5. Drawdown calculation ---
    prices["peak_equity"] = prices["equity"].cummax()
    prices["drawdown"] = prices["equity"] - prices["peak_equity"]

    return prices
