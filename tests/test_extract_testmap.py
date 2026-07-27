"""testmap-tagged unit/property/perf tests for slop_lint.extract."""

from __future__ import annotations

import contextlib
import time
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st
from pytest_testmap import testmap

from slop_lint.extract import (
    extract_comments,
    extract_docstrings,
    extract_makefile_comments,
    extract_markdown_blocks,
    extract_plain_text_blocks,
    extract_rust_comments,
    extract_text_blocks,
    extract_text_blocks_for_file,
    is_supported_file,
)

# -- extract_docstrings ------------------------------------------------------


@testmap(feature="extract_docstrings", kind="unit")
def test_extract_docstrings_unit():
    blocks = extract_docstrings('"""Module doc."""\n\n\ndef f():\n    """Func doc."""\n')
    kinds = {b.kind: b.text for b in blocks}
    assert kinds["module-docstring"] == "Module doc."
    assert kinds["function-docstring"] == "Func doc."


@testmap(feature="extract_docstrings", kind="property")
@given(st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200))
def test_extract_docstrings_never_raises_on_arbitrary_text(text: str):
    with contextlib.suppress(SyntaxError):
        extract_docstrings(text)


@testmap(feature="extract_docstrings", kind="perf")
def test_extract_docstrings_perf():
    source = '"""doc."""\n\n' + "\n".join(f"def f{i}():\n    '''d{i}'''\n" for i in range(500))
    start = time.perf_counter()
    extract_docstrings(source)
    assert time.perf_counter() - start < 1.0


# -- extract_comments ---------------------------------------------------------


@testmap(feature="extract_comments", kind="unit")
def test_extract_comments_unit():
    blocks = extract_comments("x = 1  # trailing\n# standalone\n")
    texts = [b.text for b in blocks]
    assert texts == ["trailing", "standalone"]


@testmap(feature="extract_comments", kind="property")
@given(st.integers(min_value=0, max_value=50))
def test_extract_comments_count_matches_hash_lines(n: int):
    source = "\n".join(f"x{i} = {i}  # c{i}" for i in range(n)) + "\n"
    blocks = extract_comments(source)
    assert len(blocks) == n


@testmap(feature="extract_comments", kind="perf")
def test_extract_comments_perf():
    source = "\n".join(f"x = {i}  # comment {i}" for i in range(2000)) + "\n"
    start = time.perf_counter()
    extract_comments(source)
    assert time.perf_counter() - start < 1.0


# -- extract_text_blocks --------------------------------------------------


@testmap(feature="extract_text_blocks", kind="unit")
def test_extract_text_blocks_unit():
    blocks = extract_text_blocks('"""doc."""\nx = 1  # note\n')
    assert {b.kind for b in blocks} == {"module-docstring", "comment"}


@testmap(feature="extract_text_blocks", kind="property")
@given(st.integers(min_value=0, max_value=30))
def test_extract_text_blocks_is_sorted(n: int):
    source = "\n".join(f"x{i} = {i}  # c{i}" for i in range(n)) + "\n"
    blocks = extract_text_blocks(source)
    lines = [b.line for b in blocks]
    assert lines == sorted(lines)


@testmap(feature="extract_text_blocks", kind="perf")
def test_extract_text_blocks_perf():
    source = '"""doc."""\n' + "\n".join(f"x{i} = {i}  # c{i}" for i in range(1000)) + "\n"
    start = time.perf_counter()
    extract_text_blocks(source)
    assert time.perf_counter() - start < 1.0


# -- extract_rust_comments -----------------------------------------------


@testmap(feature="extract_rust_comments", kind="unit")
def test_extract_rust_comments_unit():
    blocks = extract_rust_comments("// hi\n/* block */\nlet x = 1; // trailing\n")
    texts = [b.text for b in blocks]
    assert "hi" in texts
    assert "block" in texts
    assert "trailing" in texts


@testmap(feature="extract_rust_comments", kind="property")
@given(st.integers(min_value=0, max_value=50))
def test_extract_rust_comments_count_matches_line_count(n: int):
    source = "\n".join(f"let x{i} = {i}; // c{i}" for i in range(n)) + "\n"
    blocks = extract_rust_comments(source)
    assert len(blocks) == n


@testmap(feature="extract_rust_comments", kind="perf")
def test_extract_rust_comments_perf():
    source = "\n".join(f"let x{i} = {i}; // c{i}" for i in range(2000)) + "\n"
    start = time.perf_counter()
    extract_rust_comments(source)
    assert time.perf_counter() - start < 1.0


# -- extract_makefile_comments --------------------------------------------


@testmap(feature="extract_makefile_comments", kind="unit")
def test_extract_makefile_comments_unit():
    source = "# build the thing\nbuild:\n\tgcc -o out main.c  # compile\n"
    blocks = extract_makefile_comments(source)
    texts = [b.text for b in blocks]
    assert "build the thing" in texts
    assert "compile" in texts


