"""Analysis nodes that transform raw data into structured reports."""
from __future__ import annotations

from typing import Any, Mapping

from tradingagents.domain import NodeKind, SessionDataContext

from .data_fetch import DataFetchNode

__all__ = [
    "MarketAnalysisNode",
    "NewsAnalysisNode",
    "FundamentalsAnalysisNode",
    "SentimentAnalysisNode",
]


class _BaseAnalysisNode(DataFetchNode):
    provider = "openai"

    def __init__(
        self,
        node_id: str,
        operation: str,
        produces_key: str,
        *,
        extra_requires: set[str] | None = None,
    ) -> None:
        super().__init__(
            node_id=node_id,
            provider=self.provider,
            operation=operation,
            produces_key=produces_key,
            extra_requires=extra_requires,
        )
        self.node_kind = NodeKind.ANALYSIS

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        payload = super().build_payload(context)
        payload["context"] = "analysis"
        return payload

    def transform_response(self, response: Mapping[str, Any]) -> Any:
        return response.get("report", response)

    def execute(self, context: SessionDataContext, gateway: object) -> Mapping[str, Any]:
        payload = self.build_payload(context)
        response = gateway.invoke(self.provider, self.operation, payload)
        return {self._produces_key: self.transform_response(response)}


class MarketAnalysisNode(_BaseAnalysisNode):
    def __init__(self) -> None:
        super().__init__(
            node_id="analysis.market",
            operation="analyze_market",
            produces_key="analysis.market_report",
            extra_requires={"raw.market"},
        )

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        payload = dict(super().build_payload(context))
        payload["market_data"] = context.require("raw.market")
        return payload


class NewsAnalysisNode(_BaseAnalysisNode):
    def __init__(self) -> None:
        super().__init__(
            node_id="analysis.news",
            operation="analyze_news",
            produces_key="analysis.news_report",
            extra_requires={"raw.news"},
        )

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        payload = dict(super().build_payload(context))
        payload["news_items"] = context.require("raw.news")
        return payload


class FundamentalsAnalysisNode(_BaseAnalysisNode):
    def __init__(self) -> None:
        super().__init__(
            node_id="analysis.fundamentals",
            operation="analyze_fundamentals",
            produces_key="analysis.fundamentals_report",
            extra_requires={"raw.fundamentals"},
        )

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        payload = dict(super().build_payload(context))
        payload["fundamentals"] = context.require("raw.fundamentals")
        return payload


class SentimentAnalysisNode(_BaseAnalysisNode):
    def __init__(self) -> None:
        super().__init__(
            node_id="analysis.sentiment",
            operation="analyze_sentiment",
            produces_key="analysis.sentiment_report",
            extra_requires={"raw.sentiment"},
        )

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        payload = dict(super().build_payload(context))
        payload["sentiment"] = context.require("raw.sentiment")
        return payload
