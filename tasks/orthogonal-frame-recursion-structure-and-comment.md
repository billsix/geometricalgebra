# Reshape the orthogonal-frame recursion (nil / one / two-or-more / default) and rewrite its comment

**Status:** proposed — needs go-ahead.
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

Reshape the Gram–Schmidt-by-rejection recursion in `make_orthogonal_frame`
(`src/gacalc/frame.py`) so its `match` has the full data-shaped set of cases — **empty list** (base),
**one element**, **two-or-more** (the recursive case), and a **default** — and **rewrite the comment**
so it describes the *operation* standalone, not an invariant that only makes sense once you are
already inside the recursion. Then update the `recursive-design.md` reference doc in
runClaudeInContainer and runCrushInContainer with the lesson. (Maintainer's request, 2026-10-27.)

## Context (cold start)

The inner `orthogonalize` in `make_orthogonal_frame` today matches only two cases
(`frame.py` ~176–194):

```python
match list(remaining):
    case [v, *rest]:
        # Keep v (already orthogonal to every vector finalized before it -- each
        # earlier head was rejected out of it on the way down), reject it out of
        # each remaining vector, and orthogonalize that tail. ...
        rest_orthogonal_to_v = [w.rejected_away_from(v) for w in rest]
        return [v, *orthogonalize(rest_orthogonal_to_v)]
    case _:
        return []   # the empty/base case (wildcard, for ty-exhaustiveness)
```

This follows the house conventions "**prefer total dispatch**" and "**shape recursion to the data**
(nil/cons)" (`~/.claude/reference/recursive-design.md`, gacalc `CLAUDE.md`), but the maintainer wants
the cases spelled to the data and the comment reworded.

## What to do

1. **Four explicit cases** in the `match`:
   - `[]` — **base case**, the empty list → `[]`.
   - `[v]` — **one element**: a single vector is already orthogonal; nothing to reject → `[v]`.
   - `[v, w, *rest]` (**two or more**) — the recursive case: remove the component of each later
     vector that is parallel to `v` (reject `v` out of the rest), then recurse on that tail.
   - `case _:` — **default**: a mandatory-feeling total fallback (keep the ty-exhaustiveness reason
     noted; raise or an explicit commented no-op as fits).
   (Keep it `ty`-exhaustive — that is why the current code uses a wildcard; preserve that property.)
2. **Rewrite the comment** to stand on its own, describing the operation rather than the
   mid-recursion invariant — the maintainer's phrasing: *"remove the components of the rest that are
   parallel to the first vector (reject the first out of the rest), then recursively orthogonalize
   the rest; the first element is already orthogonal to every vector finalized before it."* State the
   operation first; the "already orthogonal to earlier heads" fact is a justification, not the lead.
3. Consider whether `make_orthogonal_frame_hestenes` warrants the same treatment (note it; do it only
   if it reads the same way).
4. Keep gates green: `make test` (incl. `tests/test_frame.py`) and `make format`.

## Follow-up (required, after the code lands)

Update the **recursive-design** reference doc in **both** sandboxes —
`runClaudeInContainer tasks/reference/recursive-design.md` (canonical) and the runCrush mirror
(byte-identical) — with the generalizable lesson: spell the recursion's cases to the data shape
(nil / single / cons-of-two-or-more / default), and **write the per-case comment to describe the
operation standalone**, not an invariant that only parses once you are already inside the recursion.
