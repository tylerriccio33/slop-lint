"""ASD-STE100 caps instructional/descriptive sentences at ~20 words for readability."""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding
from slop_lint.rules.position import resolve_position
from slop_lint.sentences import split_sentences

name = "max-sentence-length"


def check(block: TextBlock, config: Config) -> list[Finding]:
    findings: list[Finding] = []
    for sentence in split_sentences(block.text):
        word_count = len(sentence.text.split())
        if word_count <= config.max_sentence_length:
            continue
        line, col = resolve_position(block, sentence.offset)
        findings.append(
            Finding(
                rule=name,
                message=(
                    f"sentence has {word_count} words "
                    f"(max {config.max_sentence_length}): "
                    f'"{sentence.text}"'
                ),
                line=line,
                col=col,
            )
        )
    return findings
