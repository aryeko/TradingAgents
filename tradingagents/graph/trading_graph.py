# Default export remains v1 for backward compatibility:
from tradingagents.v1.graph.trading_graph import TradingAgentsGraph  # noqa: F401

# Optional explicit alias for v2:
try:
    from tradingagents.v2.graph.trading_graph import TradingAgentsGraph as TradingAgentsGraphV2  # noqa: F401
except Exception:  # pragma: no cover - fallback if v2 isn't available
    pass
