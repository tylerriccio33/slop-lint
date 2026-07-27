"""testmap-tagged tests for the not-yet-implemented rule checks.

Unit tests encode the docstring's intent and are xfail. Property/perf
tests assert the stub's real always-empty behavior.

testmap scans source statically, so tagged tests must be literal defs,
not factory-built.
"""

from __future__ import annotations

import time

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pytest_testmap import testmap

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules import (
    approved_abbreviations,
    approved_verb_forms,
    approved_word_sense,
    auxiliary_verb_complex,
    descriptive_sentence_length,
    ing_form_usage,
    instruction_clarity,
    max_sentences_per_paragraph,
    no_omitted_sentence_parts,
    one_instruction_per_sentence,
    one_topic_per_paragraph,
    safety_instruction_start,
    vertical_list_suggestion,
)

PERF_TEXT = "word " * 20000


def make_block(text: str, line: int = 1, col: int = 4) -> TextBlock:
    return TextBlock(text=text, kind="comment", line=line, col=col)


# -- approved-abbreviations --------------------------------------------------


@testmap(feature="rule-approved-abbreviations", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_approved_abbreviations_unit():
    findings = approved_abbreviations.check(make_block("Rmv the panel asap."), Config())
    assert findings != []


@testmap(feature="rule-approved-abbreviations", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_approved_abbreviations_property_stub_always_empty(text: str):
    assert approved_abbreviations.check(make_block(text), Config()) == []


@testmap(feature="rule-approved-abbreviations", kind="perf")
def test_approved_abbreviations_perf():
    start = time.perf_counter()
    approved_abbreviations.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- approved-verb-forms ------------------------------------------------------


@testmap(feature="rule-approved-verb-forms", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_approved_verb_forms_unit():
    findings = approved_verb_forms.check(
        make_block("The task will have finished by then."), Config()
    )
    assert findings != []


@testmap(feature="rule-approved-verb-forms", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_approved_verb_forms_property_stub_always_empty(text: str):
    assert approved_verb_forms.check(make_block(text), Config()) == []


@testmap(feature="rule-approved-verb-forms", kind="perf")
def test_approved_verb_forms_perf():
    start = time.perf_counter()
    approved_verb_forms.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- approved-word-sense -------------------------------------------------


@testmap(feature="rule-approved-word-sense", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_approved_word_sense_unit():
    findings = approved_word_sense.check(make_block("Stand close to the panel."), Config())
    assert findings != []


@testmap(feature="rule-approved-word-sense", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_approved_word_sense_property_stub_always_empty(text: str):
    assert approved_word_sense.check(make_block(text), Config()) == []


@testmap(feature="rule-approved-word-sense", kind="perf")
def test_approved_word_sense_perf():
    start = time.perf_counter()
    approved_word_sense.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- auxiliary-verb-complex -----------------------------------------------


@testmap(feature="rule-auxiliary-verb-complex", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_auxiliary_verb_complex_unit():
    findings = auxiliary_verb_complex.check(
        make_block("You should have finished checking the panel."), Config()
    )
    assert findings != []


@testmap(feature="rule-auxiliary-verb-complex", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_auxiliary_verb_complex_property_stub_always_empty(text: str):
    assert auxiliary_verb_complex.check(make_block(text), Config()) == []


@testmap(feature="rule-auxiliary-verb-complex", kind="perf")
def test_auxiliary_verb_complex_perf():
    start = time.perf_counter()
    auxiliary_verb_complex.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- descriptive-sentence-length ------------------------------------------


@testmap(feature="rule-descriptive-sentence-length", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_descriptive_sentence_length_unit():
    text = (
        "This is a purely descriptive sentence that runs on for more than "
        "twenty five words in total just to demonstrate the higher limit "
        "that applies to descriptive text."
    )
    findings = descriptive_sentence_length.check(make_block(text), Config())
    assert findings != []


@testmap(feature="rule-descriptive-sentence-length", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_descriptive_sentence_length_property_stub_always_empty(text: str):
    assert descriptive_sentence_length.check(make_block(text), Config()) == []


@testmap(feature="rule-descriptive-sentence-length", kind="perf")
def test_descriptive_sentence_length_perf():
    start = time.perf_counter()
    descriptive_sentence_length.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- ing-form-usage ---------------------------------------------------------


@testmap(feature="rule-ing-form-usage", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_ing_form_usage_unit():
    findings = ing_form_usage.check(
        make_block("The system is recording the data continuously."), Config()
    )
    assert findings != []


@testmap(feature="rule-ing-form-usage", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_ing_form_usage_property_stub_always_empty(text: str):
    assert ing_form_usage.check(make_block(text), Config()) == []


@testmap(feature="rule-ing-form-usage", kind="perf")
def test_ing_form_usage_perf():
    start = time.perf_counter()
    ing_form_usage.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- instruction-clarity ---------------------------------------------------


@testmap(feature="rule-instruction-clarity", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_instruction_clarity_unit():
    block = make_block("Do the thing to the part as needed.")
    findings = instruction_clarity.check(block, Config())
    assert findings != []


@testmap(feature="rule-instruction-clarity", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_instruction_clarity_property_stub_always_empty(text: str):
    assert instruction_clarity.check(make_block(text), Config()) == []


@testmap(feature="rule-instruction-clarity", kind="perf")
def test_instruction_clarity_perf():
    start = time.perf_counter()
    instruction_clarity.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- max-sentences-per-paragraph -------------------------------------------


@testmap(feature="rule-max-sentences-per-paragraph", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_max_sentences_per_paragraph_unit():
    text = " ".join(f"Sentence number {i}." for i in range(1, 8))
    findings = max_sentences_per_paragraph.check(make_block(text), Config())
    assert findings != []


@testmap(feature="rule-max-sentences-per-paragraph", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_max_sentences_per_paragraph_property_stub_always_empty(text: str):
    assert max_sentences_per_paragraph.check(make_block(text), Config()) == []


@testmap(feature="rule-max-sentences-per-paragraph", kind="perf")
def test_max_sentences_per_paragraph_perf():
    start = time.perf_counter()
    max_sentences_per_paragraph.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- no-omitted-sentence-parts ---------------------------------------------


@testmap(feature="rule-no-omitted-sentence-parts", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_no_omitted_sentence_parts_unit():
    findings = no_omitted_sentence_parts.check(
        make_block("Remove panel, replace seal, install cover."), Config()
    )
    assert findings != []


@testmap(feature="rule-no-omitted-sentence-parts", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_no_omitted_sentence_parts_property_stub_always_empty(text: str):
    assert no_omitted_sentence_parts.check(make_block(text), Config()) == []


@testmap(feature="rule-no-omitted-sentence-parts", kind="perf")
def test_no_omitted_sentence_parts_perf():
    start = time.perf_counter()
    no_omitted_sentence_parts.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- one-instruction-per-sentence -------------------------------------------


@testmap(feature="rule-one-instruction-per-sentence", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_one_instruction_per_sentence_unit():
    text = "Remove the panel and replace the seal and then install the cover."
    findings = one_instruction_per_sentence.check(make_block(text), Config())
    assert findings != []


@testmap(feature="rule-one-instruction-per-sentence", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_one_instruction_per_sentence_property_stub_always_empty(text: str):
    assert one_instruction_per_sentence.check(make_block(text), Config()) == []


@testmap(feature="rule-one-instruction-per-sentence", kind="perf")
def test_one_instruction_per_sentence_perf():
    start = time.perf_counter()
    one_instruction_per_sentence.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- one-topic-per-paragraph -------------------------------------------------


@testmap(feature="rule-one-topic-per-paragraph", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_one_topic_per_paragraph_unit():
    text = "Remove the panel. By the way, the weather was nice yesterday."
    findings = one_topic_per_paragraph.check(make_block(text), Config())
    assert findings != []


@testmap(feature="rule-one-topic-per-paragraph", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_one_topic_per_paragraph_property_stub_always_empty(text: str):
    assert one_topic_per_paragraph.check(make_block(text), Config()) == []


@testmap(feature="rule-one-topic-per-paragraph", kind="perf")
def test_one_topic_per_paragraph_perf():
    start = time.perf_counter()
    one_topic_per_paragraph.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- safety-instruction-start ------------------------------------------------


@testmap(feature="rule-safety-instruction-start", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_safety_instruction_start_unit():
    text = "It is necessary to disconnect the power before you remove the panel."
    findings = safety_instruction_start.check(make_block(text), Config())
    assert findings != []


@testmap(feature="rule-safety-instruction-start", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_safety_instruction_start_property_stub_always_empty(text: str):
    assert safety_instruction_start.check(make_block(text), Config()) == []


@testmap(feature="rule-safety-instruction-start", kind="perf")
def test_safety_instruction_start_perf():
    start = time.perf_counter()
    safety_instruction_start.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0


# -- vertical-list-suggestion ------------------------------------------------


@testmap(feature="rule-vertical-list-suggestion", kind="unit")
@pytest.mark.xfail(reason="not yet implemented", strict=True)
def test_vertical_list_suggestion_unit():
    text = "Remove the bolt, washer, bracket, seal, and cover, in that order."
    findings = vertical_list_suggestion.check(make_block(text), Config())
    assert findings != []


@testmap(feature="rule-vertical-list-suggestion", kind="property")
@given(st.text(min_size=0, max_size=200))
def test_vertical_list_suggestion_property_stub_always_empty(text: str):
    assert vertical_list_suggestion.check(make_block(text), Config()) == []


@testmap(feature="rule-vertical-list-suggestion", kind="perf")
def test_vertical_list_suggestion_perf():
    start = time.perf_counter()
    vertical_list_suggestion.check(make_block(PERF_TEXT), Config())
    assert time.perf_counter() - start < 1.0
