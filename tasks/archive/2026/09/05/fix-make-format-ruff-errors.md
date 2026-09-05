# Fix `make format` ruff errors (5 from the Odd_3 work + 1 pre-existing)

**Status:** DONE 2026-09-05 — `make format` green (ruff + `ty` clean); archived
**Priority:** 3
**Difficulty:** 1

## Resolution (2026-09-05)

All six fixed; `make format` verified green. What was done:
- **(1) `base.py:1188`** and **(2)–(4) `test_odd3.py:6/8/10`** — reflowed the docstring paragraphs to
  ≤88; the `test_odd3.py` docstring's stale `tasks/model-odd-graded-type.md` reference was **dropped**
  (kept the durable `graded-subspaces-vs-subalgebras.md` one).
- **(5) `displaygraded.py:313`** — replaced `print(error)` with
  `display(Markdown(f"raises \`ValueError\`: {error}"))` (matches the notebook's display style, no T201).
- **(6) pre-existing codemod E501** — resolved by **excluding `tasks/adhoc/` from ruff** (`pyproject.toml`
  `extend-exclude`, with a rationale comment: transient task-scoped audit scripts, not policed source),
  fixing the whole ad-hoc class rather than one line.
- **Process note:** these slipped because the Odd_3 verify harness ran `ty` + `pytest` + notebook but
  not `ruff`. `make format` is the real gate — run it before calling generated-typing work done.

## BLUF

`make format` is **red**: 6 ruff errors (E501 line-length ×5, T201 print ×1). **`ty check
src/tests/tools` is fully clean** (all three pass). Five of the six were introduced by the just-merged
Odd_3 work and slipped because that work's verify harness ran `ty` + `pytest` + the notebook execution
but **not `ruff`**; the sixth is a pre-existing E501 in an old ad-hoc codemod. All five Odd_3 ones are
trivial reflows/one-liners; the pre-existing one needs a small decision. Done = `make format` green.

## The 6 errors (exact locations from `make format`, 2026-09-05)

**Mine (from the Odd_3 merge) — trivial:**
1. **`src/gacalc/base.py:1188`** — E501 (96>88). My `sandwich` docstring edit reflowed an adjacent
   line past 88 (`keeps only ``x``'s blades. ``zero`` conjugates to ``zero`` (no ``is_vector`` …`).
   **Fix:** re-wrap that docstring paragraph to ≤88 (reflow the paragraph, not just the one line).
2. **`tests/test_odd3.py:6`** — E501 (89>88), docstring line. **Fix:** reflow.
3. **`tests/test_odd3.py:8`** — E501 (91>88), docstring line. **Fix:** reflow.
4. **`tests/test_odd3.py:10`** — E501 (91>88), docstring line — **AND it still references the now-
   archived task path** `tasks/model-odd-graded-type.md`. **Fix:** reflow **and** repoint to
   `tasks/archive/2026/09/05/model-odd-graded-type.md` (or drop it and keep the
   `graded-subspaces-vs-subalgebras.md` reference, which is the durable one).
5. **`notebooks/displaygraded.py:313`** — T201 `print` found (my `except ValueError as error:
   print(error)` in the new Odd_3 cast-raise demo cell). **T201 is in the repo-wide ruff `select` and
   there is NO notebook exemption** — and `displaygraded.py` is the only notebook that uses `print`
   (the others use `show()`/`display()`). **Fix — pick one:**
   - (a) replace `print(error)` with `display(Markdown(f"raises \`ValueError\`: {error}"))` (matches
     the notebook's existing display style; `Markdown`/`display` are already imported) — RECOMMENDED;
   - (b) add a `# noqa: T201` at that line;
   - (c) add a notebooks per-file-ignore for `T201` in `pyproject.toml` (a config decision — only if
     notebooks-should-print-freely is the maintainer's intent).

**Pre-existing (NOT from Odd_3) — needs a small decision:**
6. **`tasks/adhoc/drop-graded-type-dimension-suffixes/codemod.py:23`** — E501 (101>88), a long path in
   a docstring of an **old ad-hoc codemod** (the Vector2→Vector rename). This has been failing the
   gate since before the Odd_3 work. **Fix — pick one:**
   - (a) **exclude `tasks/adhoc/` from ruff** via `extend-exclude` in `pyproject.toml` (ad-hoc scripts
     are transient audit artifacts, not policed source — mirrors how the vendored `entrypoint/` tree is
     excluded) — RECOMMENDED, and fixes the class, not just this line;
   - (b) `# noqa: E501` on line 23;
   - (c) if the codemod is truly finished/dead, `git rm` it (its job is long done).

## Verification

`make format` exits green (ruff clean + `ty` clean). Note: **run `ruff` as part of any future
generated-typing verification** — the Odd_3 harness checked `ty`+tests+notebook but not `ruff`, which
is exactly how (1)–(5) slipped; `make format` is the real gate.

## Open questions

1. **The notebook `print` (T201)** — replace with `display(...)` (a), `# noqa` (b), or exempt
   notebooks from T201 in config (c)? *(Recommend (a).)*
2. **The pre-existing ad-hoc E501** — exclude `tasks/adhoc/` from ruff (a), `# noqa` (b), or remove the
   dead codemod (c)? *(Recommend (a) — excludes the whole transient-adhoc class from the gate.)*
