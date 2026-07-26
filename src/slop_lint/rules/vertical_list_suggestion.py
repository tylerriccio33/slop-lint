"""ASD-STE100 recommends vertical lists for complex text.

Use a vertical list instead of a long comma-separated run of items or
steps in one sentence (e.g. "Remove the bolt, washer, bracket, seal,
and cover, in that order."). Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "vertical-list-suggestion"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
