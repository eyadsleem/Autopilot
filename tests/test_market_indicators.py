from datetime import datetime, timedelta

from app.schemas import Candle
from app.services.market_data import MarketDataService


def test_compute_indicators_returns_values_for_long_enough_series():
    base = datetime(2024, 1, 1)
    candles = [
        Candle(
            timestamp=base + timedelta(days=i),
            open=100 + i,
            high=101 + i,
            low=99 + i,
            close=100 + i,
            volume=1000 + i,
        )
        for i in range(40)
    ]

    indicators = MarketDataService._compute_indicators(candles)

    assert indicators.rsi_14 is not None
    assert indicators.macd is not None
    assert indicators.macd_signal is not None
    assert indicators.atr_14 is not None
