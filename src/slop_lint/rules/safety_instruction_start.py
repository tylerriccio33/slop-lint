"""ASD-STE100 requires safety instructions to open with a command or condition.

Write the command or the condition first. Do not phrase a safety
instruction as an indirect statement (e.g. "It is necessary to
disconnect the power before you remove the panel."). Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "safety-instruction-start"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
