# Lean proofs for the reciprocal frame and `Frame`'s two inverses

**Status:** in progress (2026-11-07) — the maintainer asked for it, answered its open question, and said to
start. The 𝒢₂ theorems 1–8 are drafted in `proofs/GacalcProofs/ReciprocalFrame2D.lean` (not yet in
`GacalcProofs.lean`, and **not yet built**: the local image had no Lean; a `USE_LEAN=1` image was building
with `--network=host`). Next: build it with `make lean` (add the import), fix what fails, then 𝒢₃.
**Priority:** 6
**Difficulty:** 6
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>)
**Overlaps:** `tasks/lean-frame-class-invertible-function.md` (on hold since 2026-11-04; its theorems 1,
5 and 6 are needed here) and `tasks/lean-frame-coverage.md` (parked 2026-10-04; rejection Gram–Schmidt
and linear independence).

## BLUF

Machine-check, in `proofs/GacalcProofs/`, the results of the 2026-11-07 frame work for 𝒢₂ and 𝒢₃: the
reciprocal frame (H&S p. 28 eqs 3.5–3.7), the similar-triangles reading of a coordinate, and that both
inverses of `Frame.to_invertible_function` (`"reciprocal"` and `"peel"`) undo the forward map and agree.
Done = the theorems below build under `make lean` with no `sorry`, and each Python docstring or test that
states the fact cites its Lean theorem by name.

## Context

- The Python: `src/gacalc/frame.py` (`kronecker_delta`, `all_wedged_except_the_kth`, `reciprocal_frame`,
  `Frame.reciprocal_vectors`, `Frame.to_invertible_function(inverse_method=…)`); tests in
  `tests/test_frame.py` and `tests/test_frame_class.py` (the symbolic statements to mirror).
- The math: `tasks/reference/frames-qr-and-reciprocal-frames.md`, sections "The relation to Hestenes'
  reciprocal frame", "Why one dot product reads off an oblique coordinate: similar right triangles", and
  "The peel inverse, step by step".
- Build records: `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`,
  `tasks/archive/2026/11/07/frame-to-invertible-function-reciprocal-inverse.md`,
  `tasks/archive/2026/11/07/kronecker-delta-function.md`.
- Lean style and existing pieces: `tasks/reference/lean-ga-proof-architecture.md`,
  `tasks/reference/lean-for-gacalc.md`, CLAUDE.md "Coordinates only when needed" (vectors in with
  `IsVector` hypotheses, coordinates only inside proofs). Available: `G2.lean`/`G3.lean` (`mul`, `wedge`,
  `dot`, `normSq`, `inverse`), `Projection3D.lean` (`reject`, `reject_perp_dot`, `project_add_reject`
  against a bivector, `dual_wedge_perp_*_dot`), `Cross.lean` (`signedVolume`).
- The graded `prefix_blades` seed fix (`tasks/archive/2026/11/07/frame-prefix-blades-graded-zero-seed.md`)
  is about Python's graded types and has no Lean counterpart.

## Theorems (frame `a_1 … a_n`, `n = 2` in G2 and `n = 3` in G3, with "wedge of all ≠ 0" as the frame hypothesis)

1. **Definition** of the reciprocal vectors from eq 3.7, `a^k = (−1)^(k−1) * (face_k) * A_n⁻¹`, with
   `face_k` the wedge of all but `a_k` (Python's `all_wedged_except_the_kth`).
2. **Pure vector:** each `a^k` satisfies `IsVector`.
3. **Eq 3.5:** `dot (a^k) (a_j) = if k = j then 1 else 0` for every `k`, `j` (the Kronecker delta; state it
   as the nine/four equalities, or as a function on `Fin n`, whichever the house style prefers).
4. **Reconstruction:** for a vector `y`, `y = Σ_k (a^k · y) * a_k`.
5. **Similar triangles:** for a vector `m` perpendicular to every frame vector but `a_i` (with
   `m · a_i ≠ 0`), and `y = Σ_j x_j * a_j`, `x_i = (m · y) / (m · a_i)`; and `a^i = m / (m · a_i)` for
   any such `m`. This is the doc's step 3–4 argument, stated without picking a unit normal.
6. **Last reciprocal is the last rejection:** `a^n = w_n / |w_n|²`, with `w_n` the rejection of `a_n`
   from the span of the others (in G3, `reject` from the bivector `a_1 ∧ a_2`).
7. **Round trips, both methods:** with `f(x) = Σ_i (x · e_i) * a_i`, `g_reciprocal(y) = Σ_i (a^i · y) * e_i`,
   and `g_peel` the back-substitution, `g (f x) = x` and `f (g y) = y` for all vectors, for each `g`.
8. **The two inverses agree:** `g_reciprocal y = g_peel y` for every vector `y` (a corollary of 7, or
   directly from 3 and 6).

## Plan

1. Prove rejection orthogonality (`w_n` perpendicular to every earlier frame vector) first; theorems 6–8 rest on it.
2. G2 first: the face is a single vector and `A_2⁻¹` is a pseudoscalar, so theorems 1–8 are short and
   show the proof shape. Then G3.
3. Cite each theorem by name in the Python docstrings and tests listed in Context.
4. Add the coverage rows the architecture reference keeps.

**Not in scope** (the maintainer asked for Lean only): the prose + LaTeX book page that CLAUDE.md's
three-forms rule calls for. The symbolic Python form exists as the tests above. The book page would go
in `book/docs/frames-qr.rst`.

## Decisions

1. **Scope against the on-hold Lean frame task** (William Emerison Six <billsix@gmail.com>, 2026-11-07:
   "sure"). Theorems 6–8 need the peel, and the peel needs rejection orthogonality. This task proves
   that result itself (theorem 1 of `tasks/lean-frame-class-invertible-function.md`) and takes over that
   task's theorems 5 (round trip) and 6 (last reciprocal), which are theorems 7 and 6 here. That task's
   theorems 2–4 (triangular coefficients, rebuild, volume) stay on hold there, and
   `tasks/lean-frame-coverage.md` stays parked.

## Open questions

None.
