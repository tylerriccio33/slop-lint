from slop_lint.rules.base import Finding
from slop_lint.suppress import filter_suppressed, parse_suppressions


def test_parse_suppressions_bare_ignore():
    source = "x = 1  # slop-lint: ignore\ny = 2\n"
    assert parse_suppressions(source) == {1: None}


def test_parse_suppressions_scoped_ignore():
    source = "x = 1  # slop-lint: ignore[banned-words, passive-voice]\n"
    assert parse_suppressions(source) == {1: frozenset({"banned-words", "passive-voice"})}


def test_filter_suppressed_drops_bare_ignore_line():
    source = "# frobnicate this  # slop-lint: ignore\n"
    findings = [Finding(rule="banned-words", message="x", line=1, col=0)]
    assert filter_suppressed(findings, source) == []


def test_filter_suppressed_scoped_ignore_only_matches_named_rule():
    source = "# frobnicate this  # slop-lint: ignore[max-sentence-length]\n"
    findings = [Finding(rule="banned-words", message="x", line=1, col=0)]
    assert filter_suppressed(findings, source) == findings


def test_filter_suppressed_leaves_other_lines_alone():
    source = "# frobnicate this\n# something else  # slop-lint: ignore\n"
    findings = [
        Finding(rule="banned-words", message="x", line=1, col=0),
        Finding(rule="banned-words", message="y", line=2, col=0),
    ]
    assert filter_suppressed(findings, source) == [findings[0]]
