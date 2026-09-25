"""Remove every docstring and comment from Python source (the ``--fix`` for ``strict``)."""

from __future__ import annotations

import ast
import io
import tokenize

from slop_lint.pragma import is_pragma

_Edit = tuple[int, int, int, int, str]


def _docstring_edits(tree: ast.Module) -> list[_Edit]:
    edits: list[_Edit] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if ast.get_docstring(node, clean=False) is None:
            continue
        doc = node.body[0]
        needs_body = len(node.body) == 1 and not isinstance(node, ast.Module)
        end_line = doc.end_lineno or doc.lineno
        end_col = doc.end_col_offset if doc.end_col_offset is not None else doc.col_offset
        edits.append((doc.lineno, doc.col_offset, end_line, end_col, "pass" if needs_body else ""))
    return edits


def _comment_edits(source: str) -> list[_Edit]:
    edits: list[_Edit] = []
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type != tokenize.COMMENT or is_pragma(tok.string.lstrip("#").strip()):
            continue
        (line, col), (end_line, end_col) = tok.start, tok.end
        edits.append((line, col, end_line, end_col, ""))
    return edits


def _char_col(line: str, byte_col: int) -> int:
    return len(line.encode("utf-8")[:byte_col].decode("utf-8", errors="ignore"))


def strip_prose(source: str) -> str:
    """Return ``source`` without docstrings or comments; tool pragmas stay."""
    # A bare string after a docstring then becomes the docstring, so repeat until stable.
    while (stripped := _strip_once(source)) != source:
        source = stripped
    return source


def _strip_once(source: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    doc_edits = [
        (sl, _char_col(lines[sl - 1], sc), el, _char_col(lines[el - 1], ec), r)
        for sl, sc, el, ec, r in _docstring_edits(tree)
    ]
    edits = sorted(doc_edits + _comment_edits(source), reverse=True)
    if not edits:
        return source

    touched: set[int] = set()
    for start_line, start_col, end_line, end_col, replacement in edits:
        head = lines[start_line - 1][:start_col]
        tail = lines[end_line - 1][end_col:]
        # Keep the line count, so later edits (earlier in the file) keep their positions.
        lines[start_line - 1] = head + replacement + tail
        for i in range(start_line, end_line):
            lines[i] = ""
        touched.update(range(start_line - 1, end_line))

    out: list[str] = []
    for i, line in enumerate(lines):
        if i not in touched:
            out.append(line)
            continue
        body = line.rstrip()
        if body:
            out.append(body + ("\n" if line.endswith("\n") else ""))
    result = "".join(out)
    ast.parse(result)
    return result
