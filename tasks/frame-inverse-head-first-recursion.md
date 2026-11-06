# Can `Frame.to_invertible_function`'s inverse recurse head-first instead of peeling from the end?

**Status:** blocked — the maintainer said to hold off until the Hestenes reciprocal frame is defined
(William Emerison Six <billsix@gmail.com>, 2026-11-06)
**Blocked on:** `tasks/reciprocal-frame-hestenes.md` being done (itself on hold), so that option (B)
below, the reciprocal-frame map, is available to weigh against (A).
**Recheck:** `ls tasks/reciprocal-frame-hestenes.md` fails (the task was archived) and
`grep -n 'def reciprocal_frame' src/gacalc/frame.py` finds it. Both mean cleared.
**Priority:** 8 (blocked)
**Difficulty:** 4
**Created:** 2026-11-06 (William Emerison Six <billsix@gmail.com>): "I want to know if 'peel' or
whatever really has to start at the end. I'd like the recursion to go forwards if it can. Given that we
are dealing with orthogonal components anyway for the algorithm, I wouldn't think order matters, and I
prefer processing the first element in a recursion first, rather than starting at the tail."
**Depends on:** `tasks/archive/2026/11/06/refactor-frame-to-invertible-function.md` (it moves `peel` inside `backward`;
do this task against that shape).

## BLUF

The inverse map `backward` solves `y = Σ x_i * v_i` for the coordinates with `peel`, which recurses
from the **last** frame vector (`case [*earlier, (w, v)]`). The maintainer strongly prefers recursion
that handles the **first** element first (`case [head, *tail]`). Find out whether the inverse can be
written that way, pick a form, and implement it with no change in results. Done = `backward` recurses
head-first (or this doc records why it cannot), `make test` and `make format` pass, and, **if it
works**, the shared recursion guidance states head-first as a strong preference (last plan step).

## Context (read first)

- **The code:** `Frame.to_invertible_function` in `src/gacalc/frame.py`; `peel` inside `backward`.
  The docstring's "The order is forced" paragraph states the current reasoning.
- **The math:** `tasks/reference/frames-qr-and-reciprocal-frames.md` ("The peel inverse, step by
  step"; "The relation to Hestenes' reciprocal frame").
- **The orthogonal set:** `Frame.orthogonal_vectors` is `make_orthogonal_frame(vectors)`, which
  keeps the head and rejects it out of everything after it (head-first already).
- **Recursion guidance to follow:** the `recursive-design.md` reference doc (nil/cons, map over the
  tail; github.com/billsix/runClaudeInContainer `tasks/reference/`).

## Initial analysis (agent, 2026-11-06 — to verify, not yet tested)

**Why the order matters today.** The `w_j` are orthogonal to *each other*, but `y` is built from the
`v_i`, which are not. Because the frame is orthogonalized head-first, `w_j` is perpendicular to the
frame vectors **before** it (`w_j · v_i = 0` for `i < j`) but in general **not** to those after it.
So `w_1 · y = Σ_i x_i * (w_1 · v_i)` mixes every coordinate, while `w_k · y = x_k * |w_k|²` isolates
the last one. With *these* `w_j`, only the last coordinate can be read off alone, which is why `peel`
starts at the end. The order is a property of how the `w_j` were built, not of orthogonality itself.

**Ways to recurse forwards anyway:**

- **(A) Orthogonalize from the other end.** Build a second orthogonal set `u_j` in which each `u_j` is
  `v_j` with every **later** frame vector rejected out (`u_1 ⟂ v_2 … v_k`). Then
  `x_1 = (u_1 · y) / |u_1|²`, subtract `x_1 * v_1`, and recurse on the tail: a true head-first
  nil/cons recursion. The set can likely be had from the existing function as
  `reversed(make_orthogonal_frame(reversed(vectors)))`, so nothing new is written. Cost: a second
  orthogonalization when the map is built (`Frame` stores only the head-first `w_j`; decide whether to
  compute it in `to_invertible_function` or store it on `Frame`).
- **(B) Use the reciprocal frame, and drop the recursion.** With the reciprocal vectors `vⁱ`
  (`vⁱ · v_j = δⁱ_j`), each coordinate is independent: `x_i = vⁱ · y`. The inverse becomes a plain
  **map** over the frame, which `recursive-design.md` ranks above any hand-written recursion. This is
  the on-hold `tasks/reciprocal-frame-hestenes.md`.
- **(C) Keep the tail-first math but spell it head-first over a reversed list.** Rejected up front:
  it is the same recursion with the list reversed, so it changes only the appearance.

## Plan

1. Verify the analysis: a small symbolic 2D/3D check that `w_1 · y` mixes coordinates, and that the
   (A) set `u_j` isolates `x_1` (`u_1 · v_j = 0` for `j > 1`, `u_1 · v_1 = |u_1|²`).
2. Settle the open questions, then implement the chosen form in `backward`, keeping the existing
   exact-quotient behaviour (`_exact_quotient`), symbolic results, and the docstring's worked example
   (rewritten for the new order).
3. Update the docstring ("The order is forced" paragraph) and
   `tasks/reference/frames-qr-and-reciprocal-frames.md`.
4. Gates: `make test`, `make format`, `python tools/check_annotations.py`. Behaviour must be
   identical: `tests/test_frame_class.py` round trips (`f.inverse(f(x)) == x`) pass unchanged.
5. **If head-first works** (A or B is adopted): update the shared recursion guidance to state that
   head-first recursion (`[head, *tail]`, handle the first element first) is a **strong preference**,
   and that when an algorithm seems to need the tail first, the fix to look for is reordering the
   *construction* of its data (as in (A)) so the head can be processed first, before settling for a
   tail-first recursion. Edit `recursive-design.md` in github.com/billsix/runClaudeInContainer
   (canonical) and copy it over its two runCrushInContainer copies (`tasks/reference/` and the baked
   `client/entrypoint/dotfiles/.config/crush/reference/`; note the baked copy has drifted from the
   canonical as of 2026-11-06, so the re-copy also brings it up to date). Add one short clause to the
   "Prefer a named recursion scheme" section of both shared `CLAUDE.md` files
   (runClaudeInContainer `entrypoint/dotfiles/.claude/CLAUDE.md`, runCrushInContainer
   `client/entrypoint/dotfiles/.config/crush/CLAUDE.md`). It is a portable rule, so not the personal
   overlay. Stage by path in both repos.

## Open questions

1. **(A) or (B)?** (A) keeps a recursion, now head-first, and is self-contained. (B) removes the
   recursion entirely and uses the reciprocal frame, which this task now waits for. Decide once the
   reciprocal frame exists and both can be compared on real code.
2. **Under (A), where does the second orthogonal set live?** Computed inside `to_invertible_function`
   (no new public surface), or stored on `Frame` beside `orthogonal_vectors` (visible, costs every
   `Frame` an extra orthogonalization)? Recommended: compute it inside `to_invertible_function`.
3. **Keep the current tail-first peel as a documented alternative?** gacalc keeps parallel
   formulations side by side for teaching (the three orthogonalizations). Recommended: no; replace it,
   and keep the explanation of why the head-first `w_j` force tail-first order in the reference doc.
