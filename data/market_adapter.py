"""data/market_adapter.py - ATOM-STEP-6: Market Data Adapter"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class OHLCV:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketAdapter:
    def __init__(self, source: str = "mock"):
        self.source = source
        self._cache = {}

    def fetch_ohlcv(self, symbol: str, interval: str = "1h", limit: int = 100) -> list[OHLCV]:
        data = []
        now = datetime.utcnow()
        price = 100.0
        for i in range(limit):
            ts = now - timedelta(hours=limit - i - 1) if interval == "1h" else now - timedelta(days=limit - i - 1)
            change = random.gauss(0, 0.02)
            o, c = price, price * (1 + change)
            h, l = (
                max(o, c) * (1 + abs(change) * 0.5),
                min(o, c) * (1 - abs(change) * 0.5),
            )
            data.append(
                OHLCV(
                    timestamp=ts,
                    open=round(o, 4),
                    high=round(h, 4),
                    low=round(l, 4),
                    close=round(c, 4),
                    volume=random.uniform(1000, 10000),
                )
            )
            price = c
        return data

    def get_latest_price(self, symbol: str) -> float:
        data = self.fetch_ohlcv(symbol, limit=1)
        return data[0].close if data else 0.0

    def compute_features(self, ohlcv_data: list[OHLCV]) -> dict:
        if not ohlcv_data:
            return {}
        closes = [d.close for d in ohlcv_data]
        returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
        vol = [d.volume for d in ohlcv_data]
        mean_r = sum(returns) / len(returns) if returns else 0.0
        return {
            "returns_mean": mean_r,
            "returns_std": (sum((r - mean_r) ** 2 for r in returns) / len(returns)) ** 0.5 if len(returns) > 1 else 0.0,
            "volume_mean": sum(vol) / len(vol) if vol else 0.0,
            "latest_close": closes[-1],
            "latest_volume": vol[-1] if vol else 0.0,
        }


if __name__ == "__main__":
    adapter = MarketAdapter()
    data = adapter.fetch_ohlcv("BTCUSDT", limit=20)
    features = adapter.compute_features(data)
    print(f"Market Adapter: fetched {len(data)} bars")
    print(f"Features: {features}")
