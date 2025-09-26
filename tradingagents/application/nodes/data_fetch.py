"""Data fetch nodes that seed the session context with raw artifacts."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from tradingagents.domain import GraphNode, NodeKind, SessionDataContext

__all__ = [
    "DataFetchNode",
    "MarketDataFetchNode",
    "NewsDataFetchNode",
    "FundamentalsDataFetchNode",
    "SentimentDataFetchNode",
    "default_data_fetch_nodes",
]


class DataFetchNode(GraphNode):
    """Base implementation for nodes that retrieve raw datasets."""

    base_requirements = frozenset({"session.ticker", "session.as_of"})

    def __init__(
        self,
        node_id: str,
        provider: str,
        operation: str,
        produces_key: str,
        *,
        extra_requires: Iterable[str] | None = None,
    ) -> None:
        self.id = node_id
        self.provider = provider
        self.operation = operation
        self.node_kind = NodeKind.DATA_FETCH
        self._produces_key = produces_key
        requirements = set(self.base_requirements)
        if extra_requires:
            requirements.update(extra_requires)
        self.requires = frozenset(requirements)
        self.produces = frozenset({produces_key})

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        """Construct the payload passed to the gateway."""

        return {
            "ticker": context.require("session.ticker"),
            "as_of": context.require("session.as_of"),
        }

    def execute(self, context: SessionDataContext, gateway: object) -> Mapping[str, Any]:
        payload = self.build_payload(context)
        response = gateway.invoke(self.provider, self.operation, payload)
        return {self._produces_key: response}


class MarketDataFetchNode(DataFetchNode):
    """Fetch historical market data for the session ticker."""

    def __init__(self, lookback_days: int = 30) -> None:
        self.lookback_days = lookback_days
        super().__init__(
            node_id="data.fetch.market",
            provider="yahoo_finance",
            operation="historical_prices",
            produces_key="raw.market",
        )

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        payload = dict(super().build_payload(context))
        payload["window_days"] = self.lookback_days
        return payload


class NewsDataFetchNode(DataFetchNode):
    """Fetch recent company news from market data providers."""

    def __init__(self, window_days: int = 7, limit: int = 20) -> None:
        self.window_days = window_days
        self.limit = limit
        super().__init__(
            node_id="data.fetch.news",
            provider="finnhub",
            operation="company_news",
            produces_key="raw.news",
        )

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        payload = dict(super().build_payload(context))
        payload.update({"window_days": self.window_days, "limit": self.limit})
        return payload


class FundamentalsDataFetchNode(DataFetchNode):
    """Fetch fundamentals snapshot from financial statement providers."""

    def __init__(self) -> None:
        super().__init__(
            node_id="data.fetch.fundamentals",
            provider="simfin",
            operation="fundamentals_snapshot",
            produces_key="raw.fundamentals",
        )


class SentimentDataFetchNode(DataFetchNode):
    """Fetch social sentiment signals for the current ticker."""

    def __init__(self, window_days: int = 3) -> None:
        self.window_days = window_days
        super().__init__(
            node_id="data.fetch.sentiment",
            provider="reddit",
            operation="social_sentiment",
            produces_key="raw.sentiment",
        )

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        payload = dict(super().build_payload(context))
        payload["window_days"] = self.window_days
        return payload


def default_data_fetch_nodes() -> list[DataFetchNode]:
    """Return the default set of fetch nodes used by the bootstrapper."""

    return [
        MarketDataFetchNode(),
        NewsDataFetchNode(),
        FundamentalsDataFetchNode(),
        SentimentDataFetchNode(),
    ]
