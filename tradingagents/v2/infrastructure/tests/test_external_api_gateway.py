from collections import deque

import pytest

from tradingagents.v2.infrastructure.external import (
    ExternalApiGateway,
    ProviderInvocationError,
    ProviderNotRegisteredError,
    build_default_gateway,
)


class RecordingAdapter:
    def __init__(self, responses):
        self.responses = deque(responses)
        self.calls = []

    def invoke(self, operation, payload=None, *, timeout=None):
        self.calls.append({
            "operation": operation,
            "payload": payload,
            "timeout": timeout,
        })
        outcome = self.responses.popleft()
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_invoke_success_returns_adapter_response():
    adapter = RecordingAdapter([{"data": 42}])
    gateway = ExternalApiGateway({"stub": adapter}, default_timeout=5.0, max_retries=0)

    result = gateway.invoke("stub", "fetch", {"ticker": "AAPL"})

    assert result == {"data": 42}
    assert adapter.calls[0]["payload"] == {"ticker": "AAPL"}
    assert adapter.calls[0]["timeout"] == 5.0


def test_invoke_respects_override_timeout():
    adapter = RecordingAdapter(["ok"])
    gateway = ExternalApiGateway({"stub": adapter}, default_timeout=10.0, max_retries=0)

    gateway.invoke("stub", "fetch", {}, timeout=1.5)

    assert adapter.calls[0]["timeout"] == 1.5


def test_invoke_retries_until_success():
    adapter = RecordingAdapter([RuntimeError("boom"), {"status": "ok"}])
    gateway = ExternalApiGateway({"stub": adapter}, max_retries=1)

    result = gateway.invoke("stub", "fetch", {})

    assert result == {"status": "ok"}
    assert len(adapter.calls) == 2


def test_invoke_raises_after_max_retries():
    error = RuntimeError("failure")
    adapter = RecordingAdapter([error, error, error])
    gateway = ExternalApiGateway({"stub": adapter}, max_retries=2)

    with pytest.raises(ProviderInvocationError) as excinfo:
        gateway.invoke("stub", "fetch", {"ticker": "TSLA"})

    assert excinfo.value.provider == "stub"
    assert excinfo.value.operation == "fetch"
    assert excinfo.value.attempts == 3
    assert isinstance(excinfo.value.last_error, RuntimeError)


def test_invoke_requires_registered_provider():
    gateway = ExternalApiGateway()

    with pytest.raises(ProviderNotRegisteredError):
        gateway.invoke("unknown", "fetch", {})


def test_build_default_gateway_registers_stub_providers():
    gateway = build_default_gateway()

    providers = set(gateway.available_providers())

    assert providers == {
        "anthropic",
        "finnhub",
        "google",
        "offline_cache",
        "openai",
        "reddit",
        "simfin",
        "yahoo_finance",
    }
