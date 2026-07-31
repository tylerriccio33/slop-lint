# slop-lint

A pre-commit hook that lints Python docstrings and comments for
[ASD-STE100](https://www.asd-ste100.org/) (Simplified Technical English)
style, plus a project-configurable list of banned words.

## What it checks

`slop-lint` extracts every module, class, and function docstring, and every
`#` comment, from a Python file and runs a small set of rules against the
prose:

| Rule | What it flags |
| --- | --- |
| `banned-words` | Words from the built-in default list (`src/slop_lint/data/banned_words.txt`), plus any you add in `pyproject.toml` |
| `max-sentence-length` | Sentences longer than a configurable word count (STE-100 targets ~20 words) |
| `passive-voice` | `be` + past-participle constructions (`was written`, `is given`), as a proxy for STE-100's active-voice requirement |
| `auxiliary-verb-complex` | Modal + `have` (+ `been`) + participle chains (`should have finished`), as a proxy for STE-100's disallowed complex verb constructions |

This is a **heuristic subset** of ASD-STE100, not a full implementation of the
spec (which also defines an ~900-word approved dictionary and rules like
one-word-one-meaning, no gerunds-as-nouns, etc.). See [Roadmap](#roadmap).

## Install

```bash
uv add --dev slop-lint
```

## Configure

Add a `[tool.slop-lint]` table to `pyproject.toml`:

```toml
[tool.slop-lint]
enable = ["banned-words", "max-sentence-length", "passive-voice"]
banned-words = ["frobnicate"]
max-sentence-length = 20
```

All keys are optional; the defaults above apply if omitted. `banned-words` in
`pyproject.toml` *adds to* the built-in default list rather than replacing it —
see `src/slop_lint/data/banned_words.txt` for the shipped defaults.

## Suppressing a finding

Add a `# slop-lint: ignore` comment on the offending line to suppress every
finding on that line, or `# slop-lint: ignore[rule-name, other-rule]` to
suppress only specific rules:

```python
# The value was computed above.  # slop-lint: ignore[passive-voice]
```

## Use as a pre-commit hook

This project ships a `.pre-commit-hooks.yaml`, so it works with either
[pre-commit](https://pre-commit.com/) or [prek](https://github.com/j178/prek)
(a faster, Rust-based drop-in runner):

```yaml
repos:
  - repo: https://github.com/tylerriccio33/slop-lint
    rev: v0.1.0
    hooks:
      - id: slop-lint
```

Then:

```bash
prek install
prek run --all-files
```

## Run directly

```bash
uv run slop-lint path/to/file.py [more_files.py ...]
```

Exits `1` if any findings are reported, `0` otherwise.

### Example

Given a file with a wordy, passive docstring:

```python
def process(data):
    """This function was designed by the engineer to process the input data
    structure that is passed into it by the caller in order to produce a
    cleansed and normalized output representation."""
    # The value was computed above.
    return data
```

Running `slop-lint` reports the violations and their locations:

```console
$ uv run slop-lint example.py
example.py:2:4: [max-sentence-length] sentence has 31 words (max 20): "This function was designed by the engineer to process the input data structure that is passed into it by the caller in order to produce a cleansed and normalized output representation."
example.py:2:18: [passive-voice] possible passive voice: "was designed"
example.py:2:91: [passive-voice] possible passive voice: "is passed"
example.py:5:14: [passive-voice] possible passive voice: "was computed"
```

## Development

This repo uses [uv](https://docs.astral.sh/uv/) for environment and
dependency management, [ruff](https://docs.astral.sh/ruff/) for linting and
formatting, [pyrefly](https://pyrefly.org/) for type checking, and
[pytest](https://docs.pytest.org/) for tests.

```bash
uv sync
uv run pytest
uv run ruff check .
uv run pyrefly check
```

This repo also dogfoods itself: `.pre-commit-config.yaml` runs ruff, pyrefly,
and `slop-lint` on every commit via `prek run --all-files`.

## Roadmap

- Full ASD-STE100 approved-word dictionary (opt-in, since it's prone to false
  positives on technical identifiers)
- Additional STE-100 rules: one-word-one-meaning, gerund-as-noun detection,
  complex conjunction limits
- Support for languages beyond Python (comment/docstring extraction is
  currently AST + `tokenize`-based and Python-specific)

## License

MIT
