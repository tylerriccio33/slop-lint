"""ASD-STE100 permits only the abbreviations listed in the Dictionary.

Ad hoc abbreviations (e.g. "Rmv" for "Remove", "asap" for "as soon as
possible") that are not on the approved list are not allowed. Not yet
implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "approved-abbreviations"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
