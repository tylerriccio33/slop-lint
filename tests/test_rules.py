from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules import banned_words, max_sentence_length, passive_voice


def make_block(text: str, line: int = 1, col: int = 4) -> TextBlock:
    return TextBlock(text=text, kind="comment", line=line, col=col)


def test_banned_words_flags_configured_word():
    config = Config(banned_words=frozenset({"new", "old"}))
    findings = banned_words.check(make_block("Use the new widget, not the old one."), config)
    assert [f.message for f in findings] == ['banned word "new"', 'banned word "old"']


def test_banned_words_is_case_insensitive_and_whole_word():
    config = Config(banned_words=frozenset({"new"}))
    findings = banned_words.check(make_block("A New renewal is fine."), config)
    assert len(findings) == 1
    assert findings[0].message == 'banned word "New"'


def test_banned_words_reports_multiline_position():
    config = Config(banned_words=frozenset({"old"}))
    block = make_block("Line one.\nAn old idea.", line=10, col=4)
    findings = banned_words.check(block, config)
    assert findings[0].line == 11


def test_banned_words_empty_list_yields_nothing():
    config = Config(banned_words=frozenset())
    findings = banned_words.check(make_block("new old"), config)
    assert findings == []


def test_max_sentence_length_flags_long_sentence():
    config = Config(max_sentence_length=5)
    findings = max_sentence_length.check(
        make_block("This sentence definitely has more than five words in it."), config
    )
    assert len(findings) == 1
    assert "words" in findings[0].message


def test_max_sentence_length_allows_short_sentences():
    config = Config(max_sentence_length=20)
    findings = max_sentence_length.check(make_block("Short and fine."), config)
    assert findings == []


def test_passive_voice_flags_be_plus_participle():
    config = Config()
    findings = passive_voice.check(make_block("The file was deleted by the script."), config)
    assert len(findings) == 1
    assert "was deleted" in findings[0].message


def test_passive_voice_ignores_active_sentences():
    config = Config()
    findings = passive_voice.check(make_block("The script deletes the file."), config)
    assert findings == []


def test_passive_voice_flags_irregular_participle():
    config = Config()
    findings = passive_voice.check(make_block("The value is given by the caller."), config)
    assert len(findings) == 1
