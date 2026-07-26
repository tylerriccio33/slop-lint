from ste100_lint.sentences import split_sentences


def test_splits_on_terminal_punctuation():
    sentences = split_sentences("Do the thing. Then do another thing!")
    assert [s.text for s in sentences] == ["Do the thing.", "Then do another thing!"]


def test_single_sentence_no_trailing_period():
    sentences = split_sentences("Do the thing")
    assert [s.text for s in sentences] == ["Do the thing"]


def test_offsets_point_back_into_source_text():
    text = "First sentence. Second sentence."
    sentences = split_sentences(text)
    for sentence in sentences:
        start = sentence.offset
        assert text[start : start + len(sentence.text)] == sentence.text


def test_empty_text_yields_no_sentences():
    assert split_sentences("") == []
