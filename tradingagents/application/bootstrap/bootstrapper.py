"""Bootstrap raw session data via dedicated fetch nodes."""
from __future__ import annotations

from typing import Iterable, Mapping

from tradingagents.application.nodes.data_fetch import DataFetchNode, default_data_fetch_nodes
from tradingagents.domain import (
    DuplicateArtifactError,
    SessionDataContext,
)
from tradingagents.infrastructure.external import ExternalApiGateway

__all__ = ["BootstrapFailure", "DataBootstrapper", "default_fetch_nodes"]


class BootstrapFailure(RuntimeError):
    """Raised when the bootstrapper cannot produce required session artifacts."""

    def __init__(self, node_id: str, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.node_id = node_id
        self.cause = cause
        if cause is not None:
            self.__cause__ = cause


class DataBootstrapper:
    """Fetches and publishes raw session data before node execution."""

    METADATA_NODE_ID = "bootstrap.metadata"

    def __init__(self, fetch_nodes: Iterable[DataFetchNode] | None = None) -> None:
        self._fetch_nodes = tuple(fetch_nodes or default_data_fetch_nodes())

    @property
    def fetch_nodes(self) -> tuple[DataFetchNode, ...]:
        return self._fetch_nodes

    def bootstrap(
        self,
        context: SessionDataContext,
        gateway: ExternalApiGateway,
        *,
        ticker: str,
        as_of: str,
    ) -> Mapping[str, object]:
        """Run the bootstrap flow and return the published artifacts."""

        self._ensure_session_metadata(context, ticker=ticker, as_of=as_of)
        published: dict[str, object] = {}

        for node in self._fetch_nodes:
            if not context.is_ready(node.requires):
                missing = sorted(req for req in node.requires if req not in context)
                raise BootstrapFailure(
                    node.id,
                    f"Missing prerequisites for {node.id}: {', '.join(missing)}",
                )
            try:
                outputs = node.execute(context, gateway)
            except Exception as exc:  # pragma: no cover - wrapped below
                raise BootstrapFailure(node.id, "Failed to fetch data", cause=exc) from exc

            for key, value in outputs.items():
                if key in context:
                    continue
                try:
                    context.publish(key, value)
                except DuplicateArtifactError:
                    continue
                published[key] = value

        return published

    def _ensure_session_metadata(
        self,
        context: SessionDataContext,
        *,
        ticker: str,
        as_of: str,
    ) -> None:
        if "session.ticker" in context:
            existing = context.require("session.ticker")
            if existing != ticker:
                raise BootstrapFailure(
                    self.METADATA_NODE_ID,
                    f"Session ticker '{existing}' does not match bootstrap request '{ticker}'.",
                )
        else:
            context.publish("session.ticker", ticker)

        if "session.as_of" in context:
            existing = context.require("session.as_of")
            if existing != as_of:
                raise BootstrapFailure(
                    self.METADATA_NODE_ID,
                    f"Session as_of '{existing}' does not match bootstrap request '{as_of}'.",
                )
        else:
            context.publish("session.as_of", as_of)


def default_fetch_nodes() -> tuple[DataFetchNode, ...]:
    """Expose the default fetch node factory for consumers."""

    return tuple(default_data_fetch_nodes())
