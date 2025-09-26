"""Debate and decision nodes built on top of analysis outputs."""
from __future__ import annotations

from typing import Any, Mapping

from tradingagents.domain import NodeKind, SessionDataContext

from .data_fetch import DataFetchNode

__all__ = [
    "BullResearchNode",
    "BearResearchNode",
    "TraderDecisionNode",
    "RiskAssessmentNode",
]


class _BaseDebateNode(DataFetchNode):
    provider = "openai"

    def __init__(
        self,
        node_id: str,
        operation: str,
        produces_key: str,
        node_kind: NodeKind,
        requires: set[str],
    ) -> None:
        super().__init__(
            node_id=node_id,
            provider=self.provider,
            operation=operation,
            produces_key=produces_key,
            extra_requires=requires,
        )
        self.node_kind = node_kind

    def build_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        return {
            "ticker": context.require("session.ticker"),
            "as_of": context.require("session.as_of"),
        }

    def extract_output(self, response: Mapping[str, Any]) -> Any:
        return response.get("content", response)

    def execute(self, context: SessionDataContext, gateway: object) -> Mapping[str, Any]:
        payload = dict(self.build_payload(context))
        payload.update(self.additional_payload(context))
        response = gateway.invoke(self.provider, self.operation, payload)
        return {self._produces_key: self.extract_output(response)}

    def additional_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        return {}


class BullResearchNode(_BaseDebateNode):
    def __init__(self) -> None:
        super().__init__(
            node_id="debate.bull",
            operation="compose_bull_case",
            produces_key="debate.bull_case",
            node_kind=NodeKind.DEBATE,
            requires={
                "analysis.market_report",
                "analysis.news_report",
                "analysis.fundamentals_report",
                "analysis.sentiment_report",
            },
        )

    def additional_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        return {
            "market_report": context.require("analysis.market_report"),
            "news_report": context.require("analysis.news_report"),
            "fundamentals_report": context.require("analysis.fundamentals_report"),
            "sentiment_report": context.require("analysis.sentiment_report"),
        }


class BearResearchNode(_BaseDebateNode):
    def __init__(self) -> None:
        super().__init__(
            node_id="debate.bear",
            operation="compose_bear_case",
            produces_key="debate.bear_case",
            node_kind=NodeKind.DEBATE,
            requires={
                "analysis.market_report",
                "analysis.news_report",
                "analysis.fundamentals_report",
                "analysis.sentiment_report",
            },
        )

    def additional_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        return {
            "market_report": context.require("analysis.market_report"),
            "news_report": context.require("analysis.news_report"),
            "fundamentals_report": context.require("analysis.fundamentals_report"),
            "sentiment_report": context.require("analysis.sentiment_report"),
        }


class TraderDecisionNode(_BaseDebateNode):
    def __init__(self) -> None:
        super().__init__(
            node_id="decision.trader",
            operation="draft_trader_plan",
            produces_key="decision.trader_plan",
            node_kind=NodeKind.DECISION,
            requires={
                "debate.bull_case",
                "debate.bear_case",
                "analysis.market_report",
            },
        )

    def additional_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        return {
            "bull_case": context.require("debate.bull_case"),
            "bear_case": context.require("debate.bear_case"),
            "market_report": context.require("analysis.market_report"),
        }

    def extract_output(self, response: Mapping[str, Any]) -> Any:
        return response.get("plan", response)


class RiskAssessmentNode(_BaseDebateNode):
    def __init__(self) -> None:
        super().__init__(
            node_id="risk.assessment",
            operation="assess_risk",
            produces_key="risk.assessment",
            node_kind=NodeKind.RISK,
            requires={
                "decision.trader_plan",
                "analysis.news_report",
                "analysis.fundamentals_report",
            },
        )

    def additional_payload(self, context: SessionDataContext) -> Mapping[str, Any]:
        return {
            "trader_plan": context.require("decision.trader_plan"),
            "news_report": context.require("analysis.news_report"),
            "fundamentals_report": context.require("analysis.fundamentals_report"),
        }

    def extract_output(self, response: Mapping[str, Any]) -> Any:
        return response.get("assessment", response)
