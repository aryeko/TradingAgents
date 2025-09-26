# Codex Cloud Implementation Instructions

Use this document as the authoritative source when driving the modernization effort with Codex Cloud. It consolidates context, goals, constraints, and the step-by-step plan.

## Context
- Repository: `TradingAgents`
- Branch for modernization: `new-arch`
- Legacy documentation lives in `docs-v1/`; new architecture materials in `docs-v2/`
- Target architecture and rationale: `docs-v2/new-architecture/final-architecture.md` and `docs-v2/legacy-vs-modern.md`
- Detailed rollout plan: `docs-v2/implementation/master-plan.md`

## Goal
Implement the SOLID-aligned architecture described in `docs-v2/new-architecture/final-architecture.md` while preserving existing behaviour and ensuring thorough test coverage. Each story in the master plan must be completed in order, with passing tests and clean commits.

## Laws of the Engagement
1. **Feature Flags**: Keep the legacy runtime available via feature flag until full parity is demonstrated.
2. **Testing**: Run relevant unit tests plus `pytest -m e2e` after every story. Do not commit if tests fail.
3. **Mocking**: All external API calls (LLM, Finnhub, Yahoo Finance, Reddit, SimFin, etc.) must be mocked during tests.
4. **Commit Discipline**: One story per commit. Use conventional commit messages (`feat:`, `refactor:`, `chore:`, etc.).
5. **Documentation**: Update documentation and docstrings as new components are introduced. Cross-reference `docs-v2/` docs when appropriate.
6. **No Regression**: Maintain existing CLI behaviour until feature flag toggles the new runtime explicitly.
7. **Review Ready**: Ensure lint/tests pass and docs updated before finalizing each commit.

## Step-by-Step Plan (Stories)
Refer to `master-plan.md` for full details; summary below:
1. **S1 – Establish Mocked E2E Safety Net** *(Done)*
2. **S2 – Define Domain Contracts**: Introduce `SessionDataContext`, `GraphNode`, `NodeSpec`.
3. **S3 – Introduce External API Gateway**: Centralize outbound API calls with adapters and tests.
4. **S4 – Bootstrap Raw Data via Fetch Nodes**: Implement `DataBootstrapper` and `DataFetchNode`s with fail-fast behaviour.
5. **S5 – Migrate Analysts & Debaters to Graph Nodes**: Convert agent logic to node classes using the context and gateway.
6. **S6 – Implement Planner, Executor, Session Facade**: Build `DependencyPlanner`, `NodeExecutor`, `TradingSession`.
7. **S7 – Retire Legacy Toolkit & Interfaces**: Remove Toolkit/dataflows once new runtime is in place.
8. **S8 – Enhance Observability & Documentation**: Add logging/metrics, expand docs, broaden tests.

Each story lists prerequisites, implementation requirements, and validation commands in `master-plan.md`. Update the tracker status when a story starts (`🚧`) and completes (`✅`).

## Verification Checklist (per Story)
- [ ] Requirements implemented per master plan
- [ ] Unit tests added/updated and passing
- [ ] `pytest -m e2e` passing (with mocks)
- [ ] Documentation links/cross-references updated
- [ ] Commit created with conventional message

## Additional Resources
- `docs-v2/system-design.md`: High-level overview
- `docs-v2/components/`: Per-component deep dives
- `docs-v2/implementation/modernization-plan.md`: Detailed roadmap

Follow these instructions when formulating Codex Cloud prompts or automations to ensure consistency and alignment with project goals.
