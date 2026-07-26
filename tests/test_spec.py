"""Conformance tests against ASD-STE100 (Simplified Technical English).

ASD-STE100 is a proprietary standard published by ASD. It is not free to
distribute, so no official machine-readable test suite exists to import.
Instead, this file encodes the public writing rules and dictionary
principles (as summarized on Wikipedia) as test cases. Each test checks
one rule against slop-lint's rule set.

slop-lint currently checks only banned words, sentence length, and passive
voice, so most of these rules are not yet implemented. Tests for gaps use
``xfail`` instead of skip. This marks the gap and lets the test start
passing once the rule set gains the check.
"""

from __future__ import annotations

import pytest

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules import banned_words, max_sentence_length, noun_cluster_length, passive_voice


def make_block(text: str, line: int = 1, col: int = 4) -> TextBlock:
    return TextBlock(text=text, kind="comment", line=line, col=col)


def flagged(text: str, config: Config | None = None) -> bool:
    """True if any currently-implemented rule flags ``text``."""
    cfg = config or Config()
    block = make_block(text)
    findings = [
        *banned_words.check(block, cfg),
        *max_sentence_length.check(block, cfg),
        *passive_voice.check(block, cfg),
        *noun_cluster_length.check(block, cfg),
    ]
    return bool(findings)


# --- Writing rules ------------------------------------------------------


def test_use_approved_words_only_with_their_dictionary_meaning():
    """Use the approved words only as the part of speech and meaning given in the dictionary."""
    config = Config(banned_words=frozenset({"utilize", "commence", "terminate"}))
    findings = banned_words.check(
        make_block("Utilize the tool to commence the test, then terminate it."), config
    )
    assert len(findings) == 3


@pytest.mark.xfail(reason="no rule judges instruction clarity/specificity", strict=True)
def test_make_instructions_as_clear_and_specific_as_possible():
    """Make instructions as clear and specific as possible."""
    assert flagged("Do the thing to the part as needed.")


def test_no_multi_word_nouns_over_three_words():
    """Do not write multi-word nouns that have more than three words."""
    assert flagged("Replace the fuel pump drive shaft gear housing assembly.")


@pytest.mark.xfail(reason="no rule restricts verbs to the seven approved forms", strict=True)
def test_use_only_approved_verb_forms():
    """Use approved verb forms only: infinitive, imperative, simple present/past/future,
    and the past participle (only as an adjective)."""
    assert flagged("The technician will have finished the closing procedure by that time.")


@pytest.mark.xfail(reason="no rule bans auxiliary-verb complex constructions", strict=True)
def test_no_auxiliary_verbs_for_complex_constructions():
    """Do not use auxiliary verbs to make complex verb constructions."""
    assert flagged("The technician should have finished checking the panel by now.")


@pytest.mark.xfail(
    reason="no rule restricts '-ing' forms to technical nouns/modifiers", strict=True
)
def test_ing_form_only_as_technical_noun_or_modifier():
    """Use the '-ing' form only as a technical noun or a modifier, not
    as a continuous verb tense."""
    assert flagged("The technician is recording the reading while the pump is running.")


def test_use_active_voice():
    """Use the active voice. In descriptive writing, use the passive voice only when
    the agent is unknown."""
    assert flagged("The valve must be opened before the pump is started.")


def test_sentence_word_limit_for_instructions():
    """Write short sentences: no more than 20 words in instructions (procedures)."""
    config = Config(max_sentence_length=20)
    long_sentence = " ".join(["word"] * 25) + "."
    findings = max_sentence_length.check(make_block(long_sentence), config)
    assert findings


@pytest.mark.xfail(
    reason="no rule distinguishes a 25-word limit for descriptive text vs 20 for procedures",
    strict=True,
)
def test_sentence_word_limit_for_descriptions_is_higher():
    """Write short sentences: no more than 25 words in descriptive text."""
    config = Config(max_sentence_length=20)
    text_of_22_words = " ".join(["word"] * 22) + "."
    findings = max_sentence_length.check(make_block(text_of_22_words), config)
    assert not findings, "a 22-word descriptive sentence should be within the 25-word limit"


@pytest.mark.xfail(
    reason="no rule detects omitted sentence parts (verb, subject, article)", strict=True
)
def test_do_not_omit_sentence_parts_to_shorten_text():
    """Do not omit parts of the sentence (e.g. verb, subject, article) to make the
    text shorter."""
    assert flagged("Remove panel, replace seal, install cover.")


@pytest.mark.xfail(reason="no rule suggests vertical lists for complex text", strict=True)
def test_use_vertical_lists_for_complex_text():
    """Use vertical lists for complex text."""
    assert flagged(
        "Remove the bolt, the washer, the bracket, the seal, and the cover, in that order."
    )


@pytest.mark.xfail(reason="no rule detects multiple instructions in a single sentence", strict=True)
def test_one_instruction_per_sentence():
    """Write one instruction per sentence."""
    assert flagged("Remove the panel and replace the seal and then install the cover.")


@pytest.mark.xfail(reason="no rule enforces a single topic per paragraph", strict=True)
def test_one_topic_per_paragraph():
    """Write only one topic per paragraph."""
    text = "Remove the panel. Install the sensor. The sky is clear today. Torque the bolts."
    assert flagged(text)


@pytest.mark.xfail(reason="no rule limits a paragraph to six sentences", strict=True)
def test_no_more_than_six_sentences_per_paragraph():
    """Do not write more than six sentences in each paragraph."""
    paragraph = " ".join(f"Do step {i}." for i in range(1, 8))
    assert flagged(paragraph)


@pytest.mark.xfail(
    reason="no rule checks that safety instructions open with a command/condition",
    strict=True,
)
def test_safety_instructions_start_with_a_command_or_condition():
    """Start safety instructions with a clear command or condition."""
    assert flagged("It is necessary to disconnect the power before you remove the panel.")


# --- Dictionary principles ------------------------------------------------


def test_one_word_one_part_of_speech_one_meaning():
    """Each approved word has one part of speech and one meaning; using it outside that
    meaning (e.g. 'acceptance' instead of the approved verb 'ACCEPT') is not allowed."""
    config = Config(banned_words=frozenset({"acceptance"}))
    findings = banned_words.check(
        make_block("Before acceptance of the unit, do the specified test procedure."), config
    )
    assert findings


def test_approved_word_used_outside_its_approved_meaning():
    """Use 'close' (v) only to mean 'move together/stop movement' or
    'operate a circuit breaker'. Do not use it for other senses, such
    as closing a meeting."""
    config = Config(banned_words=frozenset({"close"}))
    findings = banned_words.check(make_block("Close the meeting after the review."), config)
    assert findings, "an over-broad banned-word match at least catches the literal word"


@pytest.mark.xfail(
    reason="no rule distinguishes approved vs non-approved senses of the same word "
    "(e.g. 'close' the door vs. 'close' meaning 'near')",
    strict=True,
)
def test_non_approved_adjective_sense_flagged_even_when_word_not_banned():
    """Do not use the adjective 'close' (meaning 'near'); use 'near'
    instead. The rule set does approve the verb 'close', so this test
    needs sense-level, not word-level, matching."""
    assert flagged("Do not go close to the landing gear.")


@pytest.mark.xfail(
    reason="no rule checks abbreviation usage against the approved list", strict=True
)
def test_use_approved_abbreviations_only():
    """Use only the abbreviations that the Dictionary gives."""
    assert flagged("Rmv the panel asap.")
