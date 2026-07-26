"""Minimal sentence splitting shared by prose rules."""

from __future__ import annotations

import re
from dataclasses import dataclass

_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True, slots=True)
class Sentence:
    text: str
    offset: int  # character offset of the sentence's start within the source text


def split_sentences(text: str) -> list[Sentence]:
    sentences: list[Sentence] = []
    start = 0
    for match in _SENTENCE_END_RE.finditer(text):
        chunk, chunk_start = text[start : match.start()], start
        stripped = chunk.strip()
        if stripped:
            sentences.append(Sentence(stripped, chunk_start + chunk.find(stripped)))
        start = match.end()
    chunk, chunk_start = text[start:], start
    stripped = chunk.strip()
    if stripped:
        sentences.append(Sentence(stripped, chunk_start + chunk.find(stripped)))
    return sentences
