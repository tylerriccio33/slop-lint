"""ASD-STE100 requires exactly one instruction per sentence.

Split chained instructions joined with "and"/"then" (e.g. "Remove the
panel and replace the seal and then install the cover.") into separate
sentences. Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "one-instruction-per-sentence"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
