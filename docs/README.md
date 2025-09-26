# TradingAgents Documentation

TradingAgents is a multi-agent LLM trading research framework. This documentation set is geared toward engineers and researchers who need to understand, extend, or operate the system. It complements the project `README.md` by focusing on architecture and design rationale rather than user-facing instructions.

## Audience and Scope
- **Core maintainers** who evolve the agent graph or add features.
- **Research engineers** integrating new data sources, LLMs, or debate strategies.
- **Ops / platform engineers** who deploy the CLI or automate experiments.

## How to Use These Docs
1. Start with the [System Design](./system-design.md) for an end-to-end view of the architecture, flows, and constraints.
2. Drill into component guides under `components/` for implementation detail, responsibilities, and extension tips.
3. Refer back to code using the file references in each section when you need concrete implementation details.

## Document Map
- [System Design](./system-design.md)
- Component Guides
  - [Analyst Team](./components/analyst-team.md)
  - [Research & Trading Pipeline](./components/research-and-trading.md)
  - [Risk Management and Governance](./components/risk-management.md)
  - [Data Platform & Tooling](./components/data-platform.md)
  - [Runtime, CLI, and Configuration](./components/runtime-and-cli.md)

Future additions such as runbooks or experiment playbooks should live alongside these guides to keep the `docs/` structure cohesive.
