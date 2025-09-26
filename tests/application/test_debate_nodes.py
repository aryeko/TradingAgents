from collections import deque

import pytest

from tradingagents.application.nodes import (
    BearResearchNode,
    BullResearchNode,
    RiskAssessmentNode,
    TraderDecisionNode,
)
from tradingagents.domain import SessionDataContext


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
def context_with_analysis():
    context = SessionDataContext(
        {
            "session.ticker": "AAPL",
            "session.as_of": "2024-07-04",
            "analysis.market_report": "market",
            "analysis.news_report": "news",
            "analysis.fundamentals_report": "fund",
            "analysis.sentiment_report": "sentiment",
            "debate.bull_case": "bull",
            "debate.bear_case": "bear",
            "decision.trader_plan": "plan",
        }
    )
    return context


def test_bull_research_node_builds_case(context_with_analysis):
    gateway = StubGateway({("openai", "compose_bull_case"): [{"content": "bull-case"}]})
    node = BullResearchNode()

    result = node.execute(context_with_analysis, gateway)

    assert result == {"debate.bull_case": "bull-case"}
    payload = gateway.calls[0][2]
    assert payload["market_report"] == "market"
    assert payload["sentiment_report"] == "sentiment"


def test_bear_research_node_builds_case(context_with_analysis):
    gateway = StubGateway({("openai", "compose_bear_case"): [{"content": "bear-case"}]})
    node = BearResearchNode()

    result = node.execute(context_with_analysis, gateway)

    assert result == {"debate.bear_case": "bear-case"}


def test_trader_decision_node_returns_plan(context_with_analysis):
    gateway = StubGateway({("openai", "draft_trader_plan"): [{"plan": "plan-out"}]})
    node = TraderDecisionNode()

    result = node.execute(context_with_analysis, gateway)

    assert result == {"decision.trader_plan": "plan-out"}
    payload = gateway.calls[0][2]
    assert payload["bull_case"] == "bull"
    assert payload["bear_case"] == "bear"


def test_risk_assessment_node(context_with_analysis):
    gateway = StubGateway({("openai", "assess_risk"): [{"assessment": "risk"}]})
    node = RiskAssessmentNode()

    result = node.execute(context_with_analysis, gateway)

    assert result == {"risk.assessment": "risk"}
    payload = gateway.calls[0][2]
    assert payload["trader_plan"] == "plan"
