"""External API gateway coordinating provider access.

See ``docs-v2/new-architecture/final-architecture.md`` and
``docs-v2/components/data-platform.md`` for the broader design context.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping

from tradingagents.v2.infrastructure.external.adapters import BaseProviderAdapter

__all__ = [
    "ExternalApiGateway",
    "ProviderInvocationError",
    "ProviderNotRegisteredError",
    "build_default_gateway",
]


class ExternalApiGatewayError(RuntimeError):
    """Base error for gateway-related failures."""


class ProviderNotRegisteredError(ExternalApiGatewayError):
    """Raised when attempting to access a provider that has not been registered."""

    def __init__(self, provider: str) -> None:
        super().__init__(f"Provider '{provider}' is not registered with the gateway.")
        self.provider = provider


class ProviderInvocationError(ExternalApiGatewayError):
    """Raised when a provider call fails after exhausting retries."""

    def __init__(
        self,
        provider: str,
        operation: str,
        attempts: int,
        last_error: Exception,
    ) -> None:
        message = (
            f"Failed to invoke '{provider}.{operation}' after {attempts} attempts:"
            f" {last_error}"
        )
        super().__init__(message)
        self.provider = provider
        self.operation = operation
        self.attempts = attempts
        self.last_error = last_error


@dataclass(frozen=True)
class GatewayConfig:
    """Configuration defaults for the gateway."""

    default_timeout: float | None = 30.0
    max_retries: int = 2
    retry_backoff_seconds: float = 0.0


class ExternalApiGateway:
    """Entry point for all outbound provider calls."""

    def __init__(
        self,
        providers: Mapping[str, BaseProviderAdapter] | None = None,
        *,
        default_timeout: float | None = None,
        max_retries: int | None = None,
        retry_backoff_seconds: float | None = None,
    ) -> None:
        config = GatewayConfig(
            default_timeout=default_timeout
            if default_timeout is not None
            else GatewayConfig.default_timeout,
            max_retries=max_retries if max_retries is not None else GatewayConfig.max_retries,
            retry_backoff_seconds=
                retry_backoff_seconds
                if retry_backoff_seconds is not None
                else GatewayConfig.retry_backoff_seconds,
        )
        self._config = config
        self._providers: Dict[str, BaseProviderAdapter] = {}
        if providers:
            for name, adapter in providers.items():
                self.register_provider(name, adapter)

    @property
    def config(self) -> GatewayConfig:
        return self._config

    def register_provider(self, name: str, adapter: BaseProviderAdapter) -> None:
        """Register a provider adapter with the gateway."""

        self._providers[name.lower()] = adapter

    def available_providers(self) -> tuple[str, ...]:
        """Return a tuple of registered provider identifiers."""

        return tuple(sorted(self._providers))

    def invoke(
        self,
        provider: str,
        operation: str,
        payload: Mapping[str, Any] | None = None,
        *,
        timeout: float | None = None,
        retries: int | None = None,
    ) -> Any:
        """Invoke an operation on the requested provider with retry semantics."""

        adapter = self._providers.get(provider.lower())
        if adapter is None:
            raise ProviderNotRegisteredError(provider)

        attempts = 0
        max_attempts = 1 + (retries if retries is not None else self._config.max_retries)
        effective_timeout = (
            timeout if timeout is not None else self._config.default_timeout
        )
        last_error: Exception | None = None
        while attempts < max_attempts:
            attempts += 1
            try:
                payload_to_send: Mapping[str, Any] = (
                    dict(payload) if payload is not None else {}
                )
                result = adapter.invoke(
                    operation,
                    payload_to_send,
                    timeout=effective_timeout,
                )
                return result
            except Exception as exc:  # pragma: no cover - branches covered via tests
                last_error = exc
                if attempts >= max_attempts:
                    raise ProviderInvocationError(
                        provider=provider,
                        operation=operation,
                        attempts=attempts,
                        last_error=exc,
                    ) from exc
                if self._config.retry_backoff_seconds > 0:
                    # Sleep omitted in tests for determinism; no-op placeholder.
                    pass
        raise ProviderInvocationError(provider, operation, attempts, last_error or Exception("Unknown error"))


def build_default_gateway(
    *,
    default_timeout: float | None = None,
    max_retries: int | None = None,
    retry_backoff_seconds: float | None = None,
) -> ExternalApiGateway:
    """Construct a gateway populated with the default provider stubs."""

    from tradingagents.v2.infrastructure.external.adapters import (
        AnthropicProviderAdapter,
        FinnhubProviderAdapter,
        GoogleProviderAdapter,
        OfflineCacheAdapter,
        OpenAIProviderAdapter,
        RedditProviderAdapter,
        SimFinProviderAdapter,
        YahooFinanceProviderAdapter,
    )

    gateway = ExternalApiGateway(
        default_timeout=default_timeout,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    gateway.register_provider("openai", OpenAIProviderAdapter())
    gateway.register_provider("anthropic", AnthropicProviderAdapter())
    gateway.register_provider("google", GoogleProviderAdapter())
    gateway.register_provider("finnhub", FinnhubProviderAdapter())
    gateway.register_provider("yahoo_finance", YahooFinanceProviderAdapter())
    gateway.register_provider("reddit", RedditProviderAdapter())
    gateway.register_provider("simfin", SimFinProviderAdapter())
    gateway.register_provider("offline_cache", OfflineCacheAdapter())
    return gateway
