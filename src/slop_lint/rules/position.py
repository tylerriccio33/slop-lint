"""Map a character offset within a TextBlock's text back to a source (line, col)."""

from __future__ import annotations

from slop_lint.extract import TextBlock


def resolve_position(block: TextBlock, offset: int) -> tuple[int, int]:
    prefix = block.text[:offset]
    newlines = prefix.count("\n")
    line = block.line + newlines
    col = block.col + offset if newlines == 0 else offset - prefix.rfind("\n") - 1
    return line, col
