from pathlib import Path

import pytest

from ste100_lint.cli import main

PYPROJECT = """
[tool.ste100-lint]
enable = ["banned-words"]
banned-words = ["new", "old"]
"""


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "pyproject.toml").write_text(PYPROJECT)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_main_returns_1_and_prints_findings(project: Path, capsys: pytest.CaptureFixture):
    target = project / "mod.py"
    target.write_text('"""This uses the new API."""\n')

    exit_code = main([str(target)])

    assert exit_code == 1
    out = capsys.readouterr().out
    assert "banned-words" in out
    assert "new" in out


def test_main_returns_0_when_clean(project: Path):
    target = project / "mod.py"
    target.write_text('"""This is fine."""\n')

    assert main([str(target)]) == 0


def test_main_skips_non_python_files(project: Path):
    target = project / "notes.txt"
    target.write_text("new old")

    assert main([str(target)]) == 0
