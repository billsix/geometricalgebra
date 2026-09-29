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
  part, wedge = antisymmetric part, pseudoscalar I₂² = −1, the basis blades as
  genuine elements `one`/`e_1`/`e_2`/`e_12 : G2` with their multiplication table, and
  the dual `A·I₂⁻¹` with `dual_vec_perp`: the dual of a vector is ⊥ the vector),
  `GacalcProofs/G3.lean` (a from-scratch 𝒢₃, the 8-dim algebra: geometric product +
  wedge + reverse — transcribed from gacalc's `Gn` oracle — the eight basis elements
  `one`/`e_1`/…/`e_123 : G3`, the multiplication table, pseudoscalar I₃² = −1, the fundamental
  identity `a b = a·b + a∧b` for vectors and its `a ⊥ b ⟹ a b = a∧b` corollary; the shared
  prerequisite for the 3D proofs), `GacalcProofs/AlgebraLaws.lean` (the associative-unital-ℝ-algebra
  laws for both 𝒢₂ and 𝒢₃: the product is associative, distributes over addition both sides, `one`
  is a two-sided identity, scalars pull through, and orthogonal vectors anticommute),
  `GacalcProofs/Sandwich.lean` (the versor sandwich `R v R⁻¹` by an even versor, in 𝒢₂ and 𝒢₃: it is
  an isometry — preserves the dot product, hence lengths and angles; the from-vectors versor is
  invertible (`R R̃ = |R|²`, `R R⁻¹ = 1`) and **carries `a` to `b`**, `R a R⁻¹ = (|a|/|b|)·b`,
  angle-free; in 3D a plane rotation fixes the orthogonal axis and keeps in-plane vectors in-plane;
  and rotations **compose by multiplying versors**, `sandwich (R₁R₂) v = sandwich R₁ (sandwich R₂ v)`,
  with the supporting `reverse_mul`/`normSq_mul`/`inverse_mul`; and for the actual a→b rotation:
  it keeps its plane oriented, fixes the perpendicular axis, and preserves the dot product — an
  oriented isometry carrying a→b, in `GacalcProofs/RotateComponents.lean`),
  `GacalcProofs/Versor2D.lean` (the angle-free versor-from-two-vectors construction in 𝒢₂: the
  bisector `h`, the versor `R = b·a + |a||b|`, `R·a = |a|·h`, and the carries-`a`-to-`b` capstone — the
  pedagogical twin of the 3D `Rotation3D.lean`), `GacalcProofs/Projection.lean` (3D projection: vector
  projection with the rejection ⊥ the vector, the wedge sees only the rejection, and the
  dual of `a∧b` — the plane normal — is ⊥ both spanning vectors; plus the uniform Hestenes rejection
  `reject_B A = (A∧B)·B⁻¹`, proved to equal `b − proj_a b` for the vector case),
  `GacalcProofs/Rotation3D.lean` (the **angle-free** 3D versor built from two vectors, à la
  `versor_from_vectors`: the half-angle bisector vector `h = |b|·a + |a|·b`, the half-angle versor
  `R = b·a + |a||b|`, and `versor_mul_from_eq_bisector` — `R·a = |a|·h`, the versor times the
  from-vector recovers the scaled bisector, with no trig), and
  `GacalcProofs/Rotation.lean` (2D: rotation from sin/cos; the geometric product
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
