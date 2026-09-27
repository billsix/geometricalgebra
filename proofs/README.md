# gacalc Lean proofs

Machine-checked proofs of the mathematics behind gacalc's geometric-algebra
derivations, in **Lean 4** on **Mathlib**. These are an independent check of the
*math* (a second oracle alongside the Python test suite) — they do **not** verify
the Python implementation.

- **Build + verify:** `make lean` from the repo root (runs `proofs/check.sh` in the
  container: `lake build` + an axioms gate that fails on any incomplete `sorry`
  proof). Needs an image built with `USE_LEAN=1` (the default full image).
- **Toolchain / deps:** pinned in `lean-toolchain` (Lean `v4.34.1`) and
  `lake-manifest.json` (the exact Mathlib revision). `.lake/` is build output +
  the fetched Mathlib — gitignored, never committed.
- **What's here:** `GacalcProofs/Lagrange.lean` (Lagrange identity, 2D + 3D),
  `GacalcProofs/G2.lean` (a from-scratch 𝒢₂: geometric product, dot = symmetric
  part, wedge = antisymmetric part, pseudoscalar I₂² = −1, and the basis blades as
  genuine elements `one`/`e_1`/`e_2`/`e_12 : G2` with their multiplication table),
  and `GacalcProofs/Rotation.lean` (2D: rotation from sin/cos; the geometric product
  enacts rotation and the product of two unit vectors is the rotor of the angle
  between them — dot = cos, wedge = sin; plus rotation "from a to b" for general
  vectors, `b = (|b|/|a|)·rot(φb−φa)a`). The basis blades are modelled as algebra
  *elements* (as in Mathlib `CliffordAlgebra` / pygae lean-ga), not real fields —
  see `tasks/reference/lean-for-gacalc.md`.
- **What's planned:** the 3D versions, the rotor sandwich / composition, the
  equivalence to Mathlib's rotation/`@inner`, the general pseudoscalar sign, and
  projection correctness — tracked as step-tasks under
  `tasks/investigate-lean-proofs-for-ga.md`.

Beginner orientation to Lean and how proofs/reuse work:
`tasks/reference/lean-for-gacalc.md`.
