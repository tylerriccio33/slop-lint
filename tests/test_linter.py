from slop_lint.config import Config
from slop_lint.linter import lint_source

SOURCE = '''"""This is the new module."""


def foo():
    """Do the new thing."""
    # an old comment
    return 1
'''


def test_lint_source_runs_enabled_rules_only():
    config = Config(enabled_rules=("banned-words",), banned_words=frozenset({"new", "old"}))
    findings = lint_source(SOURCE, config)
    assert findings
    assert all(f.rule == "banned-words" for f in findings)


def test_lint_source_respects_disabled_rule_list():
    config = Config(enabled_rules=(), banned_words=frozenset({"new", "old"}))
    findings = lint_source(SOURCE, config)
    assert findings == []


def test_lint_source_findings_sorted_by_position():
    config = Config(enabled_rules=("banned-words",), banned_words=frozenset({"new", "old"}))
    findings = lint_source(SOURCE, config)
    positions = [(f.line, f.col) for f in findings]
    assert positions == sorted(positions)
