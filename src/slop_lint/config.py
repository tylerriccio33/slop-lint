"""Load slop-lint configuration from ``[tool.slop-lint]`` in pyproject.toml."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_ENABLED_RULES = ("banned-words", "max-sentence-length", "passive-voice")
DEFAULT_MAX_SENTENCE_LENGTH = 20


@dataclass(frozen=True, slots=True)
class Config:
    enabled_rules: tuple[str, ...] = DEFAULT_ENABLED_RULES
    banned_words: frozenset[str] = field(default_factory=frozenset)
    max_sentence_length: int = DEFAULT_MAX_SENTENCE_LENGTH

    @classmethod
    def from_dict(cls, data: dict) -> Config:
        section = data.get("tool", {}).get("slop-lint", {})
        return cls(
            enabled_rules=tuple(section.get("enable", DEFAULT_ENABLED_RULES)),
            banned_words=frozenset(w.lower() for w in section.get("banned-words", [])),
            max_sentence_length=int(
                section.get("max-sentence-length", DEFAULT_MAX_SENTENCE_LENGTH)
            ),
        )


def find_pyproject(start: Path) -> Path | None:
    for directory in [start, *start.parents]:
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def load_config(start: Path | None = None) -> Config:
    path = find_pyproject(start or Path.cwd())
    if path is None:
        return Config()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return Config.from_dict(data)
