"""ASD-STE100 gives each dictionary word one part of speech and one meaning.

The Dictionary approves the verb "close" (move together) but not the
adjective "close" (near). This needs sense-level matching, not plain
word matching. Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "approved-word-sense"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
