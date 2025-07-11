from datetime import datetime
from tradingagents.portfolio import (
    Portfolio,
    portfolio_performance,
    PortfolioOptimizer,
)


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


def test_portfolio_optimizer():
    p = Portfolio(cash=1000)
    p.buy("AAPL", 10, 10, datetime(2024, 1, 1))
    opt = PortfolioOptimizer(target_return=0.2, max_risk=0.05)
    adj, (ret, risk) = opt.optimize(p, {"AAPL": [10, 8]})
    assert adj["AAPL"] < 0


def test_update_portfolio_signal():
    p = Portfolio(cash=100)

    def update(signal):
        from datetime import date

        if signal.upper().startswith("BUY"):
            p.buy("AAPL", 1, 10, date.today())
        elif signal.upper().startswith("SELL"):
            try:
                p.sell("AAPL", 1, 10, date.today())
            except Exception:
                pass

    update("BUY")
    assert p.positions["AAPL"].quantity == 1
    update("SELL")
    assert "AAPL" not in p.positions
