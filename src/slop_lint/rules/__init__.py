"""Registry of available rules, keyed by name."""

from __future__ import annotations

from types import ModuleType

from slop_lint.rules import (
    approved_abbreviations,
    approved_verb_forms,
    approved_word_sense,
    auxiliary_verb_complex,
    banned_words,
    descriptive_sentence_length,
    ing_form_usage,
    instruction_clarity,
    max_sentence_length,
    max_sentences_per_paragraph,
    no_omitted_sentence_parts,
    noun_cluster_length,
    one_instruction_per_sentence,
    one_topic_per_paragraph,
    passive_voice,
    safety_instruction_start,
    vertical_list_suggestion,
)

REGISTRY: dict[str, ModuleType] = {
    banned_words.name: banned_words,
    max_sentence_length.name: max_sentence_length,
    passive_voice.name: passive_voice,
    instruction_clarity.name: instruction_clarity,
    noun_cluster_length.name: noun_cluster_length,
    approved_verb_forms.name: approved_verb_forms,
    auxiliary_verb_complex.name: auxiliary_verb_complex,
    ing_form_usage.name: ing_form_usage,
    descriptive_sentence_length.name: descriptive_sentence_length,
    no_omitted_sentence_parts.name: no_omitted_sentence_parts,
    vertical_list_suggestion.name: vertical_list_suggestion,
    one_instruction_per_sentence.name: one_instruction_per_sentence,
    one_topic_per_paragraph.name: one_topic_per_paragraph,
    max_sentences_per_paragraph.name: max_sentences_per_paragraph,
    safety_instruction_start.name: safety_instruction_start,
    approved_word_sense.name: approved_word_sense,
    approved_abbreviations.name: approved_abbreviations,
}
