"""Runtime configuration, read from environment variables."""

import logging
import os


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer, got {raw!r}") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero, got {value}")
    return value


MAX_HTML_CHARS: int = _int_env("MAX_HTML_CHARS", 200_000)
LOG_LEVEL: int = logging.getLevelNamesMapping().get(
    os.getenv("LOG_LEVEL", "INFO").strip().upper(), logging.INFO
)
