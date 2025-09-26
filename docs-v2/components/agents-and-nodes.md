# Agents & Graph Nodes

This guide describes how analyst, researcher, trader, and risk roles map into GraphNode implementations.

## Node Types
- **Analysis Nodes**: Market, sentiment, news, fundamentals analysts translate raw data into reports.
- **Aggregation Nodes**: Research manager consolidates analyst outputs and drafts investment plans.
- **Debate Nodes**: Bull/Bear researchers and risk analysts debate strategies, updating debate states.
- **Decision Nodes**: Trader and risk judge turn debate outcomes into final trade decisions and signals.

## Contracts
Each node implements the `GraphNode` protocol:
- `id`: Stable identifier.
- `node_kind`: Enum describing the node category.
- `requires`: Set of context keys required before execution.
- `produces`: Set of keys published upon completion.
- `execute(context, gateway)`: Core logic.

## Memory Integration
Nodes can optionally pull reflections or prior decisions from memory adapters via the gateway, ensuring lessons learned influence current reasoning.

## Testing Strategy
- Unit tests mock `SessionDataContext` and `ExternalApiGateway` to ensure nodes consume/publish the correct artifacts.
- E2E tests verify end-to-end decision parity under mocked conditions.

## Related Documents
- [Final Architecture](../new-architecture/final-architecture.md)
- [Legacy vs Modern Comparison](../legacy-vs-modern.md)
