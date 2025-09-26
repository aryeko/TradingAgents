"""Domain-layer contracts for the modern TradingAgents architecture.

Refer to ``docs-v2/new-architecture/final-architecture.md`` for the
comprehensive overview of how these abstractions collaborate with the
application and infrastructure layers.
"""

from .context.session_data_context import (
    DuplicateArtifactError,
    InvalidArtifactNamespaceError,
    MissingArtifactError,
    SessionDataContext,
    validate_artifact_key,
)
from .nodes.graph_node import GraphNode, NodeKind
from .nodes.node_spec import NodeSpec

__all__ = [
    "DuplicateArtifactError",
    "InvalidArtifactNamespaceError",
    "MissingArtifactError",
    "SessionDataContext",
    "GraphNode",
    "NodeKind",
    "NodeSpec",
    "validate_artifact_key",
]
