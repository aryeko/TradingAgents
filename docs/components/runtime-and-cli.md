# Runtime, CLI, and Configuration

TradingAgents can run interactively through the CLI or programmatically via the Python API, both backed by the same orchestration code.

## Python API
Typical usage (`main.py`, `README.md`):
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
final_state, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)  # BUY / SELL / HOLD
```

- `debug=True` triggers graph streaming so intermediate messages are printed.
- `propagate()` returns both the final `AgentState` and the normalized decision from `SignalProcessor`.
- Execution directories (`dataflows/data_cache`, `results/`) are created automatically according to `config`.

## CLI Experience
`cli/main.py` implements a Typer command that launches a Rich-based dashboard. The CLI orchestrates:
- Parameter collection (tickers, dates, model selection) via interactive prompts.
- Live progress updates using `MessageBuffer` to track agent statuses, tool calls, and partial reports.
- Final report rendering, consolidating all analyst outputs and decisions into a Markdown summary.

To run locally:
```bash
python -m cli.main
```
Choose the desired options and monitor agent activity in real time.

## Configuration Surface
`DEFAULT_CONFIG` (`tradingagents/default_config.py`) exposes:
- Paths: `project_dir`, `results_dir`, `data_dir`, `data_cache_dir`.
- LLM provider settings: `llm_provider`, `deep_think_llm`, `quick_think_llm`, `backend_url`.
- Debate and recursion controls: `max_debate_rounds`, `max_risk_discuss_rounds`, `max_recur_limit`.
- Tooling: `online_tools` toggle.

Client code can copy the dict, mutate values, and pass it into `TradingAgentsGraph`. During initialization, `set_config()` propagates the values into the `dataflows` subsystem.

## Logging and Results
`TradingAgentsGraph` stores per-run snapshots in `log_states_dict`, keyed by trade date. Invoking `TradingAgentsGraph._log_state()` serializes analyst reports, debate histories, and final decisions into `results/` for post-run inspection.

The CLI also caches the final Markdown report in memory; future enhancements can persist these artifacts alongside the JSON logs.

## Deployment Notes
- The framework assumes OpenAI-compatible endpoints; alternate providers (Anthropic, Google) require the corresponding LangChain client to be configured in the config.
- For reproducible research, pin `requirements.txt` or `uv.lock` and disable online tools so all data comes from deterministic caches.
- Memory stores rely on an in-memory Chroma client. To share experiences across processes, instantiate `chromadb.PersistentClient` in `FinancialSituationMemory`.
