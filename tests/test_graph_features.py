import types
import pytest
from typer.testing import CliRunner

import cli.main as cli_main


def test_propagate_portfolio_multi(monkeypatch):
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    tg = TradingAgentsGraph.__new__(TradingAgentsGraph)
    tg.rebalance = lambda *a, **k: None

    def dummy_propagate(self, ticker, trade_date):
        return {"state": ticker}, "BUY"

    monkeypatch.setattr(TradingAgentsGraph, "propagate", dummy_propagate)

    result = TradingAgentsGraph.propagate_portfolio(tg, ["AAA", "BBB"], "2024-01-01")
    assert set(result.keys()) == {"AAA", "BBB"}
    assert result["AAA"]["signal"] == "BUY"


def test_cli_track_command(monkeypatch):
    class DummyGraph:
        def __init__(self):
            self.portfolio = types.SimpleNamespace(deposit=lambda *a, **k: None)
            self.optimizer = types.SimpleNamespace(optimize=lambda *a, **k: ({}, (0, 0)))

        def propagate_portfolio(self, tickers, date):
            return {t: {"signal": "BUY"} for t in tickers}

    monkeypatch.setattr(cli_main, "TradingAgentsGraph", DummyGraph)
    runner = CliRunner()
    result = runner.invoke(cli_main.app, [
        "track",
        "AAA,BBB",
        "--cash",
        "1000",
        "--trade-date",
        "2024-01-01",
    ])
    assert result.exit_code == 0
    assert "AAA" in result.output


def test_graph_setup_empty(monkeypatch):
    from tradingagents.graph.setup import GraphSetup

    dummy_llm = object()
    gs = GraphSetup(
        dummy_llm,
        dummy_llm,
        None,
        {},
        None,
        None,
        None,
        None,
        None,
        object(),
    )

    with pytest.raises(ValueError):
        gs.setup_graph([])
