# Lean equivalents of `Frame` and its `InvertibleFunction`

**Status:** on hold — the maintainer said "hold off on that for now" about open question 1 (William Emerison Six <billsix@gmail.com>, 2026-11-04)
**Priority:** 8 (on hold)
**Difficulty:** 6
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>). This is the follow-up the maintainer
asked for once the sympy version worked ("If it works symbolically in python now, then make a follow up
task to make lean equivalent versions"). The Python side is in `src/gacalc/frame.py` `Frame`, and the
design record is `tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md`.
**Moved out (2026-11-07):** theorems 1, 5 and 6 are now proved by
`tasks/lean-reciprocal-frame-and-frame-inverses.md` (the maintainer's decision there); theorems 2–4 remain
here, on hold.
**Overlaps:** `tasks/lean-frame-coverage.md` (Lean coverage of the rest of `frame.py`: linear
independence, rejection Gram–Schmidt, and the Hestenes closed form; parked by the maintainer
2026-10-04). This task needs that one's rejection-orthogonality result, so do that part first or
together. Whether this task un-parks it is the maintainer's call.

## BLUF

Machine-check, in `proofs/GacalcProofs/`, the facts the Python `Frame` relies on and its tests check
symbolically, for 𝒢₂ and 𝒢₃ (`G2`/`G3`), in the house style of CLAUDE.md "Coordinates only when
needed" (vectors in, scalars only in the proof body). Done = the theorems below build under
`make lean` with no `sorry`, each cited from the matching Python docstring or test.

## Context (read first)

- `tasks/reference/frames-qr-and-reciprocal-frames.md`: the math, and why the frame is stored orthogonal
  (`w_j`, coefficients `(w_j · v_i) / |w_j|²`) rather than orthonormal.
- `tasks/reference/lean-ga-proof-architecture.md` and `tasks/reference/lean-for-gacalc.md`: proof
  architecture, the object-in/scalars-in-the-body style, the teaching order of the `G2`/`G3` files.
- `tests/test_frame_class.py`: the symbolic statements to mirror.
- `proofs/GacalcProofs/StandardPosition.lean`: existing `project`/`reject` results to reuse.

## Theorems (for 𝒢₂ and 𝒢₃, frame `v_1 … v_n`, `n = 2, 3`, independence as a hypothesis)

1. **Orthogonality:** the rejection orthogonalization gives `w_i · w_j = 0` for `i ≠ j`. Shared with
   `lean-frame-coverage.md`.
2. **Triangular coefficients:** `(w_j · v_i) = 0` for `j > i`, and `(w_i · v_i) = |w_i|²`, so the
   coefficient table is triangular with a unit diagonal.
3. **Rebuild:** `v_i = Σ_j ((w_j · v_i) / |w_j|²) * w_j`, which is what `iter(frame)` computes.
4. **Volume:** `|w_i|² * |A_{i-1}|² = |A_i|²` with `A_i = v_1 ∧ … ∧ v_i`, hence
   `Π |w_i|² = |v_1 ∧ … ∧ v_n|²`.
5. **Round trip:** with `f(x) = Σ (x · e_i) * v_i` and `g` the back-substitution inverse,
   `g (f x) = x` and `f (g y) = y` for all vectors `x`, `y`. This is the Lean form of the maintainer's
   `(f⁻¹ ∘ f)(x) == x` requirement.
6. **Last reciprocal:** `(w_n / |w_n|²) · v_j = δ_{nj}`.

## Plan

1. Decide with the maintainer whether `lean-frame-coverage.md` is un-parked first (theorem 1 lives
   there), or theorem 1 is proved here.
2. State the 𝒢₂ versions, then 𝒢₃. In 𝒢₂ the back-substitution is two steps and could be stated
   concretely; in 𝒢₃ keep the same shape.
3. Cite each theorem by name from the Python `Frame` docstring and `tests/test_frame_class.py`.
4. Per CLAUDE.md's three-forms rule, the prose + LaTeX book page remains open; the notebooks task
   (`tasks/archive/2026/11/04/frame-notebooks-epix.md`) left it as a `TODO prose` comment in
   `book/docs/frames-qr.rst`, which is its home.

## Open questions

1. Un-park `tasks/lean-frame-coverage.md` together with this task, or keep that one parked and prove
   theorem 1 here? I recommend proving it here: it is the only part this task needs, and it keeps the
   parked task's other items parked. **On hold (William Emerison Six <billsix@gmail.com>, 2026-11-04): "hold off on that for now".**
