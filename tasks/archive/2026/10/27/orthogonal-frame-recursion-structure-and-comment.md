# Reshape the orthogonal-frame recursion (nil / one / two-or-more / default) and rewrite its comment

**Status:** DONE 2026-10-27 (William Emerison Six <billsix@gmail.com>). Ready to archive after the
work commit.
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-10-27 **Updated:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

`make_orthogonal_frame`'s inner `orthogonalize` recursion (`src/gacalc/frame.py`) was reshaped so
every list shape is its own `match` case — `[]` (base), `[v]` (one), `[v, *rest]` (two or more), and
a total `case _` default — and its per-case comments rewritten to describe the **operation** rather
than an invariant that only parses once you are already inside the recursion. Behavior is unchanged
(same algorithm, Modified Gram–Schmidt by rejection). Gates green: ruff + ty clean, `test_frame.py`
17 passed.

## What was done

- **Four data-shaped cases.** The old form had only `case [v, *rest]` plus a wildcard standing in for
  the base. Now `[]` returns `[]` (base — nothing to orthogonalize), `[v]` returns `[v]` (a single
  vector is already an orthogonal frame on its own), and `[v, *rest]` is the two-or-more recursive
  case. `case _` stays as the **total default**: it is unreachable (the three shapes cover every
  list), but `ty` does not prove list-pattern exhaustiveness, so the match needs an explicit
  catch-all — which also honours the "prefer total dispatch" convention.
- **Operation-first comment.** The recursive case now reads "remove from each later vector its
  component parallel to the first (reject the first out of the rest), keep the first, and recurse on
  the rest"; the first-is-already-orthogonal-to-every-earlier-head fact is a trailing justification,
  not the lead.
- **`make_orthogonal_frame_hestenes` left alone** — it is a `pairwise(prefix_blades(...))`
  list-comprehension (the closed-form blade product), not a recursion with a `match`, so the
  treatment does not apply.

## Follow-up (done)

The generalizable lesson was folded into the shared `recursive-design.md` reference doc in **both**
sandboxes (`runClaudeInContainer` canonical + byte-identical `runCrushInContainer` mirror): spell
each data shape its own case (`[]` / `[v]` / `[v, *rest]`), keep `case _` as the total default rather
than overloading it to mean the base case, and write each per-case comment to describe the operation
standalone. That doc already carried this frame example as a worked case, so its AFTER block and
type-checker note were updated to the refined form (the earlier revision used `case _` as the base
case itself).
