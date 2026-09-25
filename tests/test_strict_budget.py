import ast
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from slop_lint.budget import check_budget
from slop_lint.cli import main
from slop_lint.config import Config
from slop_lint.linter import lint_source
from slop_lint.strip import strip_prose

SOURCE = '''#!/usr/bin/env python
"""Module doc
spanning lines."""
import os  # noqa: F401
# a comment


class A:
    """Only a docstring."""


def f(x):  # trailing
    """Doc."""
    # explain
    y = x + 1  # inline
    return "# not a comment"
'''

STRIPPED = """#!/usr/bin/env python
import os  # noqa: F401


class A:
    pass


def f(x):
    y = x + 1
    return "# not a comment"
"""


def test_strict_preset_flags_every_docstring_and_comment():
    config = Config(enabled_rules=()).with_preset("strict")
    findings = lint_source(SOURCE, config)
    assert {f.line for f in findings} == {2, 5, 9, 12, 13, 14, 15}
    assert all(f.rule == "no-prose" for f in findings)


def test_unknown_preset_raises():
    with pytest.raises(ValueError, match="unknown preset"):
        Config().with_preset("lax")


def test_preset_and_budget_load_from_pyproject():
    config = Config.from_dict(
        {"tool": {"slop-lint": {"preset": "strict", "budget": {"loc-per-prose-line": 7}}}}
    )
    assert "no-prose" in config.enabled_rules
    assert config.loc_per_prose_line == 7


def test_budget_flags_scopes_over_budget():
    findings = check_budget(SOURCE, 5)
    assert [f.message.split("'")[1] for f in findings] == ["<module>", "A", "f"]


def test_budget_passes_with_enough_code():
    source = "def f(x):\n    # one note\n" + "    x += 1\n" * 10 + "    return x\n"
    assert check_budget(source, 5) == []


def test_budget_ignores_pragmas():
    source = "import os  # noqa: F401\nimport sys  # type: ignore\n"
    assert check_budget(source, 5) == []


def test_strip_prose_removes_docstrings_and_comments():
    assert strip_prose(SOURCE) == STRIPPED


def test_strip_prose_keeps_one_line_def_valid():
    result = strip_prose('def g(): """one-liner"""\n')
    assert result == "def g(): pass\n"
    ast.parse(result)


def test_strip_prose_is_noop_without_prose():
    assert strip_prose("x = 1\n") == "x = 1\n"


def test_cli_fix_rewrites_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "mod.py"
    target.write_text(SOURCE)
    assert main(["--fix", str(target)]) == 0
    assert target.read_text() == STRIPPED
    assert main(["--preset", "strict", str(target)]) == 0


def test_cli_budget_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "mod.py"
    target.write_text(SOURCE)
    assert main(["--budget", "5", str(target)]) == 1
    assert "prose-budget" in capsys.readouterr().out


def test_budget_gives_tied_comment_to_inner_scope():
    source = "def f():\n    # note\n    return 1\n"
    (finding,) = check_budget(source, 5)
    assert "'f' has 1 prose line(s) (0 docstring + 1 comment)" in finding.message


def test_budget_does_not_count_comment_lines_as_code():
    source = "def f():\n" + "    # note\n" * 5 + "    return 1\n"
    (finding,) = check_budget(source, 1)
    assert "for 2 LOC" in finding.message


def test_budget_counts_nested_comment_once_to_innermost():
    source = (
        "class A:\n"
        + "    x = 1\n" * 10
        + "    def m(self):\n"
        + "        # inner\n"
        + "        return 1\n"
    )
    findings = check_budget(source, 5)
    assert [f.message.split("'")[1] for f in findings] == ["m"]


def test_budget_scope_includes_decorators_and_async():
    source = "@dec\nasync def f():\n    return 1\n"
    assert check_budget(source, 1) == []


def test_budget_only_runs_on_python(tmp_path: Path):
    config = Config(enabled_rules=()).with_budget(1)
    assert lint_source("// a comment\nfn main() {}\n", config, path=tmp_path / "a.rs") == []


def test_strict_flags_rust_comments_but_not_markdown(tmp_path: Path):
    config = Config(enabled_rules=()).with_preset("strict")
    rust = lint_source("// hi\nfn main() {}\n", config, path=tmp_path / "a.rs")
    md = lint_source("Some prose.\n", config, path=tmp_path / "a.md")
    assert [f.rule for f in rust] == ["no-prose"]
    assert md == []


@pytest.mark.parametrize(
    "pragma",
    ["# noqa: E501", "# type: ignore", "# pragma: no cover", "# fmt: skip", "# slop-lint: ignore"],
)
def test_strict_and_fix_keep_pragmas(pragma: str):
    source = f"x = 1  {pragma}\n"
    config = Config(enabled_rules=()).with_preset("strict")
    assert lint_source(source, config) == []
    assert strip_prose(source) == source


def test_strip_prose_nested_and_async():
    source = (
        "class A:\n"
        '    """Doc."""\n'
        "\n"
        "    async def m(self):\n"
        '        """Doc."""\n'
        "        # note\n"
        "        return 1\n"
    )
    assert strip_prose(source) == "class A:\n\n    async def m(self):\n        return 1\n"


def test_strip_prose_keeps_non_docstring_strings():
    source = 'def f():\n    x = 1\n    """not a docstring"""\n    return x\n'
    assert strip_prose(source) == source


def test_strip_prose_module_with_only_docstring():
    assert strip_prose('"""Doc."""\n') == ""


def test_cli_fix_skips_unparseable_and_non_python(tmp_path: Path, capsys):
    bad = tmp_path / "bad.py"
    bad.write_text("def (:\n")
    rust = tmp_path / "a.rs"
    rust.write_text("// hi\n")
    assert main(["--fix", str(bad), str(rust)]) == 0
    assert bad.read_text() == "def (:\n"
    assert rust.read_text() == "// hi\n"
    assert "could not parse" in capsys.readouterr().err


_FRAGMENTS = [
    '"""Doc."""',
    "# note",
    "x = 1  # trailing",
    "y = '# not a comment'",
    "def f():\n    '''Doc.'''",
    "def g():\n    # only\n    return 1",
    "class C:\n    '''Doc.'''\n    z = 2  # z",
]


@given(st.lists(st.sampled_from(_FRAGMENTS), min_size=1, max_size=8))
def test_strip_prose_output_parses_and_has_no_prose(fragments: list[str]):
    result = strip_prose("\n".join(fragments) + "\n")
    ast.parse(result)
    assert lint_source(result, Config(enabled_rules=()).with_preset("strict")) == []
    assert strip_prose(result) == result


def test_strip_prose_removes_string_that_becomes_docstring():
    assert strip_prose('def f():\n    """a"""\n    """b"""\n') == "def f():\n    pass\n"
