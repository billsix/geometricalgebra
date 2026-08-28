# Make the book build fail when a book notebook errors (execution gate)

**Status:** proposed — needs go-ahead.
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-08-28 (William Emerison Six <billsix@gmail.com>) — spun out of
[[fix-broken-book-notebooks-vector2-rename]], which surfaced that a broken book notebook ships
silently instead of failing the build.

## Problem

`make docs` does **not** fail when a `book/docs/notebooks/*.py` notebook raises at execution time.
myst-nb renders the traceback into the page as a *warning* and the build still exits 0, so a broken
notebook publishes a Python traceback in place of its intended output and nobody notices. This is
exactly how the `Vector2`/`Bivector2` drift ([[fix-broken-book-notebooks-vector2-rename]]) reached a
green build with two failing notebooks.

**Root cause (verified 2026-08-28):** `book/docs/conf.py` sets only `nb_execution_timeout = 600`;
myst-nb's `nb_execution_raise_on_error` is left at its default **`False`**, which downgrades an
execution error to a warning. And `entrypoint/docs.sh` runs `make html` / `make latexpdf` without
`-W`, so warnings never fail the build either.

## The change (propose, don't auto-wire — the gate is the user's call)

Primary option (native, minimal):
- Set **`nb_execution_raise_on_error = True`** in `book/docs/conf.py`. Then a notebook that raises
  makes `sphinx-build` exit non-zero; `docs.sh` is `set -eu` and "fails fast", so `make html`
  returning non-zero already aborts the build (the plumbing propagates — no `docs.sh` change needed).

Alternative (lighter, if the native flag proves too blunt):
- After the build, grep `book/docs/_build/html/reports/notebooks/*.err.log` and exit non-zero if any
  exist. More code, but decouples from myst-nb's behaviour.

**Do NOT reach for `-W` (warning-as-error) here.** The book currently emits 16 legitimate/benign
warnings (pre-existing `base.py` `|A|`-bar substitution refs; LaTeX hyperref duplicate-label noise
from documenting re-exported names under both `gacalc.functions` and `gacalc.transforms`). `-W` would
redden the build on those; scope the gate to notebook *execution errors* only.

## Prerequisite / ordering

**Prerequisite CLEARED 2026-08-29:** [[fix-broken-book-notebooks-vector2-rename]] landed (archived
`tasks/archive/2026/08/29/`), so all 14 book notebooks now execute clean — a 2026-08-28 `make docs`
rebuild produced **no** `reports/notebooks/` error dir at all. Turning the flag on would have failed
the build while `geometric-product` / `rotate` still imported `Vector2`/`Bivector2`; that no longer
applies, so this gate is now safe to turn on and will go green.

## Verification

- With the broken notebooks fixed and the flag on: `make docs` (nested, `--cgroups=disabled`) still
  exits **0** and produces HTML + PDF.
- Introduce a deliberate error in one book notebook (e.g. a bad import) → `make docs` exits
  **non-zero** (proves it gates), then revert.
- `book/docs/_build/html/reports/notebooks/` has no `*.err.log` on a clean run.

## Scope note — this is the book-notebook sibling of the pyright gate

[[add-notebook-pyright-gate]] gates the **repo-root `notebooks/`** (display notebooks) for *type*
errors via pyright. This task gates **`book/docs/notebooks/`** (the Sphinx-executed book notebooks)
for *execution* errors. Different directories, complementary failure modes (type vs runtime). Keep
them as two tasks unless a future `make check-notebooks` unifies both.

## Cross-links

- [[fix-broken-book-notebooks-vector2-rename]] — the prerequisite fix; the bug this gate would have
  caught.
- [[add-notebook-pyright-gate]] — the `notebooks/` type-check gate (sibling, different dir/failure).
- `entrypoint/docs.sh` (`set -eu`, `make html`/`make latexpdf`) and `book/docs/conf.py`
  (`nb_execution_timeout`) — the files this touches.
- Root sandbox `CLAUDE.md` "A multi-step check script must propagate every step's failure" /
  "Verification gates in nested containers" — the gate-shape conventions.

## Open questions

1. **Native flag or err.log grep?** Recommend `nb_execution_raise_on_error = True` (one line, native,
   propagates through the existing `set -eu` docs.sh). The grep is the fallback only if the flag
   proves too blunt (e.g. a notebook we *want* to show an error on purpose — none exist today).
