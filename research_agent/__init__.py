"""Investment Research Agent using Claude Agent SDK."""

# Lazy imports to avoid circular import warning when running as __main__
__all__ = ["run_conversation", "run_single_query", "SYSTEM_PROMPT"]


def __getattr__(name: str):
    if name in __all__:
        from . import agent
        return getattr(agent, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
