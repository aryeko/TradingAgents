"""Provider adapter stubs for the ExternalApiGateway.

The actual implementations will be fleshed out in later modernization
stories. For now they provide a consistent interface for the gateway and
allow tests to register doubles without hitting live services.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

__all__ = [
    "BaseProviderAdapter",
    "OpenAIProviderAdapter",
    "AnthropicProviderAdapter",
    "GoogleProviderAdapter",
    "FinnhubProviderAdapter",
    "YahooFinanceProviderAdapter",
    "RedditProviderAdapter",
    "SimFinProviderAdapter",
    "OfflineCacheAdapter",
]


class BaseProviderAdapter(Protocol):
    """Protocol for provider adapters consumed by the gateway."""

    provider_name: str

    def invoke(
        self,
        operation: str,
        payload: Mapping[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> Any:
        ...


@dataclass
class _StubAdapter:
    provider_name: str

    def invoke(
        self,
        operation: str,
        payload: Mapping[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> Any:
        raise NotImplementedError(
            "Provider adapter stubs do not implement runtime behaviour yet."
        )


class OpenAIProviderAdapter(_StubAdapter):
    def __init__(self) -> None:
        super().__init__(provider_name="openai")


class AnthropicProviderAdapter(_StubAdapter):
    def __init__(self) -> None:
        super().__init__(provider_name="anthropic")


class GoogleProviderAdapter(_StubAdapter):
    def __init__(self) -> None:
        super().__init__(provider_name="google")


class FinnhubProviderAdapter(_StubAdapter):
    def __init__(self) -> None:
        super().__init__(provider_name="finnhub")


class YahooFinanceProviderAdapter(_StubAdapter):
    def __init__(self) -> None:
        super().__init__(provider_name="yahoo_finance")


class RedditProviderAdapter(_StubAdapter):
    def __init__(self) -> None:
        super().__init__(provider_name="reddit")


class SimFinProviderAdapter(_StubAdapter):
    def __init__(self) -> None:
        super().__init__(provider_name="simfin")


class OfflineCacheAdapter(_StubAdapter):
    def __init__(self) -> None:
        super().__init__(provider_name="offline_cache")
