from datetime import datetime
from tradingagents.portfolio import Portfolio, portfolio_performance


def test_basic_portfolio_operations():
    p = Portfolio(cash=1000)
    p.deposit(500, datetime(2024, 1, 1))
    assert p.cash == 1500
    p.buy("AAPL", 5, 10, datetime(2024, 1, 2))
    assert p.cash == 1450
    assert p.positions["AAPL"].quantity == 5
    p.sell("AAPL", 2, 12, datetime(2024, 1, 3))
    assert p.cash == 1450 + 24
    assert p.positions["AAPL"].quantity == 3
    total = p.total_value({"AAPL": 12})
    assert total == p.cash + 3 * 12


def test_portfolio_performance():
    p = Portfolio(cash=0)
    p.deposit(1000, datetime(2024, 1, 1))
    p.buy("AAPL", 10, 100, datetime(2024, 1, 2))
    ret, risk = portfolio_performance(p, {"AAPL": [100, 110]})
    assert abs(ret - 0.1) < 1e-6
    assert risk == 0.0
