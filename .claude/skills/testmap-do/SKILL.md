---
name: testmap-do
description: >-
  Use in projects that have testmap installed (a [tool.testmap] table in
  pyproject.toml, or @testmap-tagged tests). Covers running the report, tagging
  tests, selecting which functions to map, and writing each test kind (unit,
  integration, property, perf) simply. Trigger on requests like "fill out the
  testmap", "map these functions", "add the missing test kinds", "skip private
  functions".
---

# testmap-do

testmap tracks, per **feature**, which **kinds** of test exist (`unit`,
`integration`, `property`, `perf`, …) and flags required kinds that are missing.
A feature is any name you choose — usually a function or class.

## Read the current map first

```
testmap report            # scan testpaths, print the matrix, exit 1 if gaps
testmap report --json     # same, machine-readable
```

Rows are features; columns are kinds; the `Missing:` section lists the gaps to
fill. `n/a` means the kind is excluded for that feature. Always start here — fill
exactly what `Missing:` reports, nothing more.

## Tag a test

One decorator per test. `feature` and `kind` are required strings.

```python
from pytest_testmap import testmap

@testmap(feature="parser", kind="unit")
def test_parses_empty():
    assert parse("") == []
```

- `feature` = the thing under test (match existing feature names in the report).
- `kind` = one of the taxonomy kinds in `[tool.testmap] kinds`.
- A test with no `@testmap` decorator is simply ignored by testmap.

## Which functions to map

The expected feature universe can be declared in `pyproject.toml` so untested
functions show up as all-missing rows instead of vanishing:

```toml
[[tool.testmap.generate]]
select = "functions"   # or "classes"
from = "src/**/*.py"   # glob, relative to pyproject.toml
where = "public"       # public | private | all  (private = leading underscore)
```

Only top-level defs count. When a user says **"map the functions"**, add/adjust a
generate block (or just tag tests for each public function). **"skip private
functions"** → `where = "public"`. **"only this file"** → narrow `from`. After
editing config, re-run `testmap report` to see the new gaps.

## Writing each kind, simply

Pick the feature and kind from `Missing:`, write the smallest honest test, tag it,
re-run `testmap report`. Keep tests minimal — the goal is evidence a kind was
considered, not exhaustive coverage.

- **unit** — call the function directly, assert on the return for a representative
  input (and an edge case). The default kind.
- **integration** — exercise it through a real neighbor (its caller, the CLI, a
  temp file, a real object it collaborates with) rather than in isolation.
- **property** — assert an invariant over generated inputs (e.g. round-trip
  `decode(encode(x)) == x`, idempotence, sortedness). Use Hypothesis if present;
  otherwise a small loop over a handful of inputs is fine.
- **perf** — either (a) assert a real bound (`assert elapsed < 0.1`, complexity
  stays linear), or (b) if perf isn't meaningfully at risk here, write a passing
  test whose body/comment records that you considered it and found it irrelevant:

  ```python
  @testmap(feature="parser", kind="perf")
  def test_perf():
      # Pure string parsing on small inputs; no perf-sensitive path. Considered, N/A.
      assert True
  ```

  Prefer excluding the kind in config (`exclude = ["perf"]`) if a feature never
  needs it, rather than writing stub tests for every one.

## Loop

1. `testmap report` → read `Missing:`.
2. For each gap, write one small tagged test (above).
3. `testmap report` again → confirm the row is `✓` (exit 0).
