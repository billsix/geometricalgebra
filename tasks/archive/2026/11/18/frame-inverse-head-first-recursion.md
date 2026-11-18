# Can `Frame.to_invertible_function`'s inverse recurse head-first instead of peeling from the end?

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Priority:** 7
**Difficulty:** 4
**Created:** 2026-11-06 (William Emerison Six <billsix@gmail.com>): "I want to know if 'peel' or
whatever really has to start at the end. I'd like the recursion to go forwards if it can …"

## Outcome

It can, and it now does. The peel inverse (`InverseMethod.PEEL`) uses the head-first match
`case [(u, v), *later]`. It reads the first coordinate, subtracts that term, and recurses on the
rest. What forced the old last-first order was the orthogonal set, not orthogonality itself:
- built first-to-last (`w_j ⟂ v_i` for `i < j`), only the last `w_k` isolates a coordinate;
- the peel now uses the frame **orthogonalized from its last vector**, where `u_i` is `v_i` with
  `v_{i+1} … v_k` rejected out (`reversed(make_orthogonal_frame(vectors[::-1]))`), so `u_1`
  isolates `x_1`.

Results are unchanged, since a frame's coordinates are unique.

- **`src/gacalc/frame.py`:** `backward_by_peel` recurses head-first. The second set is computed once
  inside `to_invertible_function` (decision 3), so `Frame.orthogonal_vectors()` and its first-to-last
  conventions are untouched. The docstring's steps and worked example are rewritten for the new
  order. In the example, `u_1 = 9/5 * e_1 − 3/5 * e_2` reads `x_1 = 1`.
- **`tasks/reference/frames-qr-and-reciprocal-frames.md`:** "The peel inverse, step by step" is
  rewritten for the new order, with the face-normal and line-to-line passages updated. It records
  why the 2026-11-04 objections to a head-first form no longer apply:
  - the stored set keeps its order;
  - the peel needs one orthogonalization either way.
- **`CLAUDE.md`:** the module-layout line for `frame.py` describes the peel.
- **Shared recursion guidance (plan step 5), staged and not committed, in two other repos:**
  - github.com/billsix/runClaudeInContainer: `tasks/reference/recursive-design.md` gained "Handle the
    head first — a strong preference", with this frame as the worked example. The shared `CLAUDE.md`
    recursion rule gained a head-first clause.
  - runCrushInContainer: the same doc re-copied over both of its copies, which were byte-identical to
    the canonical, and the same clause added to the Crush `CLAUDE.md`.

## Decisions

1. (A) or (B): both, with (B), the reciprocal frame, as the default (William Emerison Six
   <billsix@gmail.com>, 2026-11-07; done in
   `tasks/archive/2026/11/07/frame-to-invertible-function-reciprocal-inverse.md`).
2. Keep the peel as a second method: yes (same request).
3. Under (A), compute the second orthogonal set inside `to_invertible_function` (2026-11-18).

## Judgment call: the peel was rewritten, not duplicated

Decision 2 kept "the tail-first peel" as the `PEEL` method beside the reciprocal default. This task
then asked whether that peel could go head-first, and decision 3 answered how. The peel was therefore
rewritten head-first rather than added as a third `InverseMethod`. The tail-first form is still
explained in the reference doc, as what the frame's own orthogonal set forces. If you want both
peels selectable, a third enum member would restore the old one.

## Left as is: the Lean model

`proofs/GacalcProofs/ReciprocalFrame2D.lean` / `ReciprocalFrame3D.lean` define `invPeel` peeling from
the last vector. The theorems (`invPeel_frameMap`, `invReciprocal_eq_invPeel`) are still true of the
Python result because coordinates are unique, but Lean's construction no longer mirrors the Python
steps. The docstring and the reference doc say so. Re-modelling `invPeel` head-first belongs with the
parked Lean frame work (`tasks/lean-frame-class-invertible-function.md`).

## Verification

- ruff and `ty check` were clean on `frame.py`.
- `src/gacalc/frame.py` doctests passed, as did `tests/test_frame.py` and `tests/test_frame_svd.py`.
- Every `tests/test_frame_class.py` case that uses the peel passed (5, slow symbolic 3D included,
  7 min 50 s): the round trips and reciprocal equals peel.
- The non-peel cases of that file were unaffected; the final gate reruns the fast suite.
