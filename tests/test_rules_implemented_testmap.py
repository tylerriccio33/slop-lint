"""testmap-tagged unit/property/perf tests for the implemented rule checks."""

from __future__ import annotations

import time

from hypothesis import given
from hypothesis import strategies as st
from pytest_testmap import testmap

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules import (
    auxiliary_verb_complex,
    banned_words,
    max_sentence_length,
    noun_cluster_length,
    passive_voice,
)

PERF_TEXT = "word " * 20000


def make_block(text: str, line: int = 1, col: int = 4) -> TextBlock:
    return TextBlock(text=text, kind="comment", line=line, col=col)


# -- banned-words -------------------------------------------------------------


@testmap(feature="rule-banned-words", kind="unit")
def test_banned_words_unit():
    config = Config(banned_words=frozenset({"new"}))
    findings = banned_words.check(make_block("Use the new widget."), config)
    assert [f.message for f in findings] == ['banned word "new"']


@testmap(feature="rule-banned-words", kind="property")
@given(st.sets(st.sampled_from(["alpha", "beta", "gamma"]), min_size=0, max_size=3))
def test_banned_words_finding_count_matches_occurrences(banned: set[str]):
    config = Config(banned_words=frozenset(banned))
    text = "alpha beta gamma delta"
    findings = banned_words.check(make_block(text), config)
    assert len(findings) == len(banned)


@testmap(feature="rule-banned-words", kind="perf")
def test_banned_words_perf():
    config = Config(banned_words=frozenset({"new", "old"}))
    text = "The new old widget. " * 2000
    start = time.perf_counter()
    banned_words.check(make_block(text), config)
    assert time.perf_counter() - start < 1.0


# -- max-sentence-length --------------------------------------------------


@testmap(feature="rule-max-sentence-length", kind="unit")
def test_max_sentence_length_unit():
    config = Config(max_sentence_length=5)
    findings = max_sentence_length.check(
        make_block("This sentence definitely has more than five words."), config
    )
    assert len(findings) == 1


@testmap(feature="rule-max-sentence-length", kind="property")
@given(st.integers(min_value=1, max_value=15))
def test_max_sentence_length_short_sentences_never_flagged(max_words: int):
    config = Config(max_sentence_length=max_words)
    text = " ".join(["word"] * max_words) + "."
    findings = max_sentence_length.check(make_block(text), config)
    assert findings == []


@testmap(feature="rule-max-sentence-length", kind="perf")
def test_max_sentence_length_perf():
    config = Config(max_sentence_length=20)
    text = "This is a sentence with words. " * 2000
    start = time.perf_counter()
    max_sentence_length.check(make_block(text), config)
    assert time.perf_counter() - start < 1.0


# -- passive-voice ----------------------------------------------------------


@testmap(feature="rule-passive-voice", kind="unit")
def test_passive_voice_unit():
    config = Config()
    findings = passive_voice.check(make_block("The file was deleted by the script."), config)
    assert len(findings) == 1


@testmap(feature="rule-passive-voice", kind="property")
@given(st.sampled_from(["was deleted", "is written", "were made", "is done"]))
def test_passive_voice_flags_known_passive_phrases(phrase: str):
    config = Config()
    findings = passive_voice.check(make_block(f"The item {phrase} today."), config)
    assert len(findings) >= 1


@testmap(feature="rule-passive-voice", kind="perf")
def test_passive_voice_perf():
    config = Config()
    text = "The file was deleted by the script. " * 2000
    start = time.perf_counter()
    passive_voice.check(make_block(text), config)
    assert time.perf_counter() - start < 1.0


# -- noun-cluster-length ----------------------------------------------------


@testmap(feature="rule-noun-cluster-length", kind="unit")
def test_noun_cluster_length_unit():
    config = Config(max_noun_cluster_length=3)
    findings = noun_cluster_length.check(
        make_block("Replace the fuel pump drive shaft gear housing assembly."), config
    )
    assert len(findings) == 1
    assert "noun cluster" in findings[0].message


@testmap(feature="rule-noun-cluster-length", kind="property")
@given(st.integers(min_value=1, max_value=10))
def test_noun_cluster_length_short_clusters_never_flagged(max_length: int):
    config = Config(max_noun_cluster_length=max_length)
    cluster = " ".join(f"noun{i}" for i in range(max_length))
    findings = noun_cluster_length.check(make_block(f"{cluster}."), config)
    assert findings == []


@testmap(feature="rule-noun-cluster-length", kind="perf")
def test_noun_cluster_length_perf():
    config = Config(max_noun_cluster_length=3)
    text = "Replace the fuel pump drive shaft gear housing assembly. " * 500
    start = time.perf_counter()
    noun_cluster_length.check(make_block(text), config)
    assert time.perf_counter() - start < 1.0


# -- auxiliary-verb-complex ---------------------------------------------------


@testmap(feature="rule-auxiliary-verb-complex", kind="unit")
def test_auxiliary_verb_complex_unit():
    findings = auxiliary_verb_complex.check(
        make_block("You should have finished checking the panel."), Config()
    )
    assert len(findings) == 1
    assert "should have finished" in findings[0].message


@testmap(feature="rule-auxiliary-verb-complex", kind="property")
@given(
    st.sampled_from(["can", "could", "may", "might", "must", "shall", "should", "will", "would"])
)
def test_auxiliary_verb_complex_flags_every_modal(modal: str):
    findings = auxiliary_verb_complex.check(
        make_block(f"It {modal} have finished by then."), Config()
    )
    assert len(findings) == 1


@testmap(feature="rule-auxiliary-verb-complex", kind="perf")
def test_auxiliary_verb_complex_perf():
    start = time.perf_counter()
    auxiliary_verb_complex.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0
