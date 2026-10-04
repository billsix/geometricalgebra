# gacalc Lean proofs

Machine-checked proofs of the mathematics behind gacalc's geometric-algebra
derivations, in **Lean 4** on **Mathlib**. These are an independent check of the
*math* (a second oracle alongside the Python test suite) — they do **not** verify
the Python implementation.

- **Build + verify:** `make lean` from the repo root (runs `proofs/check.sh` in the
  container: `lake build` + a completeness gate that fails on any `sorry`/`admit` in the
  sources). Needs an image built with `USE_LEAN=1` (the default full image).
- **Toolchain / deps:** pinned in `lean-toolchain` (Lean `v4.34.1`) and
  `lake-manifest.json` (the exact Mathlib revision). `.lake/` is build output +
  the fetched Mathlib — gitignored, never committed.
- **What's here** (27 modules under `GacalcProofs/`, grouped; every file is 𝒢₂+𝒢₃ unless noted):
  - *Algebras:* `G2.lean`, `G3.lean` — coordinate structs; product/wedge/reverse (𝒢₃'s transcribed
    verbatim from gacalc's `Gn` oracle by `tools/derive_lean_algebra.py`), the basis blades as genuine
    elements with their multiplication table, `I² = −1`, `dot` (the scalar part of the product),
    `dual = A·I⁻¹`, `normSq`/`magnitude`, the grade predicates `IsVector`/`IsBivector`/`IsTrivector`;
    `Lagrange.lean` (the real-number Lagrange identity 2D/3D); `AlgebraLaws.lean` (associativity,
    two-sided distributivity, identity, scalar laws, ⊥ vectors anticommute); `GradeProjection.lean`
    (`rVectorPart`/`evenPart`/`oddPart`, idempotent + complete); `Contractions.lean` (Taylor's left/right
    contraction, grade 0 included, vs Hestenes — 𝒢₃).
  - *Angles and trig:* `Rotation2D.lean` (2D from sin/cos: the product enacts rotation, unit-vector
    product = rotor of the angle, half-angle versor `R v R̃`); `Trig.lean` (`cos_between`/`sin_between`,
    `cos² + sin² = 1`, both preserved by the sandwich); `TrigEquiv.lean` (angle-form equivalences, signed
    sine in 2D); `StudentTrigForms.lean` (the student-facing cosine/sine corollaries of the dot/wedge facts).
  - *Versors and rotation:* `Versor2D.lean` / `Rotation3D.lean` (angle-free versor from two vectors:
    bisector `h`, `R = b·a + |a||b|`, `R·a = |a|·h`); `Sandwich.lean` (`inverse`, `sandwich`,
    `IsEvenVersor`; `R R̃ = |R|²·1`; the reverse-sandwich scalings of dot/normSq/wedge for ANY multivector;
    the sandwich is an isometry — dot, length, wedge, hence angles; carries `a` to `b`; fixes its own
    plane bivector and normal; rotations compose by multiplying versors; reverse is an anti-automorphism;
    blade inverses); `RotateComponents.lean` (the three matrix-free rotation goals for the a→b rotation);
    `Exp.lean` (the closed-form bivector exponential is a unit even versor).
  - *Projection, rejection, reflection:* `Projection2D.lean` / `Projection3D.lean` (Hestenes
    `proj`/`reject`/`project_onto` of a vector onto a vector or (3D) a bivector; rejection ⊥; the wedge
    sees only the rejection; `project + reject = id`; `proj_plane = project_onto`); `Reflect.lean`
    (`reflectVec = 2·proj − v`, an isometry — 𝒢₃, across a vector); `Normalize.lean` (unit magnitude).
  - *Standard position (the non-circular bootstrap):* `StandardPosition.lean` (elementary plane
    rotations `rotXY`/`rotXZ`, NOT versors; preserve dot; proj/reject equivariant; align `b` to `e₁`;
    the product from projection); `CrossStandardPosition.lean` (`rotYZ`, `reduceToPlane`, cross
    equivariance, the reduced-frame evaluations); `ProjectionRotation3D.lean` / `ProjectionRotation2D.lean`
    (`projRotation` = Python `transforms.projection_rotation`: carries from→to, ⊥ fixed, isometry, and
    equals the versor sandwich).
  - *Cross, measures, predicates:* `Cross.lean` (`cross = dual (a∧b)`, anticommutative, ⊥ both,
    scalar triple = signed volume — 𝒢₃); `Measures.lean` (area/volume, `|a∧b|²` Lagrange form,
    `|a∧b∧c|² = signedVolume²`); `Predicates2D.lean` / `Predicates3D.lean` (dual ⊥; `a·b = 0 ⟺ ab = a∧b`;
    `a ∧ (k·a) = 0`).
  The basis blades are modelled as algebra *elements* (as in Mathlib `CliffordAlgebra` / pygae lean-ga),
  not real fields — see `tasks/reference/lean-for-gacalc.md`. What each Python method maps to, and what
  is NOT covered (general grades, general n, `frame.py`, the transform factories), is in
  `tasks/reference/lean-ga-proof-architecture.md` (coverage map) and the review
  `tasks/reference/lean-proof-corpus-review-2026-10-04.md`.
- **What's planned:** the equivalence of the from-scratch results to Mathlib's rotation/`@inner`
  machinery and the general pseudoscalar sign (step-tasks under
  `tasks/investigate-lean-proofs-for-ga.md`); extending coverage to `transforms`, `standardposition`,
  `frame`, `functions`, `g1`/`gn` (`tasks/lean-coverage-extend-transforms-frame-gn.md`); general-grade
  products and a dimension-general algebra (`tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`).

Beginner orientation to Lean and how proofs/reuse work:
`tasks/reference/lean-for-gacalc.md`.
