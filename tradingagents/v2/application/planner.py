"""Dependency planning for GraphNode execution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

from tradingagents.v2.domain import NodeSpec, SessionDataContext

__all__ = [
    "PlanningError",
    "UnresolvableDependencyError",
    "CycleDetectedError",
    "DependencyPlanner",
]


class PlanningError(RuntimeError):
    """Base class for planning-related failures."""


@dataclass(frozen=True)
class UnresolvableDependencyError(PlanningError):
    node_id: str
    missing_keys: Set[str]

    def __str__(self) -> str:  # pragma: no cover - simple formatting
        keys = ", ".join(sorted(self.missing_keys))
        return f"Node '{self.node_id}' depends on unknown artifacts: {keys}."


@dataclass(frozen=True)
class CycleDetectedError(PlanningError):
    remaining_nodes: Set[str]

    def __str__(self) -> str:  # pragma: no cover - simple formatting
        nodes = ", ".join(sorted(self.remaining_nodes))
        return f"Circular dependency detected among nodes: {nodes}."


class DependencyPlanner:
    """Build a deterministic execution plan based on node dependencies."""

    def __init__(self, node_specs: Iterable[NodeSpec]) -> None:
        specs = list(node_specs)
        self._spec_map: Dict[str, NodeSpec] = {}
        for spec in specs:
            if spec.id in self._spec_map:
                raise ValueError(f"Duplicate NodeSpec id detected: {spec.id}")
            self._spec_map[spec.id] = spec

    def plan(self, context: SessionDataContext) -> List[NodeSpec]:
        available_keys = set(context.snapshot().keys())
        remaining = dict(self._spec_map)

        # Validate that every requirement can be satisfied by either the context or a node.
        producible_keys = available_keys | {
            key for spec in remaining.values() for key in spec.produces
        }
        for spec in list(remaining.values()):
            missing = spec.requires - producible_keys
            if missing:
                raise UnresolvableDependencyError(spec.id, missing)

        plan: List[NodeSpec] = []
        while remaining:
            ready = [
                spec for spec in remaining.values() if spec.requires <= available_keys
            ]
            if not ready:
                raise CycleDetectedError(set(remaining))
            ready.sort(key=lambda spec: spec.id)
            for spec in ready:
                plan.append(spec)
                available_keys.update(spec.produces)
                remaining.pop(spec.id, None)
        return plan
