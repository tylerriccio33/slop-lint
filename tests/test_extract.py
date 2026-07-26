from ste100_lint.extract import extract_comments, extract_docstrings, extract_text_blocks

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
