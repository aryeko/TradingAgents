from collections import deque

import pytest

from tradingagents.application import DataBootstrapper, BootstrapFailure
from tradingagents.application.nodes import default_data_fetch_nodes
from tradingagents.domain import SessionDataContext


class StubGateway:
    def __init__(self, responses):
        self._responses = {
            key: deque(value if isinstance(value, (list, tuple)) else [value])
            for key, value in responses.items()
        }
        self.calls = []

    def invoke(self, provider, operation, payload):
        key = (provider, operation)
        self.calls.append((provider, operation, payload))
        queue = self._responses.get(key)
        if not queue:
            raise AssertionError(f"No response queued for {key}")
        outcome = queue.popleft()
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_bootstrap_publishes_raw_artifacts():
    context = SessionDataContext()
    gateway = StubGateway(
        {
            ("yahoo_finance", "historical_prices"): [{"prices": [1, 2]}],
            ("finnhub", "company_news"): [{"articles": ["headline"]}],
            ("simfin", "fundamentals_snapshot"): [{"balance_sheet": {}}],
            ("reddit", "social_sentiment"): [{"sentiment": 0.5}],
        }
    )
    bootstrapper = DataBootstrapper(default_data_fetch_nodes())

    published = bootstrapper.bootstrap(
        context,
        gateway,
        ticker="AAPL",
        as_of="2024-07-04",
    )

    assert context.require("raw.market") == {"prices": [1, 2]}
    assert context.require("raw.news")["articles"] == ["headline"]
    assert context.require("raw.fundamentals") == {"balance_sheet": {}}
    assert context.require("raw.sentiment") == {"sentiment": 0.5}
    assert set(published) == {
        "raw.market",
        "raw.news",
        "raw.fundamentals",
        "raw.sentiment",
    }


def test_bootstrap_raises_on_gateway_error():
    context = SessionDataContext()
    gateway = StubGateway(
        {
            ("yahoo_finance", "historical_prices"): [RuntimeError("boom")],
        }
    )
    bootstrapper = DataBootstrapper(default_data_fetch_nodes())

    with pytest.raises(BootstrapFailure) as excinfo:
        bootstrapper.bootstrap(
            context,
            gateway,
            ticker="AAPL",
            as_of="2024-07-04",
        )

    assert excinfo.value.node_id == "data.fetch.market"


def test_bootstrap_detects_metadata_conflicts():
    context = SessionDataContext({"session.ticker": "MSFT", "session.as_of": "2024-07-01"})
    gateway = StubGateway({})
    bootstrapper = DataBootstrapper(default_data_fetch_nodes())

    with pytest.raises(BootstrapFailure):
        bootstrapper.bootstrap(
            context,
            gateway,
            ticker="AAPL",
            as_of="2024-07-04",
        )


def test_bootstrap_skips_existing_artifacts():
    context = SessionDataContext({
        "session.ticker": "AAPL",
        "session.as_of": "2024-07-04",
        "raw.market": {"prices": [0]},
    })
    gateway = StubGateway(
        {
            ("yahoo_finance", "historical_prices"): [{"prices": [1, 2]}],
            ("finnhub", "company_news"): [{"articles": []}],
            ("simfin", "fundamentals_snapshot"): [{"balance_sheet": {}}],
            ("reddit", "social_sentiment"): [{"sentiment": 0.1}],
        }
    )
    bootstrapper = DataBootstrapper(default_data_fetch_nodes())

    published = bootstrapper.bootstrap(
        context,
        gateway,
        ticker="AAPL",
        as_of="2024-07-04",
    )

    assert context.require("raw.market") == {"prices": [0]}
    assert "raw.market" not in published
    assert context.require("raw.news") == {"articles": []}
