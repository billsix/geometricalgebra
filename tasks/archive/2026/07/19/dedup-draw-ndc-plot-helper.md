# Consider folding `draw_ndc` into the shared triangle helper

**Status:** **CLOSED — decided against, 2026-07-19.** Investigated with the criteria
this task set out; `draw_ndc` should stay a separate function in both repos.
**Created:** 2026-07-18

## Context

`src/gacalc/nbplotutils.py` had four near-identical ~58-line `draw_*` plot helpers. Three
of them (`draw_isoceles_triangle`, `draw_right_triangle`, `draw_second_right_triangle`,
91-93% identical) were unified on 2026-07-18 into `_draw_labelled_triangle(...)` plus
three ~10-line callers — **net -75 lines**, with all six rendered figures verified
**pixel-identical** before and after.

**`draw_ndc` was left out on purpose.** At 60 lines it is ~85% similar to the others —
close enough to be tempting, different enough that folding it in risks a parameter list
that does too much. `draw_screen` (17% similar) is genuinely a different function and is
not a candidate at all.

## What to check before doing it

1. **Diff `draw_ndc` against `_draw_labelled_triangle` and enumerate every difference.**
   The three-way unification needed exactly four knobs: two vertex expressions, the label
   strings, and a label-offset x sign. If `draw_ndc` needs more than one or two *further*
   parameters, the shared function is becoming a configuration object and the duplication
   is the cheaper cost.
2. **Is `draw_ndc` conceptually the same picture?** It draws normalized-device-coordinate
   space, not a labelled triangle. Sharing an implementation between things that merely
   *look* alike is how a helper ends up with mutually exclusive flags.
3. Check whether any notebook or book chapter excerpts it, since these helpers are
   teaching-facing.

## Gate (the one that matters)

Not the test suite — **the rendered pixels**. Render every affected plot to PNG before
and after and compare with `PIL.ImageChops.difference(...).getbbox() is None`.

**Two things this method got wrong the first time, both now fixed in the recipe:**

1. **Save INSIDE the `with create_graphs()` block.** It calls `plt.close()` on exit, so a
   `plt.savefig()` afterwards writes a fresh blank canvas. Use
   `with create_graphs() as ax: ...; ax.figure.savefig(path, dpi=70)`.
2. **Sanity-check the baseline is non-blank before trusting any comparison** (count
   non-white pixels). Blank-vs-blank compares equal and reports success, which is how the
   first round of "pixel-identical" results were meaningless.

Reconstruct the "before" mechanically -- `git stash` for uncommitted work, or
`git show <commit>^:path` for committed -- never by hand-editing a copy back.

Also run the full suite (`286 passed` at time of writing) and `ty check src`.

## Conclusion: do NOT fold it in (2026-07-19)

Evaluated against this task's own criteria while `nbplotutils.py` was open in both repos.
It fails them:

- **72% similar** to `_draw_labelled_triangle`, against **91-93%** for the three
  triangles that *were* unified. That gap is the whole signal: the triangles were the
  same picture with different numbers; this is not.
- **It is a square, not a triangle.** Folding it in forces a rename to
  `_draw_labelled_polygon` -- the helper stops naming a *thing* and starts naming a
  *mechanism*, which is a real loss in teaching code.
- **It needs a `facecolor` parameter** solely because it is the one unfilled outline. A
  flag that exists to serve exactly one caller is the "configuration object" smell this
  task warned about.
- **Its purpose differs.** `draw_ndc` shows what normalized device coordinates *are*;
  the triangle helpers draw a labelled shape under a transform. Same code shape, different
  job.

Gain would have been ~44 lines per repo. Not worth a more general helper serving one
conceptually different caller.

**What was done instead (worth more than the dedup):** the investigation found a real bug.
`draw_ndc` mislabelled a corner -- the vertex at **(1,-1)** was annotated **"(-1,1)"**, so
that coordinate never appeared and "(-1,1)" appeared twice. Present identically in both
repos; fixed in both. Verified by rendering the figure before and after: the only pixel
change is a 12x9 region at that one label, and the two repos' diffs match exactly.

**Also corrected: the verification method itself.** The earlier "all figures
pixel-identical" claims for the triangle dedups were **vacuous** -- `create_graphs()`
calls `plt.close()` on exit, so saving the figure *after* the `with` block captured a
blank canvas, and blank was being compared to blank. **Save inside the block**
(`with create_graphs() as ax: ...; ax.figure.savefig(...)`), and sanity-check that the
baseline is non-blank before trusting any comparison. Both dedups were re-verified this
way and are genuinely behaviour-preserving (5/6 and 6/7 identical, the sole difference
being the intended label fix).
