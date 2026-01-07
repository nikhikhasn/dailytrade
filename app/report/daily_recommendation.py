from datetime import time

def generate_recommendation(ticker: str, capital: float):
    """
    Returns a dict with:
    - machine-readable fields (for backtesting / execution)
    - display block (for humans / UI)
    """

    # ---- MOCKED VALUES (replace with ML outputs as before) ----
    buy_time = time(15, 15)
    sell_time = time(15, 45)

    buy_price = 18.08
    sell_price = 21.92
    shares = int(capital // buy_price)

    if shares <= 0:
        return None

    expected_range_pct = ((sell_price - buy_price) / buy_price) * 100
    estimated_profit = (sell_price - buy_price) * shares

    # ---- FINAL REPORT ----
    report = {
        # 🔹 MACHINE-READABLE (used by backtest / execution)
        "ticker": ticker,
        "capital": capital,
        "buy_time": buy_time,              # datetime.time
        "sell_time": sell_time,            # datetime.time
        "buy_price": round(buy_price, 2),  # float
        "sell_price": round(sell_price, 2),
        "shares": shares,
        "expected_intraday_range_pct": round(expected_range_pct, 2),
        "estimated_profit_usd": round(estimated_profit, 2),

        # 🔹 HUMAN-READABLE (display only)
        "display": {
            "Ticker": ticker,
            "Capital allocated ($)": capital,
            "Initial buy value ($)": round(buy_price * shares, 2),
            "Number of shares": shares,
            "Buy window": f"{buy_time} (${buy_price:.2f})",
            "Sell window": f"{sell_time} (${sell_price:.2f})",
            "Expected intraday range (%)": round(expected_range_pct, 2),
            "Estimated net profit ($)": round(estimated_profit, 2),
        }
    }

    return report
