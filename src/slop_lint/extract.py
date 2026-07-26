"""Extract docstrings and comments from Python source, with source locations."""

from __future__ import annotations

import ast
import io
import tokenize
from dataclasses import dataclass


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
