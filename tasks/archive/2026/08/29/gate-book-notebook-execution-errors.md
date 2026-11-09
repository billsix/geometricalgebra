# Make the book build fail when a book notebook errors (execution gate)

**Created:** 2026-08-28 · **Completed:** 2026-08-29
**Source:** spun out of `tasks/archive/2026/08/29/fix-broken-book-notebooks-vector2-rename.md`, which
showed that a broken book notebook shipped silently instead of failing the build

## Problem

`make docs` did not fail when a `book/docs/notebooks/*.py` notebook raised at execution time: myst-nb
rendered the traceback into the page as a warning and the build exited 0. That is how the
`Vector2`/`Bivector2` drift reached a green build. Root cause (verified 2026-08-28):
`book/docs/conf.py` set only `nb_execution_timeout = 600`, leaving myst-nb's
`nb_execution_raise_on_error` at its default `False`; and `entrypoint/docs.sh` runs `make html` /
`make latexpdf` without `-W`.

## Decisions

- **Native flag, not an err.log grep.** `nb_execution_raise_on_error = True` is one line and
  propagates through the existing `set -eu` `docs.sh`. The rejected alternative — grepping
  `book/docs/_build/html/reports/notebooks/*.err.log` after the build — was kept only as a fallback
  should the flag prove too blunt (e.g. a notebook meant to show an error; none existed).
- **Not `-W`.** The book emitted 16 benign pre-existing warnings (`base.py` `|A|`-bar substitution
  refs; hyperref duplicate labels from re-exported names documented under both `gacalc.functions` and
  `gacalc.transforms`), so warning-as-error would have reddened the build; the gate is scoped to
  notebook execution errors.
- **Kept separate from the pyright gate** (`tasks/archive/2026/11/04/add-notebook-pyright-gate.md`):
  that one type-checks the repo-root `notebooks/`; this one catches runtime errors in
  `book/docs/notebooks/`.
- **Ordering:** the gate waited for the Vector2 rename fix, archived 2026-08-29, after which all 14
  book notebooks executed clean.

## What changed

`nb_execution_raise_on_error = True` was added to `book/docs/conf.py`; `docs.sh`'s `set -eu` already
propagated the failure, so it needed no change.

## Verification

Both halves proven with nested `make docs` (`--cgroups=disabled`): **positive** — the clean build (all
14 notebooks) exited 0 with no `*.err.log`; **negative** — a deliberately broken import in `rotate.py`
made myst-nb raise `ExecutionError`, `make html` failed with `Error 2`, and the build exited 2 (the
break was reverted).
