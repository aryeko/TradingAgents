# Observability

This guide outlines logging, metrics, and diagnostics for the modern runtime.

## Logging
- `NodeExecutor`: Emits start/stop events with duration, success, retry counts, and exceptions.
- `ExternalApiGateway`: Logs provider calls, latency, response size, and cost metadata (when available).
- Structured logging format: JSON lines with `session_id`, `node_id`, `provider`, `status` fields.

## Metrics
- Counters: node executions, provider invocations, failure reasons.
- Histograms: node duration, provider latency, retries.
- Gauges: active sessions, queued nodes.

## Tracing
- When available, propagate trace IDs via gateway adapters to correlate with external services.

## Debugging Tools
- Feature flag to enable verbose streaming for CLI runs.
- Context snapshot dumps on failure for post-mortem analysis.

## Related Documents
- [Master Plan](../implementation/master-plan.md)
- [Final Architecture](../new-architecture/final-architecture.md)
