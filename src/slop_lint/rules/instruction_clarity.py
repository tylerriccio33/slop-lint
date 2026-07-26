"""ASD-STE100 requires instructions to be as clear and specific as possible.

Vague instructions (e.g. "do the thing to the part as needed") force the
reader to guess the actor, action, or object. Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "instruction-clarity"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
