"""Tool directives that look like comments but are not prose."""

from __future__ import annotations

import re

_PRAGMA_RE = re.compile(
    r"^(!|\s*(-\*-|(vim?|ex):|noqa|type:|pragma:|fmt:|isort:|pyright:|pyrefly:|mypy:|ruff:"
    r"|pylint:|slop-lint:))"
)


def is_pragma(comment: str) -> bool:
    """Whether ``comment`` (the text after ``#``) is a tool directive."""
    return bool(_PRAGMA_RE.match(comment))
