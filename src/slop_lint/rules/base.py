"""Rule protocol and finding type shared by all checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from slop_lint.config import Config
from slop_lint.extract import TextBlock


@dataclass(frozen=True, slots=True)
class Finding:
    """A single rule violation, anchored to a source location."""

    rule: str
    message: str
    line: int
    col: int


class Rule(Protocol):
    """A check that inspects one text block and yields findings."""

    name: str

    def check(self, block: TextBlock, config: Config) -> list[Finding]: ...
