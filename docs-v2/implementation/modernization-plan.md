# TradingAgents Modernization Plan

## 1. Purpose
This document translates the proposed SOLID-aligned architecture into an actionable roadmap. It covers the target design, introduces the graph node taxonomy, and sequences work so we can evolve the system safely while preserving behaviour via automated tests.

## 2. Design Overview
- **SessionDataContext**: central store for raw feeds, derived artifacts, and decision outputs; exposes `require`/`publish` helpers plus readiness checks.
- **GraphNode Protocol**: common interface implemented by every runtime node (`id`, `node_kind`, `requires`, `produces`, `execute(context, gateway)`). Node kinds include `data_fetch`, `analysis`, `aggregation`, `debate`, `risk`, `decision`, and `report`.
- **ExternalApiGateway**: single choke point for outbound API usage (LLMs, data providers). Handles retries, rate-limits, and enables consistent mocking in tests.
- **DataFetchNodes**: fetch raw data once per session (e.g., market, news, fundamentals). They fail-fast and surface `NodeExecutionError` to stop execution when required feeds are unavailable.
- **DependencyPlanner**: builds a DAG from node specs and SessionDataContext readiness. Dispatches nodes only when their prerequisites are satisfied.
- **TradingSession Facade**: orchestrates bootstrap, planning, execution, and persistence; presentation layers (CLI, LangGraph adapter) interact only with this facade.

## 3. Implementation Roadmap
Each step below lists prerequisites and verification gates. The very first milestone establishes end-to-end coverage with mocked APIs so every later change is checked against current behaviour.

### Step 1 — Establish End-to-End Safety Net
**Objective**: Add reproducible e2e tests that cover the current CLI and graph workflow while mocking all external APIs.
- **Prerequisites**
  - Inventory of existing CLI entry points (`python -m cli.main`) and key graph paths (`TradingAgentsGraph.propagate`).
  - Catalog of external services to mock (OpenAI, Anthropic, Google, Finnhub, Yahoo Finance, Reddit, SimFin).
- **Implementation**
  - Introduce a pytest marker `e2e` and fixture scaffolding under `tests/e2e/`.
  - Build mock clients/adapters that simulate API responses using recorded fixtures (YAML/JSON) to reproduce typical BUY/SELL/HOLD runs.
  - Add CLI smoke test invoking the current graph via subprocess or in-process call with mocked environment variables.
  - Document test execution in `README.md` (e.g., `pytest -m e2e`).
- **Verification**
  - `pytest -m e2e` passes with all mocks active.
  - Verify logs/results match baseline fixture expectations.
  - Ensure tests fail if live network calls slip through (assert via mock spies).

### Step 2 — Define Core Domain Contracts
**Objective**: Introduce `SessionDataContext`, graph node descriptors, and shared domain models without altering runtime behaviour.
- **Prerequisites**
  - Step 1 e2e suite green.
  - Agreement on naming conventions and package boundaries (`tradingagents/domain`, `tradingagents/application`).
- **Implementation**
  - Create `tradingagents/domain/context/session_data_context.py` implementing the context API (`require`, `publish`, `is_ready`, immutability guarantees).
  - Define `GraphNode` protocol and data classes (`NodeSpec`) under `tradingagents/domain/nodes/`.
  - Add enumerations for `NodeKind` and typed identifiers for commonly shared artifacts.
  - Write unit tests validating context semantics (e.g., duplicate publish guard, readiness checks).
- **Verification**
  - Unit tests for the new modules pass.
  - Existing e2e tests still run against the legacy path (no behaviour change yet).

### Step 3 — Implement ExternalApiGateway
**Objective**: Centralise outbound API access via a gateway node and adapters.
- **Prerequisites**
  - Step 2 merged and context imports available.
  - Inventory of current API client usages inside agents/toolkit.
- **Implementation**
  - Create `tradingagents/infrastructure/external/gateway.py` exposing sync/async `invoke` methods that accept `provider`, `operation`, and payload.
  - Wrap existing LLM/data clients in adapter classes that the gateway delegates to; ensure the gateway can swap real clients for mocks.
  - Update tests to mock the gateway instead of individual SDKs.
- **Verification**
  - New gateway unit tests cover retry, logging, and error surfacing.
  - e2e suite updated to inject mocked gateway responses continues to pass.
  - Static analysis/linters confirm no direct SDK imports in high-level nodes.

### Step 4 — Introduce DataFetchNodes and Bootstrap Flow
**Objective**: Move all data acquisition into explicit data-fetch nodes executed through the planner.
- **Prerequisites**
  - Gateway operational with mocks.
  - Clear mapping from existing toolkit/dataflow functions to new providers.
