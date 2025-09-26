import os


def _env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 3,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
    # External API gateway defaults
    "gateway_default_timeout": 30.0,
    "gateway_max_retries": 2,
    "gateway_retry_backoff_seconds": 0.0,
    # Feature flags
    "use_data_bootstrapper": _env_flag("USE_DATA_BOOTSTRAPPER"),
    "use_new_runtime": _env_flag("USE_NEW_RUNTIME"),
}
