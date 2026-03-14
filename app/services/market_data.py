from __future__ import annotations

from datetime import datetime
from importlib.util import find_spec

from app.schemas import Candle, MarketSnapshot, TechnicalIndicators

if find_spec("yfinance"):
    import yfinance as yf
else:
    yf = None


class MarketDataService:
    """Loads OHLCV candles and computes core technical indicators."""

    def get_snapshot(self, symbol: str, interval: str = "1d", period: str = "3mo") -> MarketSnapshot:
        if yf is None:
            raise ValueError("yfinance dependency is not installed")

        ticker = yf.Ticker(symbol)
        history = ticker.history(interval=interval, period=period)
        if history.empty:
            raise ValueError(f"No market data found for symbol={symbol}")

        candles = [
            Candle(
                timestamp=self._timestamp(index),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=float(row["Volume"]),
            )
            for index, row in history.iterrows()
        ]
        indicators = self._compute_indicators(candles)
        return MarketSnapshot(symbol=symbol.upper(), timeframe=interval, candles=candles, indicators=indicators)

    @staticmethod
    def _compute_indicators(candles: list[Candle]) -> TechnicalIndicators:
        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]

        return TechnicalIndicators(
            rsi_14=_rsi(closes, 14),
            macd=_macd(closes)[0],
            macd_signal=_macd(closes)[1],
            atr_14=_atr(highs, lows, closes, 14),
        )

    @staticmethod
    def _timestamp(index: object) -> datetime:
        if hasattr(index, "to_pydatetime"):
            return index.to_pydatetime()
        if isinstance(index, datetime):
            return index
        raise ValueError("Unexpected timestamp type in market data response")


def _ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    k = 2 / (period + 1)
    ema_values = [values[0]]
    for v in values[1:]:
        ema_values.append((v * k) + (ema_values[-1] * (1 - k)))
    return ema_values


def _rsi(closes: list[float], period: int) -> float | None:
    if len(closes) <= period:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for idx in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[idx]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[idx]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def _macd(closes: list[float]) -> tuple[float | None, float | None]:
    if len(closes) < 26:
        return None, None
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd_line = [a - b for a, b in zip(ema12[-len(ema26):], ema26)]
    signal_line = _ema(macd_line, 9)
    return round(macd_line[-1], 4), round(signal_line[-1], 4)


def _atr(highs: list[float], lows: list[float], closes: list[float], period: int) -> float | None:
    if len(closes) <= period:
        return None

    trs: list[float] = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        trs.append(tr)
    atr = sum(trs[:period]) / period
    for tr in trs[period:]:
        atr = ((atr * (period - 1)) + tr) / period
    return round(atr, 4)
