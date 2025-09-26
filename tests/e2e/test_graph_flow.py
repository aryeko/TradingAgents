import pytest

from tradingagents.default_config import DEFAULT_CONFIG
import pytest


@pytest.mark.e2e
def test_trading_graph_propagate_returns_buy_signal(ta_graph):
    graph = ta_graph()
    final_state, decision = graph.propagate("AAPL", "2024-06-30")

    assert decision == "BUY"
    assert final_state["final_trade_decision"].endswith("**BUY**")
    assert final_state["investment_plan"]
    assert final_state["investment_debate_state"]["judge_decision"]
    assert final_state["risk_debate_state"]["judge_decision"]


@pytest.mark.e2e
@pytest.mark.parametrize(
    "llm_provider, deep_model, quick_model, backend",
    [
        ("openai", "o4-mini", "gpt-4o-mini", "https://api.openai.com/v1"),
        ("anthropic", "claude-3-5-sonnet", "claude-3-5-haiku", "https://api.anthropic.com"),
        ("google", "gemini-2.0", "gemini-2.0-flash", "https://generativelanguage.googleapis.com/v1"),
        ("ollama", "llama3", "llama3", "http://localhost:11434/v1"),
        ("openrouter", "gpt-4o-mini", "gpt-4o-mini", "https://openrouter.ai/api/v1"),
    ],
)
def test_trading_graph_supports_multiple_llm_providers(
    ta_graph, llm_provider, deep_model, quick_model, backend
):
    graph = ta_graph(
        llm_provider=llm_provider,
        deep_think_llm=deep_model,
        quick_think_llm=quick_model,
        backend_url=backend,
    )
    final_state, decision = graph.propagate("MSFT", "2024-07-01")

    assert decision == "BUY"
    assert "FINAL TRANSACTION PROPOSAL" in final_state["final_trade_decision"]


@pytest.mark.e2e
@pytest.mark.parametrize(
    "analysts",
    [
        ["market"],
        ["market", "news"],
        ["market", "social", "news", "fundamentals"],
    ],
)
@pytest.mark.parametrize("online_tools", [False, True])
def test_trading_graph_handles_analyst_permutations(ta_graph, analysts, online_tools):
    graph = ta_graph(selected_analysts=analysts, online_tools=online_tools)
    final_state, decision = graph.propagate("GOOGL", "2024-07-02")

    assert decision == "BUY"
    assert final_state["investment_plan"]
    assert final_state["risk_debate_state"]["judge_decision"].startswith("Judge")


@pytest.mark.e2e
def test_trading_graph_debug_mode_uses_stream(ta_graph):
    graph = ta_graph(debug=True)
    final_state, decision = graph.propagate("AMZN", "2024-07-03")

    assert decision == "BUY"
    assert final_state["messages"][-1].content.startswith("Portfolio Manager")
