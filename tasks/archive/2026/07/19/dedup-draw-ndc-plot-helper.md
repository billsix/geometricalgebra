# Consider folding `draw_ndc` into the shared triangle helper

**Created:** 2026-07-18 · **Completed:** 2026-07-19 (closed: decided against)

## Background

`src/gacalc/nbplotutils.py` had four near-identical ~58-line `draw_*` plot helpers. Three
of them (`draw_isoceles_triangle`, `draw_right_triangle`, `draw_second_right_triangle`,
91-93% identical) were unified on 2026-07-18 into `_draw_labelled_triangle(...)` plus
three ~10-line callers, **net -75 lines**.

`draw_ndc` was left out of that unification on purpose: at 60 lines it was ~85% similar to
the others, close enough to be tempting but different enough that folding it in risked a
parameter list that did too much. `draw_screen` (17% similar) was a different function and
never a candidate.

## Criteria used

1. **Diff `draw_ndc` against `_draw_labelled_triangle` and enumerate every difference.** The
   three-way unification needed exactly four knobs (two vertex expressions, the label strings,
   a label-offset x sign). More than one or two *further* parameters would make the shared
   function a configuration object, and the duplication the cheaper cost.
2. **Is `draw_ndc` conceptually the same picture?** Sharing an implementation between things
   that merely *look* alike is how a helper ends up with mutually exclusive flags.
3. Whether any notebook or book chapter excerpts it, since these helpers are teaching-facing.

## Conclusion: not folded in (2026-07-19)

Evaluated against those criteria with `nbplotutils.py` open in both repos (gacalc and
github.com/billsix/modelviewprojection), it failed them:

- **72% similar** to `_draw_labelled_triangle`, against **91-93%** for the three triangles that
  were unified. The triangles were the same picture with different numbers; this was not.
- **It is a square, not a triangle.** Folding it in would have forced a rename to
  `_draw_labelled_polygon`, so the helper would name a *mechanism* instead of a *thing*, a loss
  in teaching code.
- **It would need a `facecolor` parameter** solely because it is the one unfilled outline: a
  flag serving exactly one caller, the "configuration object" smell from criterion 1.
- **Its purpose differs.** `draw_ndc` shows what normalized device coordinates *are*; the
  triangle helpers draw a labelled shape under a transform.

The gain would have been ~44 lines per repo, not worth a more general helper serving one
conceptually different caller.

## What was done instead

- **A labelling bug was found and fixed in both repos.** `draw_ndc` annotated the vertex at
  **(1,-1)** as **"(-1,1)"**, so that coordinate never appeared and "(-1,1)" appeared twice.
  Rendering before and after showed the only pixel change was a 12x9 region at that label, and
  the two repos' diffs matched exactly.
- **The verification method was corrected.** The earlier "all figures pixel-identical" claims
  for the triangle dedups were **vacuous**: `create_graphs()` calls `plt.close()` on exit, so
  saving the figure *after* the `with` block captured a blank canvas, and blank was compared to
  blank. Both dedups were re-verified the correct way and were behaviour-preserving (5/6 and
  6/7 identical, the sole difference being the intended label fix).

## Verification method

The gate was **the rendered pixels**, not the test suite: every affected plot was rendered to
PNG before and after and compared with `PIL.ImageChops.difference(...).getbbox() is None`.

- **Save inside the `with create_graphs()` block**:
  `with create_graphs() as ax: ...; ax.figure.savefig(path, dpi=70)`.
- **Sanity-check that the baseline is non-blank** (count non-white pixels) before trusting any
  comparison; blank-vs-blank compares equal and reports success.
- The "before" was reconstructed mechanically (`git stash` for uncommitted work,
  `git show <commit>^:path` for committed), never by hand-editing a copy back.

The full suite (`286 passed`) and `ty check src` were also run.
