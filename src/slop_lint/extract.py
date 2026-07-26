"""Extract docstrings and comments from Python source, with source locations."""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TextBlock:
    """A piece of prose pulled out of source code: a docstring or a comment."""

    text: str
    kind: str  # "module-docstring" | "class-docstring" | "function-docstring" | "comment"
    line: int
    col: int


def extract_docstrings(source: str) -> list[TextBlock]:
    tree = ast.parse(source)
    blocks: list[TextBlock] = []

    module_doc = ast.get_docstring(tree, clean=True)
    if module_doc:
        node = tree.body[0]
        blocks.append(TextBlock(module_doc, "module-docstring", node.lineno, node.col_offset))

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        doc = ast.get_docstring(node, clean=True)
        if not doc:
            continue
        kind = "class-docstring" if isinstance(node, ast.ClassDef) else "function-docstring"
        doc_node = node.body[0]
        blocks.append(TextBlock(doc, kind, doc_node.lineno, doc_node.col_offset))

    return blocks


def extract_comments(source: str) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for tok in tokens:
        if tok.type != tokenize.COMMENT:
            continue
        text = tok.string.lstrip("#").strip()
        if not text:
            continue
        line, col = tok.start
        blocks.append(TextBlock(text, "comment", line, col))
    return blocks


def extract_text_blocks(source: str) -> list[TextBlock]:
    """Return every docstring and comment in ``source``, sorted by position."""
    blocks = extract_docstrings(source) + extract_comments(source)
    return sorted(blocks, key=lambda b: (b.line, b.col))


_RUST_BLOCK_COMMENT_RE = re.compile(r"/\*(.*?)\*/", re.DOTALL)
_RUST_LINE_COMMENT_RE = re.compile(r"//[!/]?(.*)$")


def _offset_to_linecol(source: str, offset: int) -> tuple[int, int]:
    prefix = source[:offset]
    line = prefix.count("\n") + 1
    col = offset - prefix.rfind("\n") - 1
    return line, col


def extract_rust_comments(source: str) -> list[TextBlock]:
    """Extract ``//``, ``///``, ``//!`` line comments and ``/* */`` block comments."""
    blocks: list[TextBlock] = []
    for match in _RUST_BLOCK_COMMENT_RE.finditer(source):
        text = match.group(1).strip()
        if text:
            line, col = _offset_to_linecol(source, match.start(1))
            blocks.append(TextBlock(text, "comment", line, col))

    # Blank out block comments (preserving newlines) so line-comment scanning
    # doesn't pick up a `//` that lives inside one.
    stripped = _RUST_BLOCK_COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), source)
    for lineno, line in enumerate(stripped.splitlines(), start=1):
        match = _RUST_LINE_COMMENT_RE.search(line)
        if not match:
            continue
        text = match.group(1).strip()
        if not text:
            continue
        blocks.append(TextBlock(text, "comment", lineno, match.start()))

    return sorted(blocks, key=lambda b: (b.line, b.col))


_MAKEFILE_COMMENT_RE = re.compile(r"(?<!\\)#(.*)$")


def extract_makefile_comments(source: str) -> list[TextBlock]:
    """Extract ``#`` comments from a Makefile."""
    blocks: list[TextBlock] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        match = _MAKEFILE_COMMENT_RE.search(line)
        if not match:
            continue
        text = match.group(1).strip()
        if not text:
            continue
        blocks.append(TextBlock(text, "comment", lineno, match.start()))
    return blocks


def _extract_paragraphs(source: str, kind: str, *, skip_code_fences: bool) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    paragraph: list[str] = []
    start_line = 1
    in_code_fence = False

    def flush() -> None:
        if not paragraph:
            return
        text = "\n".join(paragraph).strip()
        if text:
            blocks.append(TextBlock(text, kind, start_line, 0))
        paragraph.clear()

    for lineno, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if skip_code_fences and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_code_fence = not in_code_fence
            flush()
            start_line = lineno + 1
            continue
        if in_code_fence:
            continue
        if not stripped:
            flush()
            start_line = lineno + 1
            continue
        if not paragraph:
            start_line = lineno
        paragraph.append(line)
    flush()
    return blocks


def extract_markdown_blocks(source: str) -> list[TextBlock]:
    """Extract prose paragraphs from Markdown, skipping fenced code blocks."""
    return _extract_paragraphs(source, "markdown", skip_code_fences=True)


def extract_plain_text_blocks(source: str) -> list[TextBlock]:
    """Extract prose paragraphs from a plain text file."""
    return _extract_paragraphs(source, "text", skip_code_fences=False)


_MAKEFILE_NAMES = frozenset({"Makefile", "makefile", "GNUmakefile"})


def extract_text_blocks_for_file(path: Path, source: str) -> list[TextBlock]:
    """Extract text blocks based on ``path``'s file type."""
    suffix = path.suffix.lower()
    if suffix == ".py":
        return extract_text_blocks(source)
    if suffix == ".rs":
        return extract_rust_comments(source)
    if suffix == ".md":
        return extract_markdown_blocks(source)
    if suffix == ".txt":
        return extract_plain_text_blocks(source)
    if suffix == ".mk" or path.name in _MAKEFILE_NAMES:
        return extract_makefile_comments(source)
    return []


SUPPORTED_SUFFIXES = frozenset({".py", ".rs", ".md", ".txt", ".mk"})


def is_supported_file(path: Path) -> bool:
    """Whether ``path`` is a file type slop-lint knows how to extract text from."""
    return path.suffix.lower() in SUPPORTED_SUFFIXES or path.name in _MAKEFILE_NAMES
