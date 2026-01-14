from datetime import time
import numpy as np


class DailyGate:
    """
    Layer A: Rule-based intraday structure
    Layer B: Optional ML confidence (validation only)

    Responsibilities:
    - Identify when daily LOWs usually occur (BUY windows)
    - Identify when daily HIGHs usually occur (SELL windows)
    - Enforce valid trade order (SELL after BUY)
    - Estimate expected profit (avg high - avg low)
    """

    def __init__(self, intraday_df, model=None):
        """
        intraday_df columns required:
        - date (date)
        - time (datetime.time)
        - low (float)
        - high (float)
        - close (float)

        model: optional ML classifier for confidence only
        """
        self.intraday_df = intraday_df
        self.model = model
        self.plan = self._build_plan()

    # --------------------------------------------------
    # Core plan builder
    # --------------------------------------------------
    def _build_plan(self):
        df = self.intraday_df.copy()

        # --- Identify daily LOW and HIGH timestamps ---
        daily_lows = df.loc[df.groupby("date")["low"].idxmin()]
        daily_highs = df.loc[df.groupby("date")["high"].idxmax()]

        buy_windows = self._bucket_times(daily_lows["time"])
        sell_windows = self._bucket_times(daily_highs["time"])

        # --- Expected prices & profit ---
        expected_low = float(daily_lows["low"].mean())
        expected_high = float(daily_highs["high"].mean())
        expected_profit = expected_high - expected_low

        # --------------------------------------------------
        # Enforce trading logic: SELL must be AFTER BUY
        # --------------------------------------------------
        best_buy = buy_windows[0]

        valid_sells = [
            w for w in sell_windows
            if (w.hour, w.minute) > (best_buy.hour, best_buy.minute)
        ]

        # Fallback (rare): if no sell is after buy, keep original
        final_sell_windows = valid_sells if valid_sells else sell_windows

        plan = {
            "buy_windows": buy_windows,
            "sell_windows": final_sell_windows,
            "expected_low": expected_low,
            "expected_high": expected_high,
            "expected_profit": expected_profit,
        }

        # --------------------------------------------------
        # Layer B: ML confidence (optional)
        # --------------------------------------------------
        if self.model is not None:
            try:
                confidence = float(
                    self.model.predict_proba(self._build_features())[0][1]
                )
                status = "VALID" if confidence >= 0.65 else "CAUTION"
            except Exception:
                confidence = None
                status = "UNKNOWN"
        else:
            confidence = None
            status = "UNKNOWN"

        plan["confidence"] = confidence
        plan["status"] = status

        return plan

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def _bucket_times(self, times):
        """
        Convert timestamps into 15-minute buckets.
        Returns the top 3 most frequent buckets.
        """
        counts = {}

        for t in times:
            minute_bucket = (t.minute // 15) * 15
            bucket = time(t.hour, minute_bucket)
            counts[bucket] = counts.get(bucket, 0) + 1

        # Sort by frequency (descending)
        sorted_buckets = sorted(counts, key=counts.get, reverse=True)
        return sorted_buckets[:3]

    def _build_features(self):
        """
        Placeholder for ML confidence features.
        You already have this pipeline elsewhere.
        """
        raise NotImplementedError(
            "ML confidence feature builder not wired yet"
        )

    # --------------------------------------------------
    # Layer C helper (live confirmation)
    # --------------------------------------------------
    def get_active_window(self, now):
        """
        Returns:
        - 'BUY' if current time is inside a BUY window
        - 'SELL' if current time is inside a SELL window
        - None otherwise
        """
        current = time(now.hour, (now.minute // 15) * 15)

        if current in self.plan["buy_windows"]:
            return "BUY"

        if current in self.plan["sell_windows"]:
            return "SELL"

        return None
