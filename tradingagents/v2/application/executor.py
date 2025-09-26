"""Node execution engine with basic retry semantics."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable, List

from tradingagents.v2.domain import DuplicateArtifactError, NodeSpec, SessionDataContext

__all__ = ["NodeExecutionError", "ExecutionRecord", "NodeExecutor"]


@dataclass(frozen=True)
class NodeExecutionError(RuntimeError):
    node_id: str
    attempts: int
    cause: Exception

    def __str__(self) -> str:  # pragma: no cover - formatting helper
        return f"Node '{self.node_id}' failed after {self.attempts} attempts: {self.cause}"


@dataclass
class ExecutionRecord:
    node_id: str
    attempts: int
    duration: float


class NodeExecutor:
    """Execute nodes produced by the planner and record basic metrics."""

    def __init__(self, *, max_retries: int = 0) -> None:
        self.max_retries = max_retries

    def execute(
        self,
        plan: Iterable[NodeSpec],
        context: SessionDataContext,
        gateway: object,
    ) -> List[ExecutionRecord]:
        records: List[ExecutionRecord] = []
        for spec in plan:
            node = spec.instantiate()
            attempts = 0
            start = time.perf_counter()
            while True:
                attempts += 1
                try:
                    outputs = node.execute(context, gateway)
                except Exception as exc:  # pragma: no cover - exercised via tests
                    if attempts > self.max_retries:
                        raise NodeExecutionError(spec.id, attempts, exc) from exc
                    continue
                for key, value in outputs.items():
                    if key in context:
                        continue
                    try:
                        context.publish(key, value)
                    except DuplicateArtifactError:
                        continue
                duration = time.perf_counter() - start
                records.append(ExecutionRecord(spec.id, attempts, duration))
                break
        return records
