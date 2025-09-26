"""Graph node implementations for the application layer."""

from __future__ import annotations

from tradingagents.v2.domain import NodeKind, NodeSpec

from .data_fetch import (
    DataFetchNode,
    FundamentalsDataFetchNode,
    MarketDataFetchNode,
    NewsDataFetchNode,
    SentimentDataFetchNode,
    default_data_fetch_nodes,
)
from .analysis import (
    FundamentalsAnalysisNode,
    MarketAnalysisNode,
    NewsAnalysisNode,
    SentimentAnalysisNode,
)
from .debate import (
    BearResearchNode,
    BullResearchNode,
    RiskAssessmentNode,
    TraderDecisionNode,
)

__all__ = [
    "DataFetchNode",
    "FundamentalsDataFetchNode",
    "MarketDataFetchNode",
    "NewsDataFetchNode",
    "SentimentDataFetchNode",
    "default_data_fetch_nodes",
    "FundamentalsAnalysisNode",
    "MarketAnalysisNode",
    "NewsAnalysisNode",
    "SentimentAnalysisNode",
    "BearResearchNode",
    "BullResearchNode",
    "TraderDecisionNode",
    "RiskAssessmentNode",
    "default_node_specs",
]


def default_node_specs() -> list[NodeSpec]:
    """Return the default application node specs used by the planner."""

    return [
        NodeSpec(
            id="analysis.market",
            node_kind=NodeKind.ANALYSIS,
            requires=frozenset({"session.ticker", "session.as_of", "raw.market"}),
            produces=frozenset({"analysis.market_report"}),
            factory=MarketAnalysisNode,
        ),
        NodeSpec(
            id="analysis.news",
            node_kind=NodeKind.ANALYSIS,
            requires=frozenset({"session.ticker", "session.as_of", "raw.news"}),
            produces=frozenset({"analysis.news_report"}),
            factory=NewsAnalysisNode,
        ),
        NodeSpec(
            id="analysis.fundamentals",
            node_kind=NodeKind.ANALYSIS,
            requires=frozenset({"session.ticker", "session.as_of", "raw.fundamentals"}),
            produces=frozenset({"analysis.fundamentals_report"}),
            factory=FundamentalsAnalysisNode,
        ),
        NodeSpec(
            id="analysis.sentiment",
            node_kind=NodeKind.ANALYSIS,
            requires=frozenset({"session.ticker", "session.as_of", "raw.sentiment"}),
            produces=frozenset({"analysis.sentiment_report"}),
            factory=SentimentAnalysisNode,
        ),
        NodeSpec(
            id="debate.bull",
            node_kind=NodeKind.DEBATE,
            requires=frozenset(
                {
                    "session.ticker",
                    "session.as_of",
                    "analysis.market_report",
                    "analysis.news_report",
                    "analysis.fundamentals_report",
                    "analysis.sentiment_report",
                }
            ),
            produces=frozenset({"debate.bull_case"}),
            factory=BullResearchNode,
        ),
        NodeSpec(
            id="debate.bear",
            node_kind=NodeKind.DEBATE,
            requires=frozenset(
                {
                    "session.ticker",
                    "session.as_of",
                    "analysis.market_report",
                    "analysis.news_report",
                    "analysis.fundamentals_report",
                    "analysis.sentiment_report",
                }
            ),
            produces=frozenset({"debate.bear_case"}),
            factory=BearResearchNode,
        ),
        NodeSpec(
            id="decision.trader",
            node_kind=NodeKind.DECISION,
            requires=frozenset(
                {
                    "session.ticker",
                    "session.as_of",
                    "debate.bull_case",
                    "debate.bear_case",
                    "analysis.market_report",
                }
            ),
            produces=frozenset({"decision.trader_plan"}),
            factory=TraderDecisionNode,
        ),
        NodeSpec(
            id="risk.assessment",
            node_kind=NodeKind.RISK,
            requires=frozenset(
                {
                    "session.ticker",
                    "session.as_of",
                    "decision.trader_plan",
                    "analysis.news_report",
                    "analysis.fundamentals_report",
                }
            ),
            produces=frozenset({"risk.assessment"}),
            factory=RiskAssessmentNode,
        ),
    ]
