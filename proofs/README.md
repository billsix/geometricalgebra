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
- **What's here** (30 modules under `GacalcProofs/`, grouped; every file is 𝒢₂+𝒢₃ unless noted):
  - *Algebras:* `G1.lean` (𝒢₁ for teaching: `I² = +1`, commutative, every vector pair parallel so
    `u v = u·v`), `G2.lean`, `G3.lean` — coordinate structs; product/wedge/reverse (𝒢₃'s transcribed
    verbatim from gacalc's `Gn` oracle by `tools/derive_lean_algebra.py`), the basis blades as genuine
    elements with their multiplication table, `I² = −1`, `dot` (the scalar part of the product),
    `dual = A·I⁻¹`, `normSq`/`magnitude`, the grade predicates `IsVector`/`IsBivector`/`IsTrivector`;
    `Lagrange.lean` (the real-number Lagrange identity 2D/3D); `AlgebraLaws.lean` (associativity,
    two-sided distributivity, identity, scalar laws, ⊥ vectors anticommute); `GradeProjection.lean`
    (`rVectorPart`/`evenPart`/`oddPart`, idempotent + complete); `Contractions.lean` (Taylor's left/right
    contraction, grade 0 included, vs Hestenes — 𝒢₃).
  - *Angles and trig:* `Rotation2D.lean` (2D from sin/cos: the product enacts rotation one-sided by the
    full-angle `fullAngleRotor`, unit-vector product = that rotor of the angle; the half-angle `rotor`
    sandwich `R v R̃`, proven equal to the one-sided form and to gacalc's inverse sandwich); `Trig.lean` (`cos_between`/`sin_between`,
    `cos² + sin² = 1`, both preserved by the sandwich); `TrigEquiv.lean` (angle-form equivalences, signed
    sine in 2D); `StudentTrigForms.lean` (the student-facing cosine/sine corollaries of the dot/wedge facts).
  - *Versors and rotation:* `Versor2D.lean` / `Rotation3D.lean` (angle-free versor from two vectors:
    bisector `h`, `R = b·a + |a||b|`, `R·a = |a|·h`); `Sandwich.lean` (`inverse`, `sandwich`,
    `IsEvenVersor` (even, any magnitude) and `IsRotor` (unit versor: `R⁻¹ = R̃`, so `sandwich R v = R v R̃`);
    `R R̃ = |R|²·1`; the reverse-sandwich scalings of dot/normSq/wedge for ANY multivector;
    the sandwich is an isometry — dot, length, wedge, hence angles; carries `a` to `b`; fixes its own
    plane bivector and normal; rotations compose by multiplying versors; reverse is an anti-automorphism;
    blade inverses); `RotateComponents.lean` (the three matrix-free rotation goals for the a→b rotation);
    `Exp.lean` (the closed-form bivector exponential is a rotor, `IsRotor`); `Rotor.lean` (the versor chain
    re-done with the reverse sandwich: `rotorFromVectors = normalize ∘ versorFromVectors` is a rotor, the
    bridge `(R/|R|) v (R/|R|)~ = R v R⁻¹` for every `R`, hence the rotor sandwich = `projRotation`, carries
    `a` to `b`, isometry; Lagrange gives `|versorFromVectors a b|² = 2|a||b|(|a||b| + a·b)`; 2D coda: the
    from-vectors rotor of two unit directions IS the half-angle `rotor θ`).
  - *Projection, rejection, reflection:* `Projection2D.lean` / `Projection3D.lean` (Hestenes
    `proj`/`reject`/`project_onto` of a vector onto a vector or (3D) a bivector; rejection ⊥; the wedge
    sees only the rejection; `project + reject = id`; `proj_plane = project_onto`); `Reflect.lean`
    (`reflectVec = 2·proj − v`, an isometry — 𝒢₃, across a vector); `Normalize.lean` (unit magnitude).
  - *Standard position (the non-circular bootstrap):* `StandardPosition.lean` (elementary plane
    rotations `rotXY`/`rotXZ`, NOT versors; preserve dot; proj/reject equivariant; align `b` to `e₁`;
    the product from projection; `projectSP`/`rejectSP` = Python `project_sp`/`reject_sp` — align, keep the
    x-component, unalign — proven equal to `proj`/`reject`); `CrossStandardPosition.lean` (`rotYZ`, `reduceToPlane`, cross
    equivariance, the reduced-frame evaluations); `ProjectionRotation3D.lean` / `ProjectionRotation2D.lean`
    (`projRotation` = Python `transforms.projection_rotation`: carries from→to, ⊥ fixed, isometry, and
    equals the versor sandwich).
  - *Cross, measures, predicates:* `Cross.lean` (`cross = dual (a∧b)`, anticommutative, ⊥ both,
    scalar triple = signed volume — 𝒢₃); `Measures.lean` (area/volume, `|a∧b|²` Lagrange form,
    `|a∧b∧c|² = signedVolume²`); `Predicates2D.lean` / `Predicates3D.lean` (dual ⊥; `a·b = 0 ⟺ ab = a∧b`;
    `a ∧ (k·a) = 0`).
  - *Bridges to Mathlib:* `MathlibBridge.lean` — the from-scratch objects ARE the standard ones: `dot` is
    `inner` on `EuclideanSpace` (so `real_inner_comm` and Cauchy–Schwarz apply: `abs_dot_le_magnitude_mul`),
    the wedge is the `2×2` determinant / the three minors, the dual of the 3D wedge is `crossProduct`, the
    signed volume is `Matrix.det`, and `rot θ` (and the 2D rotor sandwich) is `Orientation.rotation θ` on ℂ (`toC` reads a 𝒢₂ vector's `c1`/`c2`).
  The basis blades are modelled as algebra *elements* (as in Mathlib `CliffordAlgebra` / pygae lean-ga),
  not real fields — see `tasks/reference/lean-for-gacalc.md`. What each Python method maps to, and what
  is NOT covered (general grades, general n, `frame.py`, the transform factories), is in
  `tasks/reference/lean-ga-proof-architecture.md` (coverage map) and the review
  `tasks/reference/lean-proof-corpus-review-2026-10-04.md`.
- **What's planned:** a dimension-general algebra, with the general pseudoscalar sign and Hestenes
  dot/wedge (`tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`, deferred); the general multivector
  inverse; the 3D rotor angle theorem (`tasks/lean-rotor-3d-angle-theorem.md`); frames
  (`tasks/lean-frame-coverage.md`, parked); the Lean→notebook pipeline. The original program
  (`tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`) is complete.

Beginner orientation to Lean and how proofs/reuse work:
`tasks/reference/lean-for-gacalc.md`.