- **Implementation**
  - Implement `DataFetchNode` subclasses for market, news, fundamentals, sentiment (one per provider group).
  - Register these nodes with the planner, ensuring they populate distinct context keys (`raw.market`, `raw.news`, etc.).
  - Create `BootstrapFailure` exceptions that abort the session when a fetch node fails.
  - Deprecate direct toolkit calls for data fetching in favour of context consumption.
- **Verification**
  - Unit tests simulate provider failures and assert the session halts early.
  - e2e suite passes, demonstrating data fetched exactly once per session.
  - Instrumentation/logs show new node execution order.

### Step 5 — Refactor Analysis and Debate Nodes
**Objective**: Migrate analyst, researcher, and risk agents to the GraphNode contract and context-driven data access.
- **Prerequisites**
  - Data fetch nodes in place and context populated with raw feeds.
  - Updated prompts/design docs specifying required inputs/outputs per agent.
- **Implementation**
  - Convert each agent factory to return a `GraphNode` implementation (`MarketAnalystNode`, `NewsAnalystNode`, etc.).
  - Replace toolkit usage with `context.require` calls and route all LLM requests through `ExternalApiGateway`.
  - Ensure each node publishes structured artifacts (`analysis.market_report`, `debate.summary`, `risk.assessment`).
  - Add focused unit tests per node that stub the gateway and context.
- **Verification**
  - Node unit tests cover success/failure paths and output schema.
  - e2e suite confirms orchestration still produces identical BUY/SELL/HOLD decisions with mocked APIs.
  - Code review verifies no residual dependency on legacy toolkit functions inside nodes.

### Step 6 — Build DependencyPlanner and NodeExecutor
**Objective**: Replace LangGraph-centric orchestration with the new dependency-aware scheduler while keeping CLI compatibility.
- **Prerequisites**
  - Nodes conform to `GraphNode` protocol.
  - Clear mapping of dependencies between nodes (captured in specs/metadata).
- **Implementation**
  - Implement `DependencyPlanner` to construct the execution DAG and expose `next_ready_nodes`.
  - Develop `NodeExecutor` that pulls from the planner, runs nodes, and handles error propagation/metrics.
  - Wrap the executor inside a revamped `TradingSession` facade and adapt CLI entry points to use it.
  - Maintain a thin LangGraph adapter if needed during transition.
- **Verification**
  - Unit tests for planner/executor ensure correct scheduling and cycle detection.
  - Run e2e suite comparing outputs from old graph vs new executor (guarded by feature flag). The new path must match baseline decisions/logs.
  - Performance benchmarks show no unacceptable regression.

### Step 7 — Retire Legacy Toolkit and Dataflows Interface
**Objective**: Remove deprecated modules once all nodes use the new abstractions.
- **Prerequisites**
  - All runtime paths pointing to new gateway/context.
  - Feature flag toggling between new and legacy orchestration demonstrates parity.
- **Implementation**
  - Delete `Toolkit`, `dataflows/interface.py`, and unused helpers; replace with provider adapters tied to the gateway.
  - Update imports across the codebase.
  - Refresh documentation (`README.md`, CLI docs) to describe the new architecture and testing strategy.
- **Verification**
  - Linting and typing succeed with removed modules.
  - e2e suite and targeted unit tests all pass.
  - Repository-wide search confirms no references to removed modules.

### Step 8 — Extend Test and Monitoring Coverage
**Objective**: Harden the modernised system with regression and observability enhancements.
- **Prerequisites**
  - Legacy code fully decommissioned.
  - New orchestration enabled by default.
- **Implementation**
  - Expand e2e scenarios (bullish, bearish, neutral) and add property-based tests for context dependency graphs.
  - Instrument gateway and executor with structured logging/metrics hooks.
  - Integrate CI workflows to run e2e suite with mocked providers by default and optionally against live services.
- **Verification**
  - CI passes with new test jobs.
  - Logs/metrics observable in local/dev environments.
  - Documentation updated with troubleshooting guidance and monitoring endpoints.

## 4. Rollout Strategy
- Use feature flags to switch between legacy LangGraph orchestration and the new executor during Steps 5–6.
- After each milestone, run the full e2e suite to ensure behaviour parity.
- Schedule periodic syncs with stakeholders to review progress and adjust the plan based on discoveries from testing or performance profiling.

## 5. Risks & Mitigations
- **Mock drift**: Regularly refresh API fixtures and validate schema changes via contract tests.
- **Dependency cycles**: Enforce planner validation and static checks on `requires` definitions.
- **Cost regressions**: Measure LLM call counts per e2e run; optimise prompts/nodes if costs increase.
- **Team adoption**: Provide example node implementations and migration playbooks to help contributors onboard to the new model.

## 6. References
- Current system design (`docs/system-design.md`).
- Architecture discussion notes (internal).
- LangGraph documentation for interoperability during transition.
