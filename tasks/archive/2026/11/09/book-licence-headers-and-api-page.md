# Book: GFDL headers on every page, `api.rst` coverage, the "turned graph paper" wording

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §3.6

## What changed

- **Licence headers:** the GFDL-1.3 comment block, identical on the 12 pages that had it, was
  prepended to the other 20 `book/docs/*.rst` pages (`api.rst` and `index.rst` included).
  `grep -Li "free documentation" book/docs/*.rst` now prints nothing.
- **`api.rst`** documents `gacalc.standardposition` (cited by `proof-projection`) and
  `gacalc.nbplotutils`. The generated `g1`–`g5` stay out, as before.
- **`rotation-graph-paper.rst`:** "a rotation is **deformed graph paper**" became "**turned graph
  paper**" (a rotation is rigid), and the title is Title Case: "Rotation Is Turning the Graph Paper".
- Already fixed, so dropped: `proof-cross` hangs off `projection-rejection-3d.rst`'s toctree.

## Verification

`make docs`: HTML and PDF built. Sphinx reports 3 and 1 warnings, all older and unrelated to this
change: the `Frame.to_invertible_function` docstring's `InvertibleFunction` cross-reference matches two
targets.
