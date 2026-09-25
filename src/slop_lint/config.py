"""Load slop-lint configuration from ``[tool.slop-lint]`` in pyproject.toml."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, replace
from fnmatch import fnmatch
from functools import cache
from importlib import resources
from pathlib import Path

DEFAULT_ENABLED_RULES = ("banned-words", "max-sentence-length", "passive-voice")
DEFAULT_MAX_SENTENCE_LENGTH = 20
DEFAULT_MAX_NOUN_CLUSTER_LENGTH = 3
PRESETS = ("strict",)


@cache
def default_banned_words() -> frozenset[str]:
    text = (
        resources.files("slop_lint.data").joinpath("banned_words.txt").read_text(encoding="utf-8")
    )
    return frozenset(line.strip().lower() for line in text.splitlines() if line.strip())


@dataclass(frozen=True, slots=True)
class Config:
    enabled_rules: tuple[str, ...] = DEFAULT_ENABLED_RULES
    banned_words: frozenset[str] = field(default_factory=default_banned_words)
    max_sentence_length: int = DEFAULT_MAX_SENTENCE_LENGTH
    max_noun_cluster_length: int = DEFAULT_MAX_NOUN_CLUSTER_LENGTH
    loc_per_prose_line: int | None = None
    exclude: tuple[str, ...] = ()
    root: Path | None = None

    def is_excluded(self, path: Path) -> bool:
        """Whether ``path`` matches an ``exclude`` glob, relative to the pyproject folder."""
        if not self.exclude:
            return False
        resolved = path.resolve()
        base = (self.root or Path.cwd()).resolve()
        rel = resolved.relative_to(base) if resolved.is_relative_to(base) else resolved
        target = rel.as_posix()
        return any(
            fnmatch(target, pattern) or fnmatch(target, pattern.removeprefix("**/"))
            for pattern in self.exclude
        )

    def with_preset(self, preset: str | None) -> Config:
        if preset is None:
            return self
        if preset not in PRESETS:
            raise ValueError(f"unknown preset {preset!r}; choose from {', '.join(PRESETS)}")
        return replace(self, enabled_rules=(*self.enabled_rules, "no-prose"))

    def with_budget(self, loc_per_prose_line: int | None) -> Config:
        if loc_per_prose_line is None:
            return self
        return replace(self, loc_per_prose_line=loc_per_prose_line)

    @classmethod
    def from_dict(cls, data: dict) -> Config:
        section = data.get("tool", {}).get("slop-lint", {})
        extra_words = frozenset(w.lower() for w in section.get("banned-words", []))
        budget = section.get("budget", {})
        config = cls(
            enabled_rules=tuple(section.get("enable", DEFAULT_ENABLED_RULES)),
            exclude=tuple(section.get("exclude", ())),
            banned_words=default_banned_words() | extra_words,
            max_sentence_length=int(
                section.get("max-sentence-length", DEFAULT_MAX_SENTENCE_LENGTH)
            ),
            max_noun_cluster_length=int(
                section.get("max-noun-cluster-length", DEFAULT_MAX_NOUN_CLUSTER_LENGTH)
            ),
        )
        loc = budget.get("loc-per-prose-line")
        return config.with_preset(section.get("preset")).with_budget(
            None if loc is None else int(loc)
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
    return replace(Config.from_dict(data), root=path.parent)