@testmap(feature="extract_makefile_comments", kind="property")
@given(st.integers(min_value=0, max_value=50))
def test_extract_makefile_comments_count_matches_hash_lines(n: int):
    source = "\n".join(f"target{i}:  # c{i}" for i in range(n)) + "\n"
    blocks = extract_makefile_comments(source)
    assert len(blocks) == n


@testmap(feature="extract_makefile_comments", kind="perf")
def test_extract_makefile_comments_perf():
    source = "\n".join(f"target{i}:  # c{i}" for i in range(2000)) + "\n"
    start = time.perf_counter()
    extract_makefile_comments(source)
    assert time.perf_counter() - start < 1.0


# -- extract_markdown_blocks -----------------------------------------------


@testmap(feature="extract_markdown_blocks", kind="unit")
def test_extract_markdown_blocks_unit():
    blocks = extract_markdown_blocks("First para.\n\n```py\nnot prose\n```\n\nSecond para.\n")
    texts = "\n".join(b.text for b in blocks)
    assert "First para." in texts
    assert "Second para." in texts
    assert "not prose" not in texts


@testmap(feature="extract_markdown_blocks", kind="property")
@given(st.integers(min_value=0, max_value=20))
def test_extract_markdown_blocks_never_crosses_blank_lines(n: int):
    source = "\n\n".join(f"paragraph {i} text" for i in range(n)) + "\n"
    blocks = extract_markdown_blocks(source)
    assert len(blocks) == n


@testmap(feature="extract_markdown_blocks", kind="perf")
def test_extract_markdown_blocks_perf():
    source = "\n\n".join(f"paragraph {i} text" for i in range(1000)) + "\n"
    start = time.perf_counter()
    extract_markdown_blocks(source)
    assert time.perf_counter() - start < 1.0


# -- extract_plain_text_blocks ---------------------------------------------


@testmap(feature="extract_plain_text_blocks", kind="unit")
def test_extract_plain_text_blocks_unit():
    blocks = extract_plain_text_blocks("First paragraph.\n\nSecond paragraph.\n")
    assert [b.text for b in blocks] == ["First paragraph.", "Second paragraph."]


@testmap(feature="extract_plain_text_blocks", kind="property")
@given(st.integers(min_value=0, max_value=20))
def test_extract_plain_text_blocks_paragraph_count(n: int):
    source = "\n\n".join(f"paragraph {i} text" for i in range(n)) + "\n"
    blocks = extract_plain_text_blocks(source)
    assert len(blocks) == n


@testmap(feature="extract_plain_text_blocks", kind="perf")
def test_extract_plain_text_blocks_perf():
    source = "\n\n".join(f"paragraph {i} text" for i in range(1000)) + "\n"
    start = time.perf_counter()
    extract_plain_text_blocks(source)
    assert time.perf_counter() - start < 1.0


# -- extract_text_blocks_for_file ------------------------------------------


@testmap(feature="extract_text_blocks_for_file", kind="unit")
def test_extract_text_blocks_for_file_unit():
    assert extract_text_blocks_for_file(Path("mod.py"), '"""doc."""\n') != []
    assert extract_text_blocks_for_file(Path("data.json"), "{}") == []


@testmap(feature="extract_text_blocks_for_file", kind="property")
@given(st.sampled_from([".py", ".rs", ".md", ".txt", ".mk", ".json", ".yaml"]))
def test_extract_text_blocks_for_file_dispatch_matches_is_supported(suffix: str):
    path = Path(f"file{suffix}")
    blocks = extract_text_blocks_for_file(path, "")
    if not is_supported_file(path):
        assert blocks == []


@testmap(feature="extract_text_blocks_for_file", kind="perf")
def test_extract_text_blocks_for_file_perf():
    source = "\n".join(f"x{i} = {i}  # c{i}" for i in range(1000)) + "\n"
    start = time.perf_counter()
    extract_text_blocks_for_file(Path("mod.py"), source)
    assert time.perf_counter() - start < 1.0


# -- is_supported_file -------------------------------------------------------


@testmap(feature="is_supported_file", kind="unit")
def test_is_supported_file_unit():
    assert is_supported_file(Path("a.py"))
    assert not is_supported_file(Path("a.json"))


@testmap(feature="is_supported_file", kind="property")
@given(st.sampled_from([".py", ".rs", ".md", ".txt", ".mk"]))
def test_is_supported_file_true_for_every_known_suffix(suffix: str):
    assert is_supported_file(Path(f"file{suffix}"))


@testmap(feature="is_supported_file", kind="perf")
def test_is_supported_file_perf():
    start = time.perf_counter()
    for _ in range(10000):
        is_supported_file(Path("a.py"))
    assert time.perf_counter() - start < 1.0
