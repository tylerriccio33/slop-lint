"""Minimal ANSI color helpers for terminal output, in the style of ruff/rustc."""

from __future__ import annotations

import os
import sys

_BOLD = "\033[1m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


def supports_color(stream=sys.stdout) -> bool:
    """Whether ``stream`` should receive ANSI color codes."""
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    return hasattr(stream, "isatty") and stream.isatty()


def _wrap(code: str, text: str, *, enabled: bool) -> str:
    return f"{code}{text}{_RESET}" if enabled else text


def bold(text: str, *, enabled: bool) -> str:
    return _wrap(_BOLD, text, enabled=enabled)


def red(text: str, *, enabled: bool) -> str:
    return _wrap(_RED, text, enabled=enabled)


def bold_red(text: str, *, enabled: bool) -> str:
    return _wrap(_BOLD + _RED, text, enabled=enabled)


def cyan(text: str, *, enabled: bool) -> str:
    return _wrap(_CYAN, text, enabled=enabled)


def yellow(text: str, *, enabled: bool) -> str:
    return _wrap(_YELLOW, text, enabled=enabled)
