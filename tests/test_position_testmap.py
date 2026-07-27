"""testmap-tagged unit/property/perf tests for slop_lint.rules.position."""

from __future__ import annotations

import time

from hypothesis import given
from hypothesis import strategies as st
from pytest_testmap import testmap

from slop_lint.extract import TextBlock
from slop_lint.rules.position import resolve_position


def make_block(text: str, line: int = 10, col: int = 4) -> TextBlock:
    return TextBlock(text=text, kind="comment", line=line, col=col)


@testmap(feature="resolve_position", kind="unit")
def test_resolve_position_unit():
    block = make_block("hello world", line=10, col=4)
    assert resolve_position(block, 0) == (10, 4)
    assert resolve_position(block, 6) == (10, 10)


@testmap(feature="resolve_position", kind="unit")
def test_resolve_position_across_newline():
    block = make_block("Line one.\nAn old idea.", line=10, col=4)
    line, col = resolve_position(block, block.text.index("old"))
    assert line == 11
    assert col == block.text.index("old") - block.text.index("\n") - 1


@testmap(feature="resolve_position", kind="property")
@given(st.integers(min_value=1, max_value=100), st.integers(min_value=0, max_value=50))
def test_resolve_position_offset_zero_is_block_start(line: int, col: int):
    block = make_block("some text here", line=line, col=col)
    assert resolve_position(block, 0) == (line, col)


@testmap(feature="resolve_position", kind="perf")
def test_resolve_position_perf():
    block = make_block("word " * 5000, line=1, col=0)
    start = time.perf_counter()
    resolve_position(block, len(block.text) - 1)
    assert time.perf_counter() - start < 1.0
