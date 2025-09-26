from tradingagents.default_config import DEFAULT_CONFIG


def get_graph(selected_analysts=None, debug=False, config=None):
    cfg = (config or DEFAULT_CONFIG).copy()
    version = (cfg.get("runtime_version") or "v1").lower()
    if selected_analysts is None:
        selected_analysts = ["market", "social", "news", "fundamentals"]

    if version == "v1":
        from tradingagents.v1.graph.trading_graph import TradingAgentsGraph
        return TradingAgentsGraph(selected_analysts, debug=debug, config=cfg)
    elif version == "v2":
        from tradingagents.v2.graph.trading_graph import TradingAgentsGraph
        return TradingAgentsGraph(selected_analysts, debug=debug, config=cfg)
    else:
        raise ValueError(f"Unknown runtime_version: {version}")
