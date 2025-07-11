from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Iterable, Tuple


@dataclass
class Transaction:
    date: datetime
    symbol: str
    quantity: float
    price: float
    type: str  # BUY, SELL, DEPOSIT, WITHDRAW


@dataclass
class Position:
    symbol: str
    quantity: float
    average_price: float


@dataclass
class Portfolio:
    cash: float = 0.0
    positions: Dict[str, Position] = field(default_factory=dict)
    history: List[Transaction] = field(default_factory=list)

    def deposit(self, amount: float, date: datetime) -> None:
        self.cash += amount
        self.history.append(Transaction(date, "", amount, 0.0, "DEPOSIT"))

    def withdraw(self, amount: float, date: datetime) -> None:
        if amount > self.cash:
            raise ValueError("Insufficient cash")
        self.cash -= amount
        self.history.append(Transaction(date, "", -amount, 0.0, "WITHDRAW"))

    def buy(self, symbol: str, quantity: float, price: float, date: datetime) -> None:
        total = quantity * price
        if total > self.cash:
            raise ValueError("Insufficient cash to buy")
        self.cash -= total
        pos = self.positions.get(symbol)
        if pos:
            new_qty = pos.quantity + quantity
            pos.average_price = (pos.average_price * pos.quantity + price * quantity) / new_qty
            pos.quantity = new_qty
        else:
            self.positions[symbol] = Position(symbol, quantity, price)
        self.history.append(Transaction(date, symbol, quantity, price, "BUY"))

    def sell(self, symbol: str, quantity: float, price: float, date: datetime) -> None:
        pos = self.positions.get(symbol)
        if not pos or pos.quantity < quantity:
            raise ValueError("Insufficient shares to sell")
        pos.quantity -= quantity
        self.cash += quantity * price
        if pos.quantity == 0:
            del self.positions[symbol]
        self.history.append(Transaction(date, symbol, -quantity, price, "SELL"))

    def total_value(self, prices: Dict[str, float]) -> float:
        value = self.cash
        for sym, pos in self.positions.items():
            value += pos.quantity * prices.get(sym, pos.average_price)
        return value


def portfolio_performance(portfolio: Portfolio, price_histories: Dict[str, Iterable[float]]) -> Tuple[float, float]:
    """Return estimated (return, risk) for the portfolio.

    price_histories maps symbols to a sequence of prices where the first and last
    elements represent the evaluation window.
    """
    weights: Dict[str, float] = {}
    total = portfolio.cash
    for sym, pos in portfolio.positions.items():
        last_price = price_histories.get(sym, [pos.average_price])[-1]
        w = pos.quantity * last_price
        weights[sym] = w
        total += w

    if total == 0:
        return 0.0, 0.0

    returns: Dict[str, float] = {}
    for sym, hist in price_histories.items():
        if len(hist) >= 2:
            returns[sym] = (hist[-1] - hist[0]) / hist[0]

    weighted_return = 0.0
    for sym, w in weights.items():
        if sym in returns:
            weighted_return += (w / total) * returns[sym]

    mean = weighted_return
    variance = 0.0
    for sym, w in weights.items():
        if sym in returns:
            variance += (w / total) * (returns[sym] - mean) ** 2

    risk = variance ** 0.5
    return weighted_return, risk


class PortfolioOptimizer:
    """Simple optimizer suggesting position adjustments based on performance."""

    def __init__(self, target_return: float = 0.05, max_risk: float = 0.1):
        self.target_return = target_return
        self.max_risk = max_risk

    def optimize(
        self,
        portfolio: Portfolio,
        price_histories: Dict[str, Iterable[float]],
    ) -> Tuple[Dict[str, float], Tuple[float, float]]:
        """Return suggested quantity changes and (return, risk)."""
        ret, risk = portfolio_performance(portfolio, price_histories)
        adjustments: Dict[str, float] = {}

        if risk > self.max_risk:
            for sym, pos in portfolio.positions.items():
                adjustments[sym] = -0.5 * pos.quantity
        elif ret < self.target_return and portfolio.positions:
            invest = portfolio.cash / len(portfolio.positions)
            for sym, pos in portfolio.positions.items():
                price = price_histories.get(sym, [pos.average_price])[-1]
                qty = invest / price if price > 0 else 0
                adjustments[sym] = qty
        else:
            for sym in portfolio.positions:
                adjustments[sym] = 0.0

        return adjustments, (ret, risk)
