"""Declarative metadata describing graph nodes for planning and execution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping

from tradingagents.v2.domain.context.session_data_context import validate_artifact_key
from tradingagents.v2.domain.nodes.graph_node import GraphNode, NodeKind

__all__ = ["NodeSpec"]


@dataclass(frozen=True, slots=True)
class NodeSpec:
    """Metadata and factory used by the planner to construct a node instance."""

    id: str
    node_kind: NodeKind
    requires: frozenset[str] = field(default_factory=frozenset)
    produces: frozenset[str] = field(default_factory=frozenset)
    factory: Callable[..., GraphNode] | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "requires", frozenset(self.requires))
        object.__setattr__(self, "produces", frozenset(self.produces))
        for key in self.requires | self.produces:
            validate_artifact_key(key)
        if not self.id:
            raise ValueError("NodeSpec.id must be a non-empty string.")

    def instantiate(self, **kwargs) -> GraphNode:
        """Instantiate the node using the configured factory."""

        if self.factory is None:
            raise TypeError(f"NodeSpec '{self.id}' does not define a factory.")
        node = self.factory(**kwargs)
        if node.id != self.id:
            raise ValueError(
                f"Node '{node.id}' does not match NodeSpec id '{self.id}'."
            )
        if node.node_kind != self.node_kind:
            raise ValueError(
                f"Node '{node.id}' kind {node.node_kind}"
                f" does not match spec kind {self.node_kind}."
            )
        if frozenset(node.requires) != self.requires:
            raise ValueError(
                f"Node '{node.id}' requires {node.requires}"
                f" but spec requires {sorted(self.requires)}."
            )
        if frozenset(node.produces) != self.produces:
            raise ValueError(
                f"Node '{node.id}' produces {node.produces}"
                f" but spec expects {sorted(self.produces)}."
            )
        return node

    def to_dict(self) -> Mapping[str, object]:
        """Return a serialisable representation of the node metadata."""

        return {
            "id": self.id,
            "node_kind": self.node_kind.value,
            "requires": sorted(self.requires),
            "produces": sorted(self.produces),
            "description": self.description,
        }
