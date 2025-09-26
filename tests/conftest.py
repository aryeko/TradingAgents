import json
import pathlib
import sys
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tradingagents.api import get_graph
from tradingagents.default_config import DEFAULT_CONFIG


class DummyLLM:
    """Minimal chat model stand-in used across the system."""

    def __init__(self, *args, **kwargs):
        self._tools = []

    def bind_tools(self, tools):
        bound = DummyLLM()
        bound._tools = list(tools)
        return bound

    def invoke(self, prompt, **kwargs):
        prompt_str = json.dumps(prompt, default=str)
        if "extract the investment decision" in prompt_str.lower():
            content = "BUY"
        elif "final transaction proposal" in prompt_str.upper():
            content = "Mock FINAL TRANSACTION PROPOSAL: **BUY**"
        else:
            content = "Mock analysis with actionable insights"
        return AIMessage(content=content, tool_calls=[])


class DummyMemory:
    def __init__(self, name, config):
        self.name = name

    def get_memories(self, current_situation, n_matches=1):
        return [
            {
                "matched_situation": f"{self.name} prior situation",
                "recommendation": f"{self.name} memory recommendation",
                "similarity_score": 0.9,
            }
        ]

    def add_situations(self, situations_and_advice):
        return None


class DummyGateway:
    def __init__(self):
        self.calls = []

    def invoke(self, provider, operation, payload):
        self.calls.append((provider, operation, payload))
        return {"provider": provider, "operation": operation, "payload": payload}


class FakeGraph:
    """Replacement LangGraph that returns a canned but realistic state."""

    def invoke(self, initial_state, **kwargs):
        final_state = dict(initial_state)
        final_state.update(
            {
                "sender": "Risk Judge",
                "market_report": "Market momentum remains strong.",
                "sentiment_report": "Social sentiment leans positive.",
                "news_report": "Macro landscape stable.",
                "fundamentals_report": "Balance sheet healthy.",
                "investment_plan": "Research team proposes scaling into position.",
                "trader_investment_plan": "Trader will ladder entries. FINAL TRANSACTION PROPOSAL: **BUY**",
                "final_trade_decision": "Risk judge confirms FINAL TRANSACTION PROPOSAL: **BUY**",
                "investment_debate_state": {
                    "history": "Bull vs Bear exchanged arguments.",
                    "bull_history": "Bull: Growth prospects solid.",
                    "bear_history": "Bear: Valuation stretched.",
                    "current_response": "Bull rebuttal delivered.",
                    "judge_decision": "Manager advocates proceeding.",
                    "count": 2,
                },
                "risk_debate_state": {
                    "history": "Risk analysts aligned on exposure.",
                    "risky_history": "Risky: take advantage of momentum.",
                    "safe_history": "Safe: size position conservatively.",
                    "neutral_history": "Neutral: monitor macro catalysts.",
                    "latest_speaker": "Risk Judge",
                    "current_risky_response": "Momentum justified.",
                    "current_safe_response": "Size limits noted.",
                    "current_neutral_response": "Monitoring plan prepared.",
                    "judge_decision": "Judge endorses controlled BUY.",
                    "count": 3,
                },
                "messages": list(initial_state.get("messages", []))
                + [
                    AIMessage(
                        content="Portfolio Manager: proceeding with BUY.",
                        tool_calls=[],
                    )
                ],
            }
        )
        return final_state

    def stream(self, initial_state, **kwargs):  # pragma: no cover - invoked in debug runs
        final_state = self.invoke(initial_state, **kwargs)
        yield final_state


@pytest.fixture
def mock_runtime(monkeypatch, tmp_path):
    """Mock all external dependencies so the graph can run deterministically."""

    import tradingagents.v1.graph.trading_graph as legacy_graph_module
    import tradingagents.v1.graph.signal_processing as legacy_signal_module
    import tradingagents.v1.graph.setup as legacy_setup_module
    import tradingagents.v2.graph.trading_graph as modern_graph_module
    import tradingagents.v2.graph.signal_processing as modern_signal_module
    import tradingagents.v2.graph.setup as modern_setup_module
    import tradingagents.v2.infrastructure.external as modern_external_module

    for module in (legacy_graph_module, modern_graph_module):
        monkeypatch.setattr(module, "ChatOpenAI", DummyLLM)
        monkeypatch.setattr(module, "ChatAnthropic", DummyLLM)
        monkeypatch.setattr(module, "ChatGoogleGenerativeAI", DummyLLM)
        monkeypatch.setattr(module, "FinancialSituationMemory", DummyMemory)

    monkeypatch.setattr(
        legacy_setup_module.GraphSetup, "setup_graph", lambda self, *_: FakeGraph()
    )
    monkeypatch.setattr(
        modern_setup_module.GraphSetup, "setup_graph", lambda self, *_: FakeGraph()
    )

    def noop_log_state(self, trade_date, final_state):
        self.log_states_dict[str(trade_date)] = {
            "final_trade_decision": final_state["final_trade_decision"],
        }

    monkeypatch.setattr(legacy_graph_module.TradingAgentsGraph, "_log_state", noop_log_state)
    monkeypatch.setattr(modern_graph_module.TradingAgentsGraph, "_log_state", noop_log_state)

    monkeypatch.setattr(
        legacy_signal_module.SignalProcessor,
        "process_signal",
        lambda self, full_signal: "BUY",
    )
    monkeypatch.setattr(
        modern_signal_module.SignalProcessor,
        "process_signal",
        lambda self, full_signal: "BUY",
    )

    monkeypatch.setattr(
        modern_external_module,
        "build_default_gateway",
        lambda **_: DummyGateway(),
    )

    def fake_propagate(self, company_name, trade_date):
        final_state = FakeGraph().invoke({"ticker": company_name, "trade_date": trade_date})
        decision = "BUY"
        return final_state, decision

    monkeypatch.setattr(
        legacy_graph_module.TradingAgentsGraph,
        "propagate",
        fake_propagate,
        raising=False,
    )
    monkeypatch.setattr(
        modern_graph_module.TradingAgentsGraph,
        "propagate",
        fake_propagate,
        raising=False,
    )

    return SimpleNamespace(tmp_path=tmp_path)


@pytest.fixture
def ta_graph(mock_runtime, tmp_path):
    def factory(*, selected_analysts=None, debug=False, version="v1", **overrides):
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(
            {
                "project_dir": str(tmp_path),
                "results_dir": str(tmp_path / "results"),
                "data_dir": str(tmp_path / "data"),
                "data_cache_dir": str(tmp_path / "cache"),
                "runtime_version": version,
                "online_tools": False,
            }
        )
        cfg.update(overrides)

        analysts = selected_analysts or ["market"]
        return get_graph(selected_analysts=analysts, debug=debug, config=cfg)

    return factory
