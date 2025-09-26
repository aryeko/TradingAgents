"""High-level TradingSession facade for the modern runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from tradingagents.application.bootstrap import DataBootstrapper
from tradingagents.application.executor import ExecutionRecord, NodeExecutor
from tradingagents.application.nodes import default_node_specs
from tradingagents.application.planner import DependencyPlanner
from tradingagents.domain import SessionDataContext
from tradingagents.infrastructure.external import ExternalApiGateway

__all__ = ["SessionResult", "TradingSession"]


@dataclass
class SessionResult:
    context: SessionDataContext
    executed_nodes: Sequence[ExecutionRecord]
    plan: Sequence[str]


class TradingSession:
    """Coordinates bootstrapping, planning, and node execution."""

    def __init__(
        self,
        *,
        bootstrapper: DataBootstrapper | None = None,
        planner: DependencyPlanner | None = None,
        executor: NodeExecutor | None = None,
        gateway: ExternalApiGateway | None = None,
        node_specs: Iterable = (),
    ) -> None:
        self.bootstrapper = bootstrapper or DataBootstrapper()
        self.gateway = gateway
        self._provided_specs = list(node_specs)
        self._planner = planner
        self._executor = executor

    def run(
        self,
        *,
        ticker: str,
        as_of: str,
        context: SessionDataContext | None = None,
    ) -> SessionResult:
        runtime_context = context or SessionDataContext()
        gateway = self.gateway
        if gateway is None:
            raise ValueError("TradingSession requires an ExternalApiGateway instance.")

        self.bootstrapper.bootstrap(
            runtime_context,
            gateway,
            ticker=ticker,
            as_of=as_of,
        )

        specs = self._provided_specs or default_node_specs()
        planner = self._planner or DependencyPlanner(specs)
        plan = planner.plan(runtime_context)

        executor = self._executor or NodeExecutor()
        records = executor.execute(plan, runtime_context, gateway)

        return SessionResult(
            context=runtime_context,
            executed_nodes=records,
            plan=[spec.id for spec in plan],
        )
