from collections import deque

import pytest

from tradingagents.v2.application import (
    DataBootstrapper,
    DependencyPlanner,
    NodeExecutor,
    TradingSession,
)
from tradingagents.v2.application.nodes import default_node_specs
from tradingagents.v2.domain import NodeSpec, NodeKind, SessionDataContext


class GatewayStub:
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


class IncrementingNode:
    def __init__(self, node_id: str, produces: str, *, fail_once: bool = False):
        self.id = node_id
        self.node_kind = NodeKind.ANALYSIS
        self.requires = frozenset()
        self.produces = frozenset({produces})
        self._produces = produces
        self._fail_once = fail_once
        self._called = False

    def execute(self, context: SessionDataContext, gateway: object):
        if self._fail_once and not self._called:
            self._called = True
            raise RuntimeError("transient")
        return {self._produces: context.snapshot().get(self._produces, 0) + 1}


def _analysis_gateway_responses():
    return {
        ("yahoo_finance", "historical_prices"): [{"report": "prices"}],
        ("finnhub", "company_news"): [{"report": "news"}],
        ("simfin", "fundamentals_snapshot"): [{"report": "fund"}],
        ("reddit", "social_sentiment"): [{"report": "sent"}],
        ("openai", "analyze_market"): [{"report": "market"}],
        ("openai", "analyze_news"): [{"report": "news-report"}],
        ("openai", "analyze_fundamentals"): [{"report": "fund-report"}],
        ("openai", "analyze_sentiment"): [{"report": "sent-report"}],
        ("openai", "compose_bull_case"): [{"content": "bull"}],
        ("openai", "compose_bear_case"): [{"content": "bear"}],
        ("openai", "draft_trader_plan"): [{"plan": "plan"}],
        ("openai", "assess_risk"): [{"assessment": "risk"}],
    }


def test_dependency_planner_orders_nodes():
    specs = default_node_specs()
    planner = DependencyPlanner(specs)
    context = SessionDataContext(
        {
            "session.ticker": "AAPL",
            "session.as_of": "2024-07-04",
            "raw.market": {},
            "raw.news": {},
            "raw.fundamentals": {},
            "raw.sentiment": {},
        }
    )

    plan = planner.plan(context)

    assert [spec.id for spec in plan] == [
        "analysis.fundamentals",
        "analysis.market",
        "analysis.news",
        "analysis.sentiment",
        "debate.bear",
        "debate.bull",
        "decision.trader",
        "risk.assessment",
    ]


def test_node_executor_runs_plan():
    context = SessionDataContext(
        {
            "session.ticker": "AAPL",
            "session.as_of": "2024-07-04",
            "raw.market": {},
            "raw.news": {},
            "raw.fundamentals": {},
            "raw.sentiment": {},
        }
    )
    gateway = GatewayStub(_analysis_gateway_responses())
    planner = DependencyPlanner(default_node_specs())
    plan = planner.plan(context)

    executor = NodeExecutor()
    records = executor.execute(plan, context, gateway)

    assert context.require("risk.assessment") == "risk"
    assert [record.node_id for record in records][-1] == "risk.assessment"


def test_node_executor_retries_failures():
    spec = NodeSpec(
        id="test.node",
        node_kind=NodeKind.ANALYSIS,
        requires=frozenset(),
        produces=frozenset({"analysis.value"}),
        factory=lambda: IncrementingNode("test.node", "analysis.value", fail_once=True),
    )
    context = SessionDataContext()
    executor = NodeExecutor(max_retries=1)
    records = executor.execute([spec], context, gateway=object())

    assert context.require("analysis.value") == 1
    assert records[0].attempts == 2


def test_trading_session_runs_pipeline():
    gateway = GatewayStub(_analysis_gateway_responses())
    bootstrapper = DataBootstrapper()
    session = TradingSession(
        bootstrapper=bootstrapper,
        planner=DependencyPlanner(default_node_specs()),
        executor=NodeExecutor(),
        gateway=gateway,
        node_specs=default_node_specs(),
    )

    result = session.run(ticker="AAPL", as_of="2024-07-04")

    artifacts = result.context.snapshot()
    assert artifacts["risk.assessment"] == "risk"
    assert "analysis.market_report" in artifacts
    assert result.plan[-1] == "risk.assessment"
