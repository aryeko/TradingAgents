"""Session-scoped artifact store for the modern TradingAgents runtime.

The :class:`SessionDataContext` is introduced as part of the SOLID-aligned
architecture outlined in ``docs-v2/new-architecture/final-architecture.md``.
It provides deterministic data sharing across nodes, preventing accidental
mutation and making orchestration decisions reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping

__all__ = [
    "DuplicateArtifactError",
    "InvalidArtifactNamespaceError",
    "MissingArtifactError",
    "SessionDataContext",
    "validate_artifact_key",
]


class SessionDataContextError(RuntimeError):
    """Base class for context-related issues."""


class MissingArtifactError(SessionDataContextError):
    """Raised when a required artifact has not yet been published."""

    def __init__(self, key: str) -> None:
        super().__init__(f"Artifact '{key}' is missing from the session context.")
        self.key = key


class DuplicateArtifactError(SessionDataContextError):
    """Raised when attempting to publish an artifact more than once."""

    def __init__(self, key: str) -> None:
        super().__init__(f"Artifact '{key}' has already been published.")
        self.key = key


class InvalidArtifactNamespaceError(SessionDataContextError):
    """Raised when an artifact key does not follow the required namespace rules."""

    def __init__(self, key: str) -> None:
        super().__init__(
            "Artifact keys must be namespaced (e.g., 'raw.market')."
            f" Received: '{key}'."
        )
        self.key = key


def validate_artifact_key(key: str) -> None:
    if not isinstance(key, str) or "." not in key:
        raise InvalidArtifactNamespaceError(str(key))
    segments = key.split(".")
    if any(not segment.strip() for segment in segments):
        raise InvalidArtifactNamespaceError(key)


@dataclass(frozen=True)
class _ContextState:
    """Immutable snapshot state."""

    artifacts: Dict[str, Any]


class SessionDataContext:
    """Shared store for artifacts exchanged between graph nodes.

    The context enforces namespaced keys (``raw.*``, ``analysis.*`` etc.) and
    guards against accidental duplicate writes. Nodes obtain their dependencies
    via :meth:`require` and publish new data with :meth:`publish`.
    """

    def __init__(self, initial_data: Mapping[str, Any] | None = None) -> None:
        self._state = _ContextState(artifacts={})
        if initial_data:
            for key, value in dict(initial_data).items():
                validate_artifact_key(key)
                self._state.artifacts[key] = value

    def require(self, key: str) -> Any:
        """Return the artifact for ``key`` or raise :class:`MissingArtifactError`."""

        validate_artifact_key(key)
        try:
            return self._state.artifacts[key]
        except KeyError as exc:  # pragma: no cover - exercised via error path
            raise MissingArtifactError(key) from exc

    def publish(self, key: str, value: Any) -> Any:
        """Publish ``value`` under ``key`` if it has not been published before."""

        validate_artifact_key(key)
        if key in self._state.artifacts:
            raise DuplicateArtifactError(key)
        self._state.artifacts[key] = value
        return value

    def is_ready(self, requirements: Iterable[str]) -> bool:
        """Return ``True`` when every requirement has been published."""

        for key in requirements:
            if key not in self._state.artifacts:
                return False
        return True

    def snapshot(self) -> Dict[str, Any]:
        """Return a shallow copy of the stored artifacts."""

        return dict(self._state.artifacts)

    def __contains__(self, key: object) -> bool:  # pragma: no cover - simple passthrough
        return key in self._state.artifacts

    def __repr__(self) -> str:  # pragma: no cover - diagnostic helper
        return f"SessionDataContext(artifacts={self._state.artifacts!r})"
