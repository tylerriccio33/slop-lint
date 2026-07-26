"""ASD-STE100 forbids multi-word noun clusters longer than three words.

Long noun strings (e.g. "fuel pump drive shaft gear housing assembly") are
hard to parse; the standard caps them at three words. Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "noun-cluster-length"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
