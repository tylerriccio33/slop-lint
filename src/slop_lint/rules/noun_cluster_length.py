"""ASD-STE100 forbids multi-word noun clusters longer than three words.

Long noun strings (e.g. "fuel pump drive shaft gear housing assembly") are
hard to parse; the standard caps them at three words. This heuristic ends a
noun cluster at the first function word: an article, preposition,
conjunction, pronoun, or common verb.
"""

from __future__ import annotations

import re

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding
from slop_lint.rules.position import resolve_position
from slop_lint.sentences import split_sentences

name = "noun-cluster-length"

_FUNCTION_WORDS = frozenset(
    """
    a an the this that these those
    and or but nor so yet
    of to in on at by for with from into onto over under above below
    between among through during before after since until
    is are was were be been being am
    do does did have has had
    will would shall should can could may might must
    not no
    i you he she it we they
    his her its their our your my
    as if than then
    """.split()  # noqa: SIM905
)

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*|[,;:]")


def check(block: TextBlock, config: Config) -> list[Finding]:
    findings: list[Finding] = []
    max_length = config.max_noun_cluster_length
    for sentence in split_sentences(block.text):
        run: list[re.Match[str]] = []
        for match in [*_TOKEN_RE.finditer(sentence.text), None]:
            is_word = match is not None and match.group(0)[0].isalpha()
            is_break = match is None or not is_word or match.group(0).lower() in _FUNCTION_WORDS
            if is_break:
                if len(run) > max_length:
                    findings.append(_make_finding(block, sentence.offset, run, max_length))
                run = []
            else:
                run.append(match)
    return findings


def _make_finding(
    block: TextBlock,
    sentence_offset: int,
    run: list[re.Match[str]],
    max_length: int,
) -> Finding:
    cluster = " ".join(match.group(0) for match in run)
    line, col = resolve_position(block, sentence_offset + run[0].start())
    return Finding(
        rule=name,
        message=(f'noun cluster has {len(run)} words (max {max_length}): "{cluster}"'),
        line=line,
        col=col,
    )
