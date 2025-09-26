from datetime import datetime

import pytest

from tradingagents.domain import (
    DuplicateArtifactError,
    InvalidArtifactNamespaceError,
    MissingArtifactError,
    SessionDataContext,
)


def test_require_returns_published_value():
    context = SessionDataContext({"raw.market": {"price": 123}})
    assert context.require("raw.market") == {"price": 123}


def test_require_raises_for_missing_key():
    context = SessionDataContext()
    with pytest.raises(MissingArtifactError):
        context.require("analysis.market_report")


def test_publish_rejects_duplicate_keys():
    context = SessionDataContext()
    context.publish("raw.market", {"price": 100})
    with pytest.raises(DuplicateArtifactError):
        context.publish("raw.market", {"price": 101})


@pytest.mark.parametrize("invalid_key", ["raw", "", "analysis."])
def test_publish_rejects_invalid_namespaces(invalid_key: str):
    context = SessionDataContext()
    with pytest.raises(InvalidArtifactNamespaceError):
        context.publish(invalid_key, {})


def test_is_ready_checks_all_requirements():
    context = SessionDataContext({"raw.market": {}})
    assert not context.is_ready({"raw.market", "raw.news"})
    context.publish("raw.news", {"headlines": []})
    assert context.is_ready({"raw.market", "raw.news"})


def test_snapshot_returns_copy():
    context = SessionDataContext()
    payload = {"timestamp": datetime(2024, 1, 1)}
    context.publish("analysis.market_report", payload)

    snapshot = context.snapshot()
    assert snapshot == {"analysis.market_report": payload}
    snapshot["analysis.market_report"] = {}
    assert context.require("analysis.market_report") is payload
