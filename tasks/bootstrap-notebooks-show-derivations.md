# Part III notebooks: each derivation worked with set values and live ePiX plots

**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-16, on branch `quarter-turn-and-bootstrap-notebooks`
**Related:** `tasks/bare-2d-bootstrap-pages.md` (the Part III pages; open);
`tasks/archive/2026/11/16/bootstrap-dot-wedge-from-proj-rej.md` (where the request came up);
github.com/billsix/epix-mirror `tasks/figure-fit-to-points.md` (the follow-on there; proposed)

## What was done

The six Part III companion notebooks, `book/docs/notebooks/bootstrap-*.py`, used to check each
result by subtracting two sides and printing a list such as `[0, 0]`. They were rewritten as
worked examples:

- **A values cell** near the top sets the vectors, or the vector and angle in Step 1. Every
  notebook uses `a = 2 * e_1 + 1 * e_2`, `b = 1 * e_1 + 2 * e_2`, `v = -1 * e_1 + 2 * e_2`, and
  Step 1 uses `θ = π/3`. With these, the cosine and sine of the angle from `a` to `b` are exactly
  `4/5` and `3/5`, `|a| * |b| = 5`, and the sandwich's `R = 9 − 3 * e₁₂`. The intro says once that
  a reader can change the values and rerun.
- **Each derivation step** is computed from the values, shown as output, and drawn live with
  ePiX: 13 figures across the six notebooks.
  - The new helper `book/figures/epix/_bootstrap_live.py` re-exports `_frame_scene`'s primitives
    and adds `scene_around`. It sizes a figure from the points it has to show, at a fixed
    3.4 in width with equal scales, so changed values still frame.
  - Step 3's second triangle draws only `v`, its two parts and `v'`, not `a` or `b`.
- **Checks** sit beside what they check. Each cell subtracts two things and shows one result,
  `0`. Each notebook first checks the set values, then has a "For all vectors" section that
  repeats the checks with symbolic coordinates, still one fact per cell. The `zeros()` helper,
  the result lists and the `assert`s are gone.
- **Pages:** each `bootstrap-*.rst` page's companion-notebook sentence now describes the worked
  example.
- **Style rule:** recorded in `tasks/reference/book-outline.md` ("Structural conventions"), with a
  pointer in `CLAUDE.md`'s book section.
- **Tool fix:** `tools/check_epix_keywords.py` now exempts `min` and `max`, which are
  positional-only builtins like `len` and `sorted`. Before, it reported them as unknown callees
  in the new helper and failed `make format`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-16)

- **Plots are ePiX, drawn live**, not matplotlib.
- **Checks sit beside what they check, one result per cell.** A check uses the plotted values or
  symbolic ones. There is no closing section of checks.
- **The page keeps its LaTeX derivation.** The notebook repeats the steps with numbers and
  pictures.
- **One shared set of values** across the six steps, left to the implementer. The values above
  were chosen because they give exact rational results.
- **Scope:** Part III only.

How the request was reached is in
`tasks/archive/2026/11/16/bootstrap-dot-wedge-from-proj-rej.md` ("How it went", item 8).

## Not done

- **A fitting figure in epix itself.** `epix.figure()` takes only fixed bounds, which is why
  `scene_around` exists here. Adding a fitting figure to epix, then bumping `EPIX_COMMIT` and
  swapping `scene_around` over to it, is filed as github.com/billsix/epix-mirror
  `tasks/figure-fit-to-points.md`. It was outside this task's go-ahead.
- **Label placement uses fixed offsets.** Labels were placed for the set values. Very different
  values can make a label overlap a line. The pictures stay correct; only the labels may need a
  nudge.

## Verification

- Every notebook was executed cell by cell with `nbclient` in the container. Every check cell
  output `0`, and the 13 figures were inspected. Three were adjusted:
  - Step 2's `x * e₁` label sat on its line;
  - Step 3's second-triangle labels collided;
  - θ labels moved closer to their angles.
- `make format`: green (ruff, ty over `book/docs/notebooks`, `check_epix_keywords`).
  `tools/check_annotations.py` reports nothing for the notebooks or the helper.
- `make docs` (its `podman run` line): green.
  - All six notebooks executed under myst-nb with no errors.
  - No undefined references in the final LaTeX log, and no Sphinx warnings for Part III.
  - The rendered HTML notebook pages carry the 13 figures, and each check cell renders as a
    single `0`.
