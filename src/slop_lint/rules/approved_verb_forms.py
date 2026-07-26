"""ASD-STE100 allows only seven verb forms.

Approved forms: infinitive, imperative, simple present, simple past,
simple future, and the past participle used only as an adjective. Reject
other constructions, e.g. "will have finished". Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "approved-verb-forms"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
