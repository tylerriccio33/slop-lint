"""Lint Python docstrings and comments for ASD-STE100 style and banned words."""

from slop_lint.config import Config, load_config
from slop_lint.linter import lint_source
from slop_lint.rules.base import Finding

__all__ = ["Config", "Finding", "lint_source", "load_config"]
