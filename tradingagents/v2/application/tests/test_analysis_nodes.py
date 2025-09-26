from collections import deque

import pytest

from tradingagents.v2.application.nodes import (
    FundamentalsAnalysisNode,
    MarketAnalysisNode,
    NewsAnalysisNode,
    SentimentAnalysisNode,
)
from tradingagents.v2.domain import SessionDataContext


class StubGateway:
    def __init__(self, responses):
        self._responses = {
            key: deque([value] if not isinstance(value, (list, tuple)) else value)
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


@pytest.fixture
def context_with_raw():
    context = SessionDataContext(
        {
            "session.ticker": "AAPL",
            "session.as_of": "2024-07-04",
            "raw.market": {"prices": [1, 2]},
            "raw.news": ["headline"],
            "raw.fundamentals": {"pe": 10},
            "raw.sentiment": {"score": 0.4},
        }
    )
    return context


def test_market_analysis_node_returns_report(context_with_raw):
    gateway = StubGateway({("openai", "analyze_market"): [{"report": "market"}]})
    node = MarketAnalysisNode()

    result = node.execute(context_with_raw, gateway)

    assert result == {"analysis.market_report": "market"}
    assert gateway.calls[0][2]["market_data"] == {"prices": [1, 2]}


def test_news_analysis_node_uses_news_items(context_with_raw):
    gateway = StubGateway({("openai", "analyze_news"): [{"report": "news"}]})
    node = NewsAnalysisNode()

    result = node.execute(context_with_raw, gateway)

    assert result["analysis.news_report"] == "news"
    assert gateway.calls[0][2]["news_items"] == ["headline"]


def test_fundamentals_analysis_node(context_with_raw):
    gateway = StubGateway({("openai", "analyze_fundamentals"): [{"report": "fund"}]})
    node = FundamentalsAnalysisNode()

    result = node.execute(context_with_raw, gateway)

    assert result == {"analysis.fundamentals_report": "fund"}


def test_sentiment_analysis_node(context_with_raw):
    gateway = StubGateway({("openai", "analyze_sentiment"): [{"report": "sent"}]})
    node = SentimentAnalysisNode()

    result = node.execute(context_with_raw, gateway)

    assert result == {"analysis.sentiment_report": "sent"}
