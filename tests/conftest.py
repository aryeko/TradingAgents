import json
from types import SimpleNamespace

import pytest


@pytest.fixture
def mock_runtime(monkeypatch, tmp_path):
    """Mock all external dependencies so the graph can run deterministically."""
    from langchain_core.messages import AIMessage

    # Lazy import to ensure patches land before usage
    import tradingagents.graph.trading_graph as graph_module
    import tradingagents.graph.signal_processing as signal_module

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

    # Patch heavy dependencies with deterministic doubles
    monkeypatch.setattr(graph_module, "ChatOpenAI", DummyLLM)
    monkeypatch.setattr(graph_module, "ChatAnthropic", DummyLLM)
    monkeypatch.setattr(graph_module, "ChatGoogleGenerativeAI", DummyLLM)
    monkeypatch.setattr(graph_module, "FinancialSituationMemory", DummyMemory)
    monkeypatch.setattr(graph_module.GraphSetup, "setup_graph", lambda self, *_: FakeGraph())

    def noop_log_state(self, trade_date, final_state):
        self.log_states_dict[str(trade_date)] = {
            "final_trade_decision": final_state["final_trade_decision"],
        }

    monkeypatch.setattr(graph_module.TradingAgentsGraph, "_log_state", noop_log_state)
    monkeypatch.setattr(
        signal_module.SignalProcessor,
        "process_signal",
        lambda self, full_signal: "BUY",
    )

    # Ensure temp directories exist without touching user space
    return SimpleNamespace(tmp_path=tmp_path)
