from collections import deque

from tradingagents.v2.application.nodes import (
    FundamentalsDataFetchNode,
    MarketDataFetchNode,
    NewsDataFetchNode,
    SentimentDataFetchNode,
)
from tradingagents.v2.domain import SessionDataContext


class StubGateway:
    def __init__(self):
        self.calls = []
        self.responses = deque()

    def enqueue(self, response):
        self.responses.append(response)

    def invoke(self, provider, operation, payload):
        self.calls.append((provider, operation, payload))
        if not self.responses:
            raise AssertionError("No queued response for gateway call")
        outcome = self.responses.popleft()
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _context_with_metadata():
    context = SessionDataContext()
    context.publish("session.ticker", "AAPL")
    context.publish("session.as_of", "2024-07-04")
    return context


def test_market_fetch_node_invokes_gateway_with_window():
    gateway = StubGateway()
    gateway.enqueue({"prices": []})
    node = MarketDataFetchNode(lookback_days=10)
    context = _context_with_metadata()

    result = node.execute(context, gateway)

    assert result == {"raw.market": {"prices": []}}
    provider, operation, payload = gateway.calls[0]
    assert provider == "yahoo_finance"
    assert operation == "historical_prices"
    assert payload["window_days"] == 10


def test_news_fetch_node_includes_limit_and_window():
    gateway = StubGateway()
    gateway.enqueue({"articles": []})
    node = NewsDataFetchNode(window_days=5, limit=12)
    context = _context_with_metadata()

    node.execute(context, gateway)

    payload = gateway.calls[0][2]
    assert payload["window_days"] == 5
    assert payload["limit"] == 12


def test_fundamentals_fetch_node_produces_expected_key():
    gateway = StubGateway()
    gateway.enqueue({"balance_sheet": {}})
    node = FundamentalsDataFetchNode()
    context = _context_with_metadata()

    result = node.execute(context, gateway)

    assert "raw.fundamentals" in result


def test_sentiment_fetch_node_uses_reddit_provider():
    gateway = StubGateway()
    gateway.enqueue({"posts": []})
    node = SentimentDataFetchNode(window_days=2)
    context = _context_with_metadata()

    node.execute(context, gateway)

    provider, operation, payload = gateway.calls[0]
    assert provider == "reddit"
    assert operation == "social_sentiment"
    assert payload["window_days"] == 2
