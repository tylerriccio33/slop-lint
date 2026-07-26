from pathlib import Path

from slop_lint.config import Config, load_config

PYPROJECT = """
[tool.slop-lint]
enable = ["banned-words"]
banned-words = ["new", "old"]
max-sentence-length = 15
"""


def test_from_dict_parses_section():
    import tomllib

    config = Config.from_dict(tomllib.loads(PYPROJECT))
    assert config.enabled_rules == ("banned-words",)
    assert config.banned_words == frozenset({"new", "old"})
    assert config.max_sentence_length == 15


def test_load_config_reads_nearest_pyproject(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(PYPROJECT)
    nested = tmp_path / "pkg" / "sub"
    nested.mkdir(parents=True)
    config = load_config(nested)
    assert config.banned_words == frozenset({"new", "old"})


def test_load_config_falls_back_to_defaults(tmp_path: Path):
    config = load_config(tmp_path)
    assert config.banned_words == frozenset()
    assert config.enabled_rules == ("banned-words", "max-sentence-length", "passive-voice")
