"""ASD-STE100 restricts '-ing' forms to technical nouns or modifiers.

Use the '-ing' form only as a noun or a modifier. Do not use it as a
continuous verb tense (e.g. "is recording", "is running"). Not yet
implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "ing-form-usage"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
