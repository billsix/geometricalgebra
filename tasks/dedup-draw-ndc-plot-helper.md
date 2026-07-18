# Consider folding `draw_ndc` into the shared triangle helper

**Status:** proposed — deliberately deferred by Bill 2026-07-18 ("leave it as is for now")
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
and after and compare with `PIL.ImageChops.difference(...).getbbox() is None`. That is
how the three-way dedup was verified, and it is the only check that catches a plot
silently shifting. A recipe exists in this session's history: render under
`matplotlib.use("Agg")` inside `create_graphs()`, save at fixed dpi, compare per file.

Also run the full suite (`286 passed` at time of writing) and `ty check src`.

## Recommendation

Low priority. The big win is already taken; this is one 60-line function. Do it only if
someone is already editing `nbplotutils.py` and finds the near-duplication in the way.
