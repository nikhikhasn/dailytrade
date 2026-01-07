from datetime import datetime
import pandas as pd

from app.backtest.models import Trade


# ==================================================
# DB-BASED DAILY SIMULATION (KEEP FOR LATER STAGES)
# ==================================================

def simulate_day(
    db,
    ticker: str,
    trading_date,
    capital: float
):
    """
    Used later for live / DB-backed simulations.
    NOT used in Stage 2–3.2.
    """
    from app.db.models import MinuteBar
    from app.report.daily_recommendation import generate_recommendation

    rec = generate_recommendation(ticker, capital)
    if not rec:
        return None

    required_keys = [
        "buy_time",
        "sell_time",
        "buy_price",
        "sell_price",
        "shares",
    ]

    if not all(k in rec for k in required_keys):
        return None

    buy_time = datetime.combine(trading_date, rec["buy_time"])
    sell_time = datetime.combine(trading_date, rec["sell_time"])
    shares = rec["shares"]

    if shares <= 0:
        return None

    buy_bar = db.query(MinuteBar).filter(
        MinuteBar.ticker == ticker,
        MinuteBar.ts == buy_time
    ).first()

    sell_bar = db.query(MinuteBar).filter(
        MinuteBar.ticker == ticker,
        MinuteBar.ts == sell_time
    ).first()

    if not buy_bar or not sell_bar:
        return None

    return Trade(
        ticker=ticker,
        entry_time=buy_time,
        entry_price=float(buy_bar.close),
        exit_time=sell_time,
        exit_price=float(sell_bar.close),
        shares=shares,
    )


# ==================================================
# DATAFRAME-BASED BACKTEST (STAGE 2 + 3.2)
# ==================================================

def run_backtest(price_df: pd.DataFrame):
    """
    Pure DataFrame backtest.
    Used by run_backtest.py.
    """

    trades = []
    capital = 10_000.0

    # --- SIMPLE PLACEHOLDER STRATEGY ---
    for i in range(1, len(price_df)):
        prev = price_df.iloc[i - 1]
        curr = price_df.iloc[i]

        if curr["close"] > prev["close"]:
            entry_price = prev["close"]
            exit_price = curr["close"]
            shares = 1

            pnl = (exit_price - entry_price) * shares
            capital += pnl

            trades.append(
                {
                    "entry_time": prev["timestamp"],
                    "exit_time": curr["timestamp"],
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "shares": shares,
                    "pnl": pnl,
                }
            )

    trades_df = pd.DataFrame(trades)

    # =========================
    # Stage 3.2 – Minimal Stats
    # =========================

    if not trades_df.empty:
        wins = trades_df[trades_df["pnl"] > 0]
        losses = trades_df[trades_df["pnl"] <= 0]

        win_rate = len(wins) / len(trades_df)
        loss_rate = 1 - win_rate

        avg_win = wins["pnl"].mean() if not wins.empty else 0.0
        avg_loss = abs(losses["pnl"].mean()) if not losses.empty else 0.0

        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
    else:
        win_rate = expectancy = avg_win = avg_loss = 0.0

    stats = {
        "total_trades": len(trades_df),
        "win_rate": win_rate,
        "total_pnl": trades_df["pnl"].sum() if not trades_df.empty else 0.0,
        "avg_pnl": trades_df["pnl"].mean() if not trades_df.empty else 0.0,
        "expectancy": expectancy,
    }

    return trades_df, stats
