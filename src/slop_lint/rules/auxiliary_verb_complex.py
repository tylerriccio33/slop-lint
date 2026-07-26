"""ASD-STE100 disallows auxiliary verbs used to build complex verb constructions.

Modal/auxiliary chains (e.g. "should have finished checking") are not
approved verb forms. Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "auxiliary-verb-complex"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
