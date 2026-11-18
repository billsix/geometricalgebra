# Frame peel inverse: reconsider head-first, remove the use-before-binding closures, revise the shared recursion rule

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)
**Follows:** `tasks/archive/2026/11/18/frame-inverse-head-first-recursion.md`

## Outcome

`Frame.to_invertible_function` (`src/gacalc/frame.py`) now reads top to bottom. Its peel inverse is
tail-first again, as it was before the head-first experiment.

1. **No closure reads a name bound later** (commit `cd73128`).
   - `backward_by_reciprocal` and `backward_by_peel` take their precomputed vectors as a first
     parameter.
   - The `match inverse_method:` binds them with `functools.partial(…, self.reciprocal_vectors())`
     / `functools.partial(…, self.orthogonal_vectors())`.

   The pattern dated from the `inverse_method` keyword (`3f70ba3`, 2026-11-07), not from the
   head-first change.
2. **The peel is tail-first again.** It walks the frame's own orthogonal set with
   `case [*earlier, (w, v)]`: solve the last coordinate, subtract its term, recurse on the rest. This
   is back-substitution against QR's `R`, and it mirrors the Lean `invPeel`. The function is now
   byte-for-byte the pre-experiment code (`116e638~1`) except for the `functools.partial` binding.
   The docstring's steps, worked example and "order is forced" paragraph are restored, and the
   Lean-mismatch sentence is gone.
3. **Docs in this repo:**
   - `tasks/reference/frames-qr-and-reciprocal-frames.md`: the peel section, the face-normal and
     line-to-line passages are restored. "Why the order is last-first" records the head-first round
     trip and why it was reverted (the second orthogonal set existed nowhere else; the reversal was
     moved, not removed; Lean no longer matched).
   - `CLAUDE.md`: the `frame.py` line says the peel starts from the last vector again.
4. **The shared rule, softened in github.com/billsix/runClaudeInContainer and runCrushInContainer
   (staged, not committed):**
   - `tasks/reference/recursive-design.md` is now "Handle the head first when the data is in that
     order — a preference, not a mandate". Tail-first is right when the construction makes the last
     element solvable (back-substitution, a stack). Don't build the data reversed just to start at
     the head. The frame is the counter-example. It was re-copied byte-for-byte over both runCrush
     copies.
   - Matching clauses are in both shared `CLAUDE.md` files.
   - Separately, the same session added the "a nested function reads only names bound before it;
     bind later data with `functools.partial`" rule to `python-coding-standard.md` and both
     `CLAUDE.md` files. The maintainer committed and pushed that.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. Peel order: revert to tail-first, for the code that reads best.
2. Use-before-binding: `functools.partial`, done first and committed on its own.
3. Shared rule: soften, with the frame as the counter-example.

## Assessment that drove decision 1

The head-first version made the recursion nicer but the data worse:
- it needed a second orthogonal set found nowhere else (not `Frame`, the book, this repo's reference
  doc, or Lean);
- building it by reversing, orthogonalizing and reversing back is the reversal moved into the data,
  the same thing the rule said "does not count";
- it broke the correspondence with the Lean `invPeel`.

Results and cost were the same either way.

## Verification

- ruff and `ty check` were clean on `frame.py`.
- The `frame.py` doctests passed, as did `tests/test_frame.py`, `tests/test_frame_svd.py` and the fast
  `tests/test_frame_class.py` cases (98 passed).
- All five peel cases of `tests/test_frame_class.py`, including the slow symbolic 3D round trips and
  reciprocal equals peel, passed (7 min 27 s).
- Step 1's `partial` version had passed all seven slow cases (26 min 46 s) before the order change.
