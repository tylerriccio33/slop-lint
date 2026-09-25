# slop-lint

A pre-commit hook that lints Python docstrings and comments for
[ASD-STE100](https://www.asd-ste100.org/) (Simplified Technical English)
style, plus a project-configurable list of banned words.

## What it checks

`slop-lint` extracts docstrings and `#` comments from Python files, and runs
rules against that prose. It also reads comments in Rust (`.rs`) and
Makefiles, and paragraphs in `.md` and `.txt` files.

| Rule | Flags | Example output |
| --- | --- | --- |
| `banned-words` | Words from the [built-in list](src/slop_lint/data/banned_words.txt), plus any you add | `banned word "utilize"` |
| `max-sentence-length` | Sentences over `max-sentence-length` words (default 20) | `sentence has 31 words (max 20): "..."` |
| `passive-voice` | `be` + past participle (`was written`), a proxy for active voice | `possible passive voice: "was computed"` |
| `auxiliary-verb-complex` | Modal + `have` (+ `been`) + participle | `complex verb construction: "should have been cleared"` |
| `noun-cluster-length` | Noun clusters over `max-noun-cluster-length` words (default 3) | `noun cluster has 5 words (max 3): "database connection pool timeout value"` |
| `no-prose` | Every docstring and comment (see [Strict preset](#strict-preset)) | `function docstring not allowed` |
| `prose-budget` | Scopes with too much prose for their code (see [Prose budget](#prose-budget)) | `'add' has 5 prose line(s) (4 docstring + 1 comment) for 2 LOC (allowed 0)` |

The defaults enable `banned-words`, `max-sentence-length`, and `passive-voice`.

These rule names exist as stubs for the rest of the spec, and flag nothing yet:
`approved-abbreviations`, `approved-verb-forms`, `approved-word-sense`,
`descriptive-sentence-length`, `ing-form-usage`, `instruction-clarity`,
`max-sentences-per-paragraph`, `no-omitted-sentence-parts`,
`one-instruction-per-sentence`, `one-topic-per-paragraph`,
`safety-instruction-start`, `vertical-list-suggestion`.

This is a **heuristic subset** of ASD-STE100, not a full implementation. See
[Roadmap](#roadmap).

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
max-noun-cluster-length = 3
preset = "strict"              # optional, see below

[tool.slop-lint.budget]
loc-per-prose-line = 5         # optional, see below
```

All keys are optional; the defaults above apply if omitted. `banned-words` in
`pyproject.toml` *adds to* the built-in default list rather than replacing it —
see `src/slop_lint/data/banned_words.txt` for the shipped defaults.

## Strict preset

The `strict` preset adds `no-prose`, which flags every docstring and comment.
It ignores tool pragmas such as `# noqa`, `# type: ignore`, and shebangs.
Turn it on with `preset = "strict"` or `--preset strict`.

`--fix` removes every docstring and comment from the Python files you give
it. It keeps pragmas, and puts `pass` in a body that becomes empty:

```python
def add(a, b):
    """Add two numbers.

    Returns the sum of a and b.
    """
    # Plain addition.
    return a + b
```

```console
$ uv run slop-lint --preset strict add.py
add.py:2:4: no-prose function docstring not allowed
add.py:6:4: no-prose comment not allowed
Found 2 issues
$ uv run slop-lint --fix add.py
add.py: stripped docstrings and comments
Fixed 1 file
$ cat add.py
def add(a, b):
    return a + b
```

## Prose budget

A budget limits prose instead of banning it. Each module, class, and function
gets one prose line per `N` lines of code. Docstring lines and comment lines
both count as prose. A comment counts against its innermost scope. Set it
with `loc-per-prose-line = N` under `[tool.slop-lint.budget]`, or with
`--budget N`.

For the `add` function above, with `N` = 5:

```console
$ uv run slop-lint --budget 5 add.py
add.py:1:0: prose-budget 'add' has 5 prose line(s) (4 docstring + 1 comment) for 2 LOC (allowed 0)
Found 1 issue
```

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
uv run slop-lint --preset strict --budget 5 path/to/file.py
uv run slop-lint --fix path/to/file.py
```

The exit code is `1` if there are findings, and `0` if there are none.

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
example.py:2:4: max-sentence-length sentence has 31 words (max 20): "This function was designed ..."
example.py:2:18: passive-voice possible passive voice: "was designed"
example.py:3:15: passive-voice possible passive voice: "is passed"
example.py:5:14: passive-voice possible passive voice: "was computed"
Found 4 issues
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
