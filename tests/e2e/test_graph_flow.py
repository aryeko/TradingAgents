import pytest

from tradingagents.default_config import DEFAULT_CONFIG


@pytest.mark.e2e
@pytest.mark.parametrize("version", ["v1", "v2"])
def test_trading_graph_propagate_returns_buy_signal(ta_graph, version):
    """Test that the trading graph returns a BUY signal for both v1 and v2 architectures."""
    graph = ta_graph(version=version)
    final_state, decision = graph.propagate("AAPL", "2024-06-30")

    assert decision == "BUY"
    assert final_state["final_trade_decision"].endswith("**BUY**")
    assert final_state["investment_plan"]
    assert final_state["investment_debate_state"]["judge_decision"]
    assert final_state["risk_debate_state"]["judge_decision"]


@pytest.mark.e2e
@pytest.mark.parametrize("version", ["v1", "v2"])
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
    ta_graph, version, llm_provider, deep_model, quick_model, backend
):
    """Test that both v1 and v2 architectures support multiple LLM providers."""
    graph = ta_graph(
        version=version,
        llm_provider=llm_provider,
        deep_think_llm=deep_model,
        quick_think_llm=quick_model,
        backend_url=backend,
    )
    final_state, decision = graph.propagate("MSFT", "2024-07-01")

    assert decision == "BUY"
    assert "FINAL TRANSACTION PROPOSAL" in final_state["final_trade_decision"]


@pytest.mark.e2e
@pytest.mark.parametrize("version", ["v1", "v2"])
@pytest.mark.parametrize(
    "analysts",
    [
        ["market"],
        ["market", "news"],
        ["market", "social", "news", "fundamentals"],
    ],
)
@pytest.mark.parametrize("online_tools", [False, True])
def test_trading_graph_handles_analyst_permutations(ta_graph, version, analysts, online_tools):
    """Test that both v1 and v2 architectures handle different analyst combinations."""
    graph = ta_graph(version=version, selected_analysts=analysts, online_tools=online_tools)
    final_state, decision = graph.propagate("GOOGL", "2024-07-02")

    assert decision == "BUY"
    assert final_state["investment_plan"]
    assert final_state["risk_debate_state"]["judge_decision"].startswith("Judge")


@pytest.mark.e2e
@pytest.mark.parametrize("version", ["v1", "v2"])
def test_trading_graph_debug_mode_uses_stream(ta_graph, version):
    """Test that both v1 and v2 architectures support debug mode with streaming."""
    graph = ta_graph(version=version, debug=True)
    final_state, decision = graph.propagate("AMZN", "2024-07-03")

    assert decision == "BUY"
    assert final_state["messages"][-1].content.startswith("Portfolio Manager")


@pytest.mark.e2e
@pytest.mark.parametrize("version", ["v1", "v2"])
def test_version_specific_functionality(ta_graph, version):
    """Test that validates version-specific functionality works correctly."""
    graph = ta_graph(version=version)
    final_state, decision = graph.propagate("TSLA", "2024-07-04")
    
    # Both versions should return BUY
    assert decision == "BUY"
    
    # Validate that the graph has the expected structure for each version
    if version == "v1":
        # v1 specific validations
        assert "final_trade_decision" in final_state
        assert "investment_debate_state" in final_state
        assert "risk_debate_state" in final_state
    elif version == "v2":
        # v2 specific validations
        assert "session" in final_state or "final_trade_decision" in final_state
    else:
        pytest.fail(f"Unknown version: {version}")
