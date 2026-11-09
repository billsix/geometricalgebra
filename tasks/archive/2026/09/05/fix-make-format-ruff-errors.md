# Fix `make format` ruff errors (5 from the Odd_3 work + 1 pre-existing)

**Created:** 2026-09-05 · **Completed:** 2026-09-05

## The problem

`make format` was red with 6 ruff errors (E501 ×5, T201 ×1) while `ty check src/tests/tools` was
clean. Five came from the just-merged Odd_3 work (`tasks/archive/2026/09/05/model-odd-graded-type.md`),
whose verify harness ran `ty` + `pytest` + the notebook but not ruff; the sixth was a pre-existing
E501 in an old ad-hoc codemod.

## What changed

- **`src/gacalc/base.py`** (the `sandwich` docstring, 96 > 88) and **`tests/test_odd3.py`** (three
  docstring lines, 89–91 > 88): the docstring paragraphs were reflowed to ≤ 88. The `test_odd3.py`
  docstring's stale reference to the then-just-archived Odd_3 task path was dropped, keeping the
  durable `graded-subspaces-vs-subalgebras.md` reference.
- **`notebooks/displaygraded.py`** T201: `print(error)` in the cast-raise demo cell became
  `display(Markdown(f"raises \`ValueError\`: {error}"))`, matching the notebook's display style
  (T201 is in the repo-wide `select` with no notebook exemption, and this was the only notebook using
  `print`). Rejected: a `# noqa: T201`, or a notebooks-wide T201 per-file-ignore (a config decision
  only if notebooks should print freely).
- **The pre-existing E501** (a 101-column path in the docstring of the `drop-graded-type-dimension-suffixes`
  Vector2→Vector codemod): resolved by **excluding `tasks/adhoc/` from ruff** via `extend-exclude` in
  `pyproject.toml`, with a comment that ad-hoc scripts are transient task-scoped artifacts, not policed
  source — fixing the class rather than the line. Rejected: a `# noqa: E501`, or `git rm` of the codemod.

## Verification

`make format` green (ruff + `ty` clean). Process lesson: `make format` is the real gate; run it before
calling generated-typing work done.
