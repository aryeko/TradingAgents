"""Graph node protocol used by the modern TradingAgents runtime.

The taxonomy of node kinds and their responsibilities is defined in
``docs-v2/new-architecture/final-architecture.md``. Nodes interact with the
shared :class:`~tradingagents.domain.SessionDataContext` to obtain inputs and
publish outputs.
"""
from __future__ import annotations

from enum import Enum
from typing import Mapping, Protocol, runtime_checkable

from tradingagents.v2.domain.context.session_data_context import SessionDataContext

__all__ = ["GraphNode", "NodeKind"]


class NodeKind(str, Enum):
    """Classification for nodes participating in a trading session."""

    DATA_FETCH = "data_fetch"
    ANALYSIS = "analysis"
    AGGREGATION = "aggregation"
    DEBATE = "debate"
    RISK = "risk"
    DECISION = "decision"
    REPORT = "report"


@runtime_checkable
class GraphNode(Protocol):
    """Protocol implemented by every node in the execution graph."""

    id: str
    node_kind: NodeKind
    requires: frozenset[str]
    produces: frozenset[str]

    def execute(
        self,
        context: SessionDataContext,
        gateway: object,
    ) -> Mapping[str, object]:
        """Execute the node's logic and return published artifacts.

        The ``gateway`` parameter will be an instance of
        :class:`ExternalApiGateway` (introduced in Story S3). It is typed as
        ``object`` here to avoid an import cycle before the gateway exists.
        """

        ...
