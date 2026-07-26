from pathlib import Path

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

SOURCE = '''"""Module docstring."""


class Foo:
    """Class docstring."""

    def bar(self):
        """Function docstring."""
        # a comment
        return 1  # trailing comment
'''


def test_extract_docstrings_finds_module_class_and_function():
    blocks = extract_docstrings(SOURCE)
    kinds = {b.kind: b.text for b in blocks}
    assert kinds["module-docstring"] == "Module docstring."
    assert kinds["class-docstring"] == "Class docstring."
    assert kinds["function-docstring"] == "Function docstring."


def test_extract_comments_finds_standalone_and_trailing():
    blocks = extract_comments(SOURCE)
    texts = [b.text for b in blocks]
    assert "a comment" in texts
    assert "trailing comment" in texts
    assert all(b.kind == "comment" for b in blocks)


def test_extract_text_blocks_is_sorted_by_position():
    blocks = extract_text_blocks(SOURCE)
    lines = [b.line for b in blocks]
    assert lines == sorted(lines)


def test_no_docstring_yields_nothing():
    blocks = extract_docstrings("def foo():\n    return 1\n")
    assert blocks == []


RUST_SOURCE = """\
//! Module-level doc comment.

/// Adds two numbers.
fn add(a: i32, b: i32) -> i32 {
    // a line comment
    a + b // trailing comment
}

/* a block
   comment */
"""


def test_extract_rust_comments_finds_line_and_doc_comments():
    blocks = extract_rust_comments(RUST_SOURCE)
    texts = [b.text for b in blocks]
    assert "Module-level doc comment." in texts
    assert "Adds two numbers." in texts
    assert "a line comment" in texts
    assert "trailing comment" in texts


def test_extract_rust_comments_finds_block_comments():
    blocks = extract_rust_comments(RUST_SOURCE)
    texts = [b.text for b in blocks]
    assert any("a block" in t for t in texts)


MAKEFILE_SOURCE = """\
# Build the project
build:
\tgcc -o out main.c  # compile

.PHONY: build
"""


def test_extract_makefile_comments_finds_standalone_and_trailing():
    blocks = extract_makefile_comments(MAKEFILE_SOURCE)
    texts = [b.text for b in blocks]
    assert "Build the project" in texts
    assert "compile" in texts


MARKDOWN_SOURCE = """\
# Title

This is the new intro paragraph.

```python
# not prose
new_old = 1
```

Another paragraph here.
"""


def test_extract_markdown_blocks_skips_code_fences():
    blocks = extract_markdown_blocks(MARKDOWN_SOURCE)
    texts = "\n".join(b.text for b in blocks)
    assert "new intro paragraph" in texts
    assert "not prose" not in texts
    assert "Another paragraph here." in texts


def test_extract_plain_text_blocks_splits_paragraphs():
    blocks = extract_plain_text_blocks("First paragraph.\n\nSecond paragraph.\n")
    texts = [b.text for b in blocks]
    assert texts == ["First paragraph.", "Second paragraph."]


def test_extract_text_blocks_for_file_dispatches_by_suffix():
    assert extract_text_blocks_for_file(Path("mod.py"), '"""doc."""\n') != []
    assert extract_text_blocks_for_file(Path("lib.rs"), "// hi\n") != []
    assert extract_text_blocks_for_file(Path("README.md"), "hello world\n") != []
    assert extract_text_blocks_for_file(Path("notes.txt"), "hello world\n") != []
    assert extract_text_blocks_for_file(Path("Makefile"), "# hi\nbuild:\n") != []
    assert extract_text_blocks_for_file(Path("data.json"), "{}") == []


def test_is_supported_file():
    assert is_supported_file(Path("a.py"))
    assert is_supported_file(Path("a.rs"))
    assert is_supported_file(Path("a.md"))
    assert is_supported_file(Path("a.txt"))
    assert is_supported_file(Path("Makefile"))
    assert not is_supported_file(Path("a.json"))
