from typing import List
from app.backtest.models import Trade


def summarize(trades: List[Trade]):
    """
    Summarize backtest performance metrics.

    Each metric answers a specific question about strategy quality:
    - profitability
    - consistency
    - risk
    """

    # If no trades occurred, return empty summary
    if not trades:
        return {}

    # -----------------------------
    # PROFIT & LOSS METRICS
    # -----------------------------

    # Total profit/loss across ALL trades
    # Positive → strategy made money
    # Negative → strategy lost money
    total_pnl = sum(t.pnl for t in trades)

    # Split trades into winners and losers
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]

    # -----------------------------
    # PERFORMANCE SUMMARY
    # -----------------------------

    return {
        # Total number of executed trades
        # Measures strategy activity level
        "total_trades": len(trades),

        # Fraction of profitable trades
        # Example: 0.60 = 60% of trades were winners
        # NOTE: High win-rate does NOT guarantee profitability
        "win_rate": round(len(wins) / len(trades), 3),

        # Net profit/loss over entire backtest period
        # This is the most important metric
        "total_pnl": round(total_pnl, 2),

        # Average profit or loss per trade
        # Useful to compare strategies with different trade counts
        "avg_pnl": round(total_pnl / len(trades), 2),

        # Best single trade outcome
        # Shows upside potential of the strategy
        "best_trade": round(max(t.pnl for t in trades), 2),

        # Worst single trade outcome
        # Shows downside risk of the strategy
        "worst_trade": round(min(t.pnl for t in trades), 2),
    }
