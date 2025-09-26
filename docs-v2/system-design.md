# System Design Overview (Modern Architecture)

This overview summarizes the SOLID-aligned runtime described in the master plan. For deep dives, follow the component links below.

## 1. Architecture Layers
- **Presentation**: CLI, Python API, optional LangGraph adapter.
- **Application**: `TradingSession` facade, `DependencyPlanner`, `NodeExecutor`, `DataBootstrapper`.
- **Domain**: `SessionDataContext`, `GraphNode` protocol, node specs, domain models.
- **Infrastructure**: `ExternalApiGateway`, provider adapters, memory stores, result persistence.

## 2. Execution Flow
1. Presentation layer invokes `TradingSession` with configuration and ticker/date.
2. `DataBootstrapper` fetches raw datasets once; failures raise `BootstrapFailure`.
3. `DependencyPlanner` constructs a DAG of nodes based on `requires`/`produces` metadata.
4. `NodeExecutor` runs ready nodes, piping LLM/data access through the gateway and publishing artifacts to the context.
5. Final artifacts (decision, audit trail) are persisted, and callers receive structured results.

## 3. Key Contracts
- `SessionDataContext`: Immutable-friendly store with `require`, `publish`, and readiness checks.
- `GraphNode`: Interface implemented by every node, encapsulating business logic.
- `ExternalApiGateway`: Central entry point for outbound API/service calls.

## 4. Transition Approach
The modernization plan migrates components in stages, using feature flags to keep the legacy `TradingAgentsGraph` available until parity is achieved. Refer to `implementation/master-plan.md` for the full rollout sequence.

## 5. Resources
- [Final Architecture](./new-architecture/final-architecture.md)
- [Modernization Plan](./implementation/modernization-plan.md)
- [Legacy vs Modern Comparison](./legacy-vs-modern.md)
