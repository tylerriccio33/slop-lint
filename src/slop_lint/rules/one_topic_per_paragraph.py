"""ASD-STE100 requires each paragraph to cover only one topic.

A paragraph that drifts between unrelated subjects (e.g. mixing an
unrelated observation into a procedure) violates single-topic structure.
Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "one-topic-per-paragraph"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
