"""Registry of available rules, keyed by name."""

from __future__ import annotations

from types import ModuleType

from slop_lint.rules import banned_words, max_sentence_length, passive_voice

REGISTRY: dict[str, ModuleType] = {
    banned_words.name: banned_words,
    max_sentence_length.name: max_sentence_length,
    passive_voice.name: passive_voice,
}
