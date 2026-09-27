# Lean proof — rotation from scratch (sin/cos → geometric product → dot & wedge)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** the scaffolded `proofs/` project (done) — nothing else; this is the foundation the
dot/wedge step-tasks build on.
**Next:** `tasks/lean-proof-dot-product.md`, `tasks/lean-proof-wedge-product.md`
**Archive-coupled with:** `tasks/rename-rotor-to-versor.md` (DONE but held) — the maintainer wants both
archived together so the final squash deletes the rename's adhoc codemods in one step; they share the
"a rotor is really a unit versor" thread. Don't archive this until it too is complete.

**Status:** in-progress — 2D core + the general-vector "from a to b" framing landed 2026-09-28
(`proofs/GacalcProofs/Rotation.lean`, `make lean` green); the sandwich/rotor-composition story, the
Mathlib-rotation *equivalence* proof, and the 3D version remain
**Priority:** 7
**Difficulty:** 8

## BLUF

Formalize, in Lean 4, the book's foundational derivation: **define sine/cosine (from geometry),
define rotation as "from the direction of vec 1 to vec 2, magnitudes irrelevant", derive the
geometric product from rotation, and obtain the dot and wedge as its symmetric/antisymmetric parts**
— for 2D first, then 3D. "Done" = a Lean development that builds these definitions from scratch (not
by citing the general Mathlib theorem) with `make lean` green, and a proof that the from-scratch
result is **equivalent to the general case** (Mathlib's rotation/inner-product machinery). This is
the hardest and most foundational proof; the other proof step-tasks reuse its geometric product.

## Context — read first

- Read `tasks/reference/lean-for-gacalc.md` (Lean orientation + the `proofs/` layout) and
  `tasks/reference/book-outline.md` §C/§E/§F (the rotation → geometric-product → projection spine the
  proof must mirror).
- The dot/wedge-as-parts *conclusion* is already landed in coordinates: `proofs/GacalcProofs/G2.lean`
  defines 𝒢₂ and proves `dot_is_sym_part` / `wedge_is_antisym_part` / `vec_mul`. **What is missing is
  the derivation of the geometric product FROM rotation/trig** — this task supplies that upstream
  half, so the dot/wedge are *derived*, not defined by a hand-written multiplication table.
- Hard parts: this needs real trigonometry (Mathlib `Real.cos`/`Real.sin`, angle-addition) and a
  choice of how to model rotation and the algebra in Lean. Decide the representation early (extend
  the `G2` structure with a rotation operator, vs. work in `Mathlib`'s `Complex`/`EuclideanSpace`/
  `CliffordAlgebra` and map back). Reference existing Lean rotation/GA proofs (Mathlib's
  `Complex`/`Real.Angle`, `pygae/lean-ga`) and learn from them — but keep the proof standalone.

## Progress (2026-09-28) — 2D core landed in `proofs/GacalcProofs/Rotation.lean`

The 2D representation choice is settled: rotation acts on `ℝ × ℝ` (the geometric, pre-algebra
definition), the algebra is the from-scratch `GacalcProofs.G2`, and Mathlib supplies only the trig
lemmas (`cos_add`/`sin_add`/`cos_sub`/`sin_sub`/`cos_sq_add_sin_sq`). Landed and `make lean`-green:

- `rot θ` (rotation from sin/cos), `rot_add` (rotations compose by adding angles), `rot_normSq`
  (rotation preserves magnitude).
- `rotor θ = cos θ + sin θ·e₁e₂`, and `vec_mul_rotor` — **the geometric product enacts rotation**
  (right-multiplying a vector by the rotor rotates it).
- `uvec_mul_uvec` — **the geometric product of two unit vectors is the rotor of the angle between
  them** (the geometric product *derived from rotation*), and `uvec_dot`/`uvec_wedge` reading off
  dot = cos, wedge = sin of that angle (ties to `G2`'s dot=symmetric / wedge=antisymmetric part).

## Progress (2026-09-28, later) — general-vector framing + basis-blades-as-elements refactor

Two follow-ups landed the same day, both `make lean`-green:

- **Rotation "from a to b" for general (non-unit) vectors** (the book's exact framing):
  `polar r φ` / `scale c v` (self-contained, no reach for `ℝ × ℝ`'s module instance), `rot_polar`
  (rotating a polar vector adds to its angle, magnitude unchanged), and `rot_from_to`:
  `b = (|b|/|a|) · rot (φb − φa) a`. Plus `rotorFromTo`/`rotorFromTo_carry` — the rotor built from
  two directions carries one to the other (the GA statement of "rotate from a to b").
- **Basis blades are now elements, not just field names.** The maintainer noticed the `G2` struct
  fields were typed `ℝ` as if `e₁` were a real. Fixed in `G2.lean`: the fields are honest coordinate
  *coefficients* (`s`/`c1`/`c2`/`c12 : ℝ`), and the basis blades are genuine elements
  `one`/`e_1`/`e_2`/`e_12 : G2` with the GA multiplication table (`e_1_sq`, `e_1_mul_e_2`,
  `e_2_mul_e_1`, `e_12_sq`) and `eq_smul_basis`. `Rotation.lean`'s `rotor`/`uvec` are now linear
  combinations of those elements (`cos θ · 1 + sin θ · e₁e₂`, `cos α · e₁ + sin α · e₂`), not raw
  tuples; `uvec_eq_vec` bridges back to `G2.vec`. See the Resolved decisions below and the citation.

## Plan (remaining)

- [x] 2D representation choice; `rot` + basic props; product enacts rotation; product of unit vectors
      = rotor of the angle; dot/wedge read off. (Landed — see Progress.)
- [x] Rotation "from a to b" for general (non-unit) vectors: `b = |b|/|a| · rot θ a` where θ is the
      angle from a to b (magnitudes scale, direction rotates) — the book's exact framing.
      (Landed 2026-09-28: `polar`/`scale`/`rot_polar`/`rot_from_to`, plus `rotorFromTo_carry`.)
- [ ] The rotor sandwich / rotor composition story (optional for 2D; needed to generalize to 3D).
      **Design settled in analysis (2026-09-28), one open naming Q:** gacalc rotates with the
      *inverse* sandwich `R v R⁻¹` (versor conjugation, scale-invariant), not the textbook `R v R̃`
      (which needs a unit rotor); both agree when `R` is unit. gacalc's "rotor" is really an
      un-normalized even **versor** — keep the name (recommended) or rename to versor (Q1). Suggested
      Lean statements (sandwich norm-preserving, scale-invariant, `R⁻¹=R̃` for unit R, composition by
      rotor product) are all in `tasks/reference/unit-bivector-and-rotors.md` §6. Discuss before coding.
- [ ] Prove equivalence to the general case (Mathlib's `Real.Angle`/rotation or `Complex` rotation,
      and `@inner` for the dot) — learn from those, keep the construction standalone. (DECIDED
      2026-09-28: keep the construction standalone; Mathlib is mapped in only here, for equivalence.)
- [ ] **3D versor sandwich — sequenced AFTER projection (decided with the maintainer 2026-09-29).**
      Prerequisites, in order: (a) build a from-scratch **`G3`** (shared with the 3D dot/wedge/pseudoscalar
      step-tasks); (b) `tasks/lean-proof-projection.md` — the projection decomposition (vector projection,
      wedge-via-rejection, dual/normal orthogonality, projection-onto-plane = `(c·B)B⁻¹`). Then the 3D
      sandwich is a **corollary**: it fixes the perpendicular (rejection) part and rotates the in-plane
      part, and the in-plane rotation is the already-proved G2 `sandwich_versor`. So the hard rotational
      content is done; 3D only adds "which plane, leave the orthogonal complement fixed."
- [ ] Update `proofs/README.md` when 3D lands.

## Open questions

_(none open — the representation question is resolved below.)_

## Resolved decisions

1. **Representation (resolved 2026-09-28, William Emerison Six <billsix@gmail.com>):** structure-based
   coordinate `G2` (real coefficient fields `s`/`c1`/`c2`/`c12`), NOT Mathlib `CliffordAlgebra`, for
   the standalone construction — mapping to Mathlib only for the *equivalence* direction. Crucially,
   the basis blades are exposed as genuine **elements** `one`/`e_1`/`e_2`/`e_12 : G2` (a basis vector
   is a vector, not a real), with the GA multiplication table proved. This mirrors Mathlib
   `CliffordAlgebra` / pygae `lean-ga`, where a basis vector maps into the algebra via
   `ι Q : M →ₗ[R] CliffordAlgebra Q` (so `ι Q eᵢ : CliffordAlgebra Q` is an algebra element and scalars
   enter via `algebraMap`). Inspiration cited in the `G2.lean` module docstring and
   `tasks/reference/lean-for-gacalc.md`: Wieser & Song, *Formalizing Geometric Algebra in Lean* (2021,
   arXiv:2110.03551).
