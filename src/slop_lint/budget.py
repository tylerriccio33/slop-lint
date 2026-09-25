"""Budget prose per scope: each module, class, and def gets one prose line per N lines of code."""

from __future__ import annotations

import ast
import io
import tokenize
from dataclasses import dataclass

from slop_lint.pragma import is_pragma
from slop_lint.rules.base import Finding

name = "prose-budget"

Scope = ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(slots=True)
class Budget:
    """One scope's prose lines and the lines of code they document."""

    node: Scope
    start: int
    end: int
    docstring_lines: int = 0
    comment_lines: int = 0
    loc: int = 0

    @property
    def name(self) -> str:
        return getattr(self.node, "name", "<module>")

    @property
    def prose(self) -> int:
        return self.docstring_lines + self.comment_lines


def _comments(source: str) -> list[tuple[int, bool]]:
    """Each prose comment's line, and whether the comment has the whole line."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (SyntaxError, tokenize.TokenError):
        return []
    lines = source.splitlines()
    return [
        (t.start[0], not lines[t.start[0] - 1][: t.start[1]].strip())
        for t in tokens
        if t.type == tokenize.COMMENT and not is_pragma(t.string.lstrip("#").strip())
    ]


def _docstring_span(node: Scope) -> range:
    if ast.get_docstring(node, clean=False) is None:
        return range(0)
    expr = node.body[0]
    return range(expr.lineno, (expr.end_lineno or expr.lineno) + 1)


def budgets(source: str) -> list[Budget]:
    """A Budget per module, class, and def; a comment counts to its innermost scope."""
    tree = ast.parse(source)
    lines = source.splitlines()
    comments = _comments(source)
    scopes: list[Scope] = [tree]
    scopes += [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
    ]
    prose_lines = {line for line, whole in comments if whole}
    for node in scopes:
        prose_lines.update(_docstring_span(node))

    result: list[Budget] = []
    for node in scopes:
        if isinstance(node, ast.Module):
            start, end = 1, len(lines)
        else:
            start = min([node.lineno, *(d.lineno for d in node.decorator_list)])
            end = node.end_lineno or node.lineno
        loc = sum(1 for i in range(start, end + 1) if lines[i - 1].strip() and i not in prose_lines)
        result.append(Budget(node, start, end, len(_docstring_span(node)), loc=loc))

    for line, _ in comments:
        # Ties go to the later scope in walk order, which is the inner one.
        owner = min(
            (i for i, b in enumerate(result) if b.start <= line <= b.end),
            key=lambda i: (result[i].end - result[i].start, -i),
        )
        result[owner].comment_lines += 1
    return result


def check_budget(source: str, loc_per_prose_line: int) -> list[Finding]:
    """Flag every scope whose prose lines exceed ``loc // loc_per_prose_line``."""
    findings: list[Finding] = []
    for b in budgets(source):
        allowed = b.loc // loc_per_prose_line
        if b.prose <= allowed:
            continue
        findings.append(
            Finding(
                rule=name,
                message=(
                    f"'{b.name}' has {b.prose} prose line(s) ({b.docstring_lines} docstring + "
                    f"{b.comment_lines} comment) for {b.loc} LOC (allowed {allowed})"
                ),
                line=getattr(b.node, "lineno", 1),
                col=getattr(b.node, "col_offset", 0),
            )
        )
    return findings
