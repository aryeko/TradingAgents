# TradingAgents Modern Architecture Master Plan

This master plan governs the rollout of the SOLID-aligned architecture described in `docs-v2/new-architecture/final-architecture.md`. Follow the stories in order, ensuring every requirement and validation is complete before marking a story done. Tests must be run **before every commit** and all external APIs must remain mocked during automated runs.

## Tracker

| Story | Title | Status | Owner | Validation Summary |
|-------|-------|--------|-------|--------------------|
| S1 | Establish Mocked E2E Safety Net | ✅ Done | Core team | `pytest -m e2e` (mocked) |
| S2 | Define Domain Contracts | ⏳ Pending | Architecture squad | `pytest tests/domain -q`, `pytest -m e2e` |
| S3 | Introduce External API Gateway | ⏳ Pending | Infrastructure squad | `pytest tests/domain tests/infrastructure -q`, `pytest -m e2e` |
| S4 | Bootstrap Raw Data via Fetch Nodes | ⏳ Pending | Data platform squad | `pytest tests/domain tests/infrastructure tests/application -q`, `pytest -m e2e` |
| S5 | Migrate Analysts & Debaters to Graph Nodes | ⏳ Pending | Research agents squad | `pytest tests/application -q`, `pytest -m e2e` |
| S6 | Implement Planner, Executor, and Session Facade | ⏳ Pending | Runtime squad | `pytest tests/application tests/domain -q`, `pytest -m e2e` |
| S7 | Retire Legacy Toolkit & Interfaces | ⏳ Pending | Core maintainers | `pytest`, `pytest -m e2e` |
| S8 | Enhance Observability & Documentation | ⏳ Pending | Ops & Docs squad | `pytest`, `pytest -m e2e`, manual doc review |

> **Status legend**: ✅ Done, ⏳ Pending, 🚧 In Progress (update when work begins).

## Story Details

### Story S1 — Establish Mocked E2E Safety Net _(✅ Done)_
- **Objective**: Capture current behaviour with deterministic end-to-end tests that fully mock LLM and market data APIs.
- **Requirements**:
  - Add pytest marker `e2e` and fixtures under `tests/` that replace all network calls with pure-Python doubles.
  - Cover CLI and direct graph entry points to lock in BUY/SELL/HOLD outputs.
  - Document execution command (`pytest -m e2e`) in repo docs.
- **Validation**:
  - `pytest -m e2e`
  - Confirm no live HTTP requests (inspect mocks/logs).

### Story S2 — Define Domain Contracts _(⏳ Pending)_
- **Objective**: Introduce the core abstractions that decouple orchestration from infrastructure.
- **Requirements**:
  - Implement `SessionDataContext` with `require`, `publish`, `is_ready`, duplicate protection, and namespaced keys.
  - Create `GraphNode` protocol, `NodeKind` enum, and `NodeSpec` data model.
  - Provide docstrings referencing `final-architecture.md`.
- **Validation**:
  - Unit tests for context and node specs covering happy paths and error cases.
  - Run `pytest tests/domain -q` and `pytest -m e2e`.

### Story S3 — Introduce External API Gateway _(⏳ Pending)_
- **Objective**: Centralise outbound API access so business logic no longer instantiates SDKs directly.
- **Requirements**:
  - Implement `ExternalApiGateway` with sync `invoke(provider, operation, payload)` signature.
  - Create adapter stubs for OpenAI, Anthropic, Google, Finnhub, Yahoo Finance, Reddit, SimFin, and offline caches.
  - Support retries, timeout configuration, and error normalization.
  - Update existing modules to reference the gateway (no behaviour change yet).
- **Validation**:
  - Unit tests using monkeypatch to simulate success/failure and retry behaviour.
  - Run `pytest tests/domain tests/infrastructure -q` and `pytest -m e2e`.

### Story S4 — Bootstrap Raw Data via Fetch Nodes _(⏳ Pending)_
- **Objective**: Fetch all required datasets once per session, failing fast on missing feeds.
- **Requirements**:
  - Create `DataBootstrapper` and `DataFetchNode` subclasses for market, news, fundamentals, sentiment data.
  - Publish `raw.*` artifacts into `SessionDataContext` using gateway adapters.
  - Introduce `BootstrapFailure` for critical errors.
  - Add feature flag wiring so bootstrapper can be invoked without replacing legacy runtime yet.
- **Validation**:
  - Unit tests for bootstrap success/failure, ensuring context keys populated correctly.
  - Run `pytest tests/domain tests/infrastructure tests/application -q` and `pytest -m e2e`.

### Story S5 — Migrate Analysts & Debaters to Graph Nodes _(⏳ Pending)_
- **Objective**: Convert market, sentiment, news, fundamentals, bull, bear, trader, and risk agents to `GraphNode`s using the shared context and gateway.
- **Requirements**:
  - Implement node classes under `tradingagents/application/nodes/` with declarative `requires`/`produces` definitions.
  - Replace direct Toolkit usage with context access and gateway calls.
  - Provide fixture-backed unit tests for each node verifying published artifacts.
  - Update prompts as needed to reference structured data.
- **Validation**:
  - `pytest tests/application -q`
  - `pytest -m e2e`

### Story S6 — Implement Planner, Executor, and Session Facade _(⏳ Pending)_
- **Objective**: Build the runtime engine that sequences nodes according to dependencies.
- **Requirements**:
  - Implement `DependencyPlanner` (cycle detection, readiness checks) and `NodeExecutor` (retry policy, metrics hooks).
  - Create `TradingSession` facade composing bootstrapper, planner, and executor.
  - Provide compatibility layer for CLI via feature flag `USE_NEW_RUNTIME`.
- **Validation**:
  - Unit tests for planner/executor edge cases.
  - Run `pytest tests/application tests/domain -q` and `pytest -m e2e`.

### Story S7 — Retire Legacy Toolkit & Interfaces _(⏳ Pending)_
- **Objective**: Remove obsolete utilities after all nodes use the new abstractions.
- **Requirements**:
  - Delete `Toolkit`, `tradingagents/dataflows/interface.py`, and unused helpers.
  - Replace import sites with gateway/providers.
  - Update documentation and changelog to reflect removal.
- **Validation**:
  - Run full `pytest` suite.
  - Run `pytest -m e2e`.

### Story S8 — Enhance Observability & Documentation _(⏳ Pending)_
- **Objective**: Finalise the rollout with monitoring hooks and refreshed documentation.
- **Requirements**:
  - Add structured logging/metrics to gateway and executor (latency, retries, cost estimates).
  - Expand docs in `docs-v2` with implementation guidance and migration notes.
  - Broaden e2e coverage to bullish/bearish/neutral fixture scenarios.
- **Validation**:
  - Run full `pytest` suite and `pytest -m e2e`.
  - Manual doc review for accuracy and completeness.

## Execution Notes
- Use conventional commits for each story. No merges between stories until their tests pass.
- Keep `docs-v1` as the reference set for the legacy architecture; update links when stories cut over to the new runtime.
- Update the tracker table after each story: change status to 🚧 when in progress and ✅ once validations finish.
- Communicate progress during weekly syncs, sharing test run outputs and notable findings.
