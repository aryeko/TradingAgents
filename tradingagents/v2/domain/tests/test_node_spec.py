from dataclasses import dataclass
from typing import Mapping

import pytest

from tradingagents.v2.domain import NodeKind
from tradingagents.v2.domain.nodes import NodeSpec
from tradingagents.v2.domain.context import SessionDataContext


@dataclass
class DummyNode:
    id: str
    node_kind: NodeKind
    requires: frozenset[str]
    produces: frozenset[str]

    def execute(self, context: SessionDataContext, gateway: object) -> Mapping[str, object]:
        return {key: f"value for {key}" for key in self.produces}


class DummyFactory:
    def __init__(self, node: DummyNode) -> None:
        self.node = node
        self.calls = 0

    def __call__(self, **_: object) -> DummyNode:
        self.calls += 1
        return self.node


def test_instantiate_returns_valid_node():
    node = DummyNode(
        id="analysis.market",
        node_kind=NodeKind.ANALYSIS,
        requires=frozenset({"raw.market"}),
        produces=frozenset({"analysis.market_report"}),
    )
    factory = DummyFactory(node)
    spec = NodeSpec(
        id="analysis.market",
        node_kind=NodeKind.ANALYSIS,
        requires=node.requires,
        produces=node.produces,
        factory=factory,
        description="Market analyst",
    )

    created = spec.instantiate()

    assert created is node
    assert factory.calls == 1


def test_instantiate_validates_identity_and_metadata():
    node = DummyNode(
        id="wrong",
        node_kind=NodeKind.ANALYSIS,
        requires=frozenset({"raw.market"}),
        produces=frozenset({"analysis.market_report"}),
    )
    spec = NodeSpec(
        id="analysis.market",
        node_kind=NodeKind.ANALYSIS,
        requires=frozenset({"raw.market"}),
        produces=frozenset({"analysis.market_report"}),
        factory=lambda: node,
    )

    with pytest.raises(ValueError):
        spec.instantiate()


def test_missing_factory_raises_type_error():
    spec = NodeSpec(
        id="analysis.market",
        node_kind=NodeKind.ANALYSIS,
        requires=frozenset({"raw.market"}),
        produces=frozenset({"analysis.market_report"}),
    )

    with pytest.raises(TypeError):
        spec.instantiate()


@pytest.mark.parametrize(
    "requires,produces",
    [
        (frozenset({"raw.market"}), frozenset({"analysis.market_report"})),
        (frozenset(), frozenset()),
    ],
)
def test_to_dict_serialises_metadata(requires: frozenset[str], produces: frozenset[str]):
    spec = NodeSpec(
        id="analysis.market",
        node_kind=NodeKind.ANALYSIS,
        requires=requires,
        produces=produces,
    )

    payload = spec.to_dict()

    assert payload["id"] == "analysis.market"
    assert payload["node_kind"] == NodeKind.ANALYSIS.value
    assert payload["requires"] == sorted(requires)
    assert payload["produces"] == sorted(produces)
