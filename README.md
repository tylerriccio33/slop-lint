# ste100-lint

A pre-commit hook that lints Python docstrings and comments for
[ASD-STE100](https://www.asd-ste100.org/) (Simplified Technical English)
style, plus a project-configurable list of banned words.

## What it checks

`ste100-lint` extracts every module, class, and function docstring, and every
`#` comment, from a Python file and runs a small set of rules against the
prose:

| Rule | What it flags |
| --- | --- |
| `banned-words` | Words you've explicitly disallowed in `pyproject.toml` (e.g. `new`, `old`) |
| `max-sentence-length` | Sentences longer than a configurable word count (STE-100 targets ~20 words) |
| `passive-voice` | `be` + past-participle constructions (`was written`, `is given`), as a proxy for STE-100's active-voice requirement |

This is a **heuristic subset** of ASD-STE100, not a full implementation of the
spec (which also defines an ~900-word approved dictionary and rules like
one-word-one-meaning, no gerunds-as-nouns, etc.). See [Roadmap](#roadmap).

## Install

```bash
uv add --dev ste100-lint
```

## Configure

Add a `[tool.ste100-lint]` table to `pyproject.toml`:

```toml
[tool.ste100-lint]
enable = ["banned-words", "max-sentence-length", "passive-voice"]
banned-words = ["new", "old", "utilize", "leverage", "synergy"]
max-sentence-length = 20
```

All keys are optional; the defaults above apply if omitted.

## Use as a pre-commit hook

This project ships a `.pre-commit-hooks.yaml`, so it works with either
[pre-commit](https://pre-commit.com/) or [prek](https://github.com/j178/prek)
(a faster, Rust-based drop-in runner):

```yaml
repos:
  - repo: https://github.com/tylerriccio33/ste100-lint
    rev: v0.1.0
    hooks:
      - id: ste100-lint
```

Then:

```bash
prek install
prek run --all-files
```

## Run directly

```bash
uv run ste100-lint path/to/file.py [more_files.py ...]
```

Exits `1` if any findings are reported, `0` otherwise.

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
and `ste100-lint` on every commit via `prek run --all-files`.

## Roadmap

- Full ASD-STE100 approved-word dictionary (opt-in, since it's prone to false
  positives on technical identifiers)
- Additional STE-100 rules: one-word-one-meaning, gerund-as-noun detection,
  complex conjunction limits
- Support for languages beyond Python (comment/docstring extraction is
  currently AST + `tokenize`-based and Python-specific)
- Inline suppression comments (e.g. `# ste100: ignore`)

## License

MIT
