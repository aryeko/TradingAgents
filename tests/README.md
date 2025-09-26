# TradingAgents Test Suite

This directory contains the test suite for TradingAgents, including end-to-end (e2e) tests that validate both the legacy v1 and modern v2 architectures.

## Test Structure

### E2E Tests (`tests/e2e/`)

The e2e tests are designed to run on both v1 and v2 architectures using pytest's parametrized fixtures. **Each test automatically runs twice - once for each version** when you run `pytest`.

#### Key Features:

- **Dual Version Support**: All e2e tests run on both v1 and v2 architectures
- **Mocked External Dependencies**: Tests use mocked LLMs, memory, and external services for deterministic results
- **Version-Specific Validation**: Tests can validate architecture-specific behavior
- **Clear Test Output**: Tests display which version is being tested

#### Test Markers:

- `@pytest.mark.e2e`: End-to-end tests exercising the TradingAgents runtime

## Running Tests

### Using pytest directly

```bash
# Run all e2e tests (both versions automatically)
python -m pytest -m e2e -v

# Run specific test for both versions
python -m pytest tests/e2e/test_graph_flow.py::test_trading_graph_propagate_returns_buy_signal -v

# Run tests for v1 only
python -m pytest -m e2e -k "[v1]" -v

# Run tests for v2 only
python -m pytest -m e2e -k "[v2]" -v
```

## Test Configuration

### pytest.ini

The pytest configuration includes markers for organizing tests:

```ini
[pytest]
markers =
    e2e: End-to-end tests exercising the TradingAgents runtime with mocked external services.
```

### conftest.py

The test configuration includes:

- **Mocked Runtime**: All external dependencies are mocked for deterministic testing
- **Parametrized Tests**: Each test uses `@pytest.mark.parametrize("version", ["v1", "v2"])` to run for both versions
- **Version Parameter**: Tests receive the version as a direct parameter

## Writing New Tests

When writing new e2e tests:

1. **Add the e2e marker and parametrize for versions**:
   ```python
   @pytest.mark.e2e
   @pytest.mark.parametrize("version", ["v1", "v2"])
   def test_my_feature(ta_graph, version):
   ```

2. **Add version-specific validation if needed**:
   ```python
   if version == "v1":
       # v1 specific assertions
       assert "legacy_field" in result
   elif version == "v2":
       # v2 specific assertions
       assert "modern_field" in result
   ```

3. **Use the ta_graph fixture with version parameter**:
   ```python
   graph = ta_graph(version=version, selected_analysts=["market"], debug=False)
   final_state, decision = graph.propagate("AAPL", "2024-06-30")
   ```

## Test Coverage

The e2e tests cover:

- **Basic Graph Propagation**: Core trading decision flow
- **Multiple LLM Providers**: OpenAI, Anthropic, Google, Ollama, OpenRouter
- **Analyst Combinations**: Different combinations of market, news, social, and fundamentals analysts
- **Online/Offline Tools**: Both online and offline data fetching modes
- **Debug Mode**: Streaming output in debug mode
- **Version-Specific Features**: Architecture-specific functionality validation

## Quick Start

Simply run:
```bash
python -m pytest -m e2e -v
```

This will automatically run all tests for both v1 and v2 architectures. Each test function will appear twice in the output - once for each version.

## Mocking Strategy

Tests use comprehensive mocking to ensure deterministic results:

- **LLMs**: All language models return predictable responses
- **Memory**: Financial situation memory returns canned responses
- **External Services**: All external API calls are mocked
- **Graph Execution**: The actual graph execution is replaced with a fake implementation that returns realistic state

This ensures tests are fast, reliable, and don't depend on external services or API keys.
