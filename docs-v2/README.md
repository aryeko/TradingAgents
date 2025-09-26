# TradingAgents Modern Architecture Documentation

This documentation set covers the modern, SOLID-aligned architecture for TradingAgents. It complements `docs-v1/` (legacy reference) and focuses on the new runtime, dependency-planned execution, and migration guidance.

## Getting Started
1. Review the [System Design Overview](./system-design.md) for a quick tour of layers, components, and data flow.
2. Dive into component guides under `components/` for role-specific responsibilities and extension tips.
3. Consult the implementation plan under `implementation/` when rolling out or contributing to the modernization effort.
4. Use [legacy-vs-modern](./legacy-vs-modern.md) to understand motivations and key differences.

## Document Map
- [System Design Overview](./system-design.md)
- [Legacy vs Modern Comparison](./legacy-vs-modern.md)
- [Final Architecture Reference](./new-architecture/final-architecture.md)
- Component Guides (`components/`)
  - [Session Orchestration](./components/session-orchestration.md)
  - [Data Providers & Gateway](./components/data-platform.md)
  - [Agents & Nodes](./components/agents-and-nodes.md)
  - [Observability](./components/observability.md)
- Implementation Guides (`implementation/`)
  - [Master Plan](./implementation/master-plan.md)
  - [Modernization Plan](./implementation/modernization-plan.md)
  - Additional step-by-step docs as we progress.

Legacy documentation remains available under `docs-v1/` for historical reference.
