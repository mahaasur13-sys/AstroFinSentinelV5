"""trading/broker/binance.py — ATOM-STEP-9: Binance broker adapter"""
from __future__ import annotations

import time
from typing import Optional

import yaml

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False

from .base import (
    AccountBalance,
    BaseBroker,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
)


class BinanceBroker(BaseBroker):
    """Binance spot/futures broker via CCXT.
    
    Paper mode by default. To enable live trading, set paper=False
    and provide API credentials via:
    - Environment variables: BINANCE_API_KEY, BINANCE_SECRET
    - Or config file: config/binance_credentials.yaml
    """

    def __init__(self, paper: bool = True, config_path: Optional[str] = None):
        super().__init__(paper=paper)
        self.api_key: Optional[str] = None
        self.secret: Optional[str] = None
        self.exchange: Optional[object] = None
        self._load_credentials(config_path)

    def _load_credentials(self, config_path: Optional[str] = None):
        """Load API credentials from environment or config file."""
        import os
        self.api_key = os.environ.get("BINANCE_API_KEY")
        self.secret = os.environ.get("BINANCE_SECRET")
        
        if not self.api_key and config_path:
            try:
                with open(config_path) as f:
                    creds = yaml.safe_load(f)
                    self.api_key = creds.get("api_key")
                    self.secret = creds.get("secret")
            except Exception:
                pass

    def connect(self) -> bool:
        """Connect to Binance via CCXT."""
        if not HAS_CCXT:
            print("Warning: ccxt not installed. Running in simulation mode.")
            self.connected = True
            return True

        try:
            config = {
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
            }
            if not self.paper and self.api_key and self.secret:
                config["apiKey"] = self.api_key
                config["secret"] = self.secret
            else:
                config["test"] = True  # Testnet/sandbox mode

            self.exchange = ccxt.binance(config)
            self.exchange.fetch_balance()
            self.connected = True
            print(f"BinanceBroker connected (paper={self.paper})")
            return True
        except Exception as e:
            print(f"Binance connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Close connection."""
        self.exchange = None
        self.connected = False
        print("BinanceBroker disconnected")

    def get_account_balance(self) -> AccountBalance:
        """Get account balance."""
        if not self.connected:
            return AccountBalance(total_equity=0, available_cash=0, positions_value=0, total_pnl=0)

        if not HAS_CCXT or not self.exchange:
            # Simulation
            return AccountBalance(
                total_equity=10000.0,
                available_cash=10000.0,
                positions_value=0.0,
                total_pnl=0.0,
                currency="USDT",
            )

        try:
            balance = self.exchange.fetch_balance()
            total_usd = float(balance.get("total", {}).get("USDT", 0))
            free_usd = float(balance.get("free", {}).get("USDT", 0))
            return AccountBalance(
                total_equity=total_usd,
                available_cash=free_usd,
                positions_value=total_usd - free_usd,
                total_pnl=0.0,
                currency="USDT",
            )
        except Exception:
            return AccountBalance(total_equity=10000, available_cash=10000, positions_value=0, total_pnl=0)

    def get_positions(self) -> list[Position]:
        """Get open positions."""
        if not self.connected:
            return []

        if not HAS_CCXT or not self.exchange:
            return []

        try:
            balance = self.exchange.fetch_balance()
            positions = []
            for symbol, data in balance.get("total", {}).items():
                if symbol == "USDT" or float(data) <= 0:
                    continue
                try:
                    ticker = self.exchange.fetch_ticker(symbol + "/USDT")
                    price = ticker.get("last", 0)
                    qty = float(data)
                    positions.append(Position(
                        symbol=symbol,
                        quantity=qty,
                        avg_entry_price=0,
                        current_price=price,
                        unrealized_pnl=0,
                        unrealized_pnl_pct=0,
                    ))
                except Exception:
                    continue
            return positions
        except Exception:
            return []

    def place_order(self, symbol: str, side: OrderSide, order_type: OrderType,
                    quantity: float, price: Optional[float] = None) -> Order:
        """Place an order."""
        order_id = f"sim_{int(time.time()*1000)}"
        
        if not self.connected:
            return Order(
                order_id=order_id, symbol=symbol, side=side,
                order_type=order_type, quantity=quantity, price=price,
                status=OrderStatus.REJECTED, notes="Not connected",
            )

        if not HAS_CCXT or not self.exchange or self.paper:
            # Paper/live simulation
            exec_price = price or self.get_market_price(symbol)
            commission = quantity * exec_price * 0.001  # 0.1% maker fee
            return Order(
                order_id=order_id,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status=OrderStatus.FILLED,
                filled_qty=quantity,
                avg_fill_price=exec_price,
                commission=commission,
                notes="Paper simulation" if self.paper else "Live (testnet)",
            )

        # Real CCXT order
        try:
            side_str = "buy" if side == OrderSide.BUY else "sell"
            type_str = order_type.value
            
            if order_type == OrderType.LIMIT or order_type == OrderType.STOP_LIMIT:
                order = self.exchange.create_order(symbol, type_str, side_str, quantity, price)
            elif order_type == OrderType.STOP:
                order = self.exchange.create_order(symbol, "stop", side_str, quantity, price)
            else:
                order = self.exchange.create_order(symbol, "market", side_str, quantity)

            return Order(
                order_id=str(order.get("id", order_id)),
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status=OrderStatus.FILLED,
                filled_qty=float(order.get("filled", quantity)),
                avg_fill_price=float(order.get("average", price or 0)),
                commission=float(order.get("fee", {}).get("cost", 0)),
                created_at=order.get("timestamp", time.time() * 1000) / 1000,
            )
        except Exception as e:
            return Order(
                order_id=order_id, symbol=symbol, side=side,
                order_type=order_type, quantity=quantity, price=price,
                status=OrderStatus.REJECTED, notes=str(e),
            )

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if not self.connected or not HAS_CCXT or not self.exchange or self.paper:
            return False
        try:
            self.exchange.cancel_order(order_id)
            return True
        except Exception:
            return False

    def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get order status."""
        if not self.connected:
            return None
        if "sim_" in order_id:
            return None  # Simulation orders are instant
        if not HAS_CCXT or not self.exchange:
            return None
        try:
            order = self.exchange.fetch_order(order_id)
            return Order(
                order_id=str(order["id"]),
                symbol=order["symbol"],
                side=OrderSide.BUY if order["side"] == "buy" else OrderSide.SELL,
                order_type=OrderType.MARKET,
                quantity=float(order["amount"]),
                price=float(order.get("price", 0)),
                status=OrderStatus.FILLED if order["status"] == "closed" else OrderStatus.PENDING,
                filled_qty=float(order.get("filled", 0)),
            )
        except Exception:
            return None

    def get_market_price(self, symbol: str) -> float:
        """Get current market price."""
        if not self.connected:
            return 0.0
        if not HAS_CCXT or not self.exchange:
            return 100.0  # Simulation price

        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker.get("last", 0))
        except Exception:
            return 0.0

    def __repr__(self) -> str:
        status = "connected" if self.connected else "disconnected"
        mode = "PAPER" if self.paper else "LIVE"
        return f"BinanceBroker({mode}, {status})"
