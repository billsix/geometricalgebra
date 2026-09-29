# Lean GA proofs — architecture, techniques, and what's proven

**What this is:** the durable "how it's built" companion to `tasks/reference/lean-for-gacalc.md` (the
beginner orientation). It records the *architecture* of the from-scratch Lean proofs in
`proofs/GacalcProofs/`, the techniques that keep them tractable, and an inventory of what is proven.
Read this before extending the proofs. Updated in place (never archived).

**Status:** written 2026-09-29 (William Emerison Six <billsix@gmail.com>), harvesting the versor /
projection / algebra-law session. `make lean` green.

## The representation (settled)

- Each algebra `G2`/`G3` is a **coordinate struct** (`@[ext]`, one `ℝ` field per basis blade), with the
  basis blades exposed as genuine **elements** (`one`/`e_1`/…), NOT as real fields — a basis vector is
  a vector, not a real. (Inspiration: Mathlib `CliffordAlgebra` / pygae `lean-ga`; Wieser & Song,
  arXiv:2110.03551. See `lean-for-gacalc.md`.)
- **Correct-by-construction product:** `G3`'s `mul`/`wedge`/`reverse` were NOT hand-derived — they were
  emitted by running gacalc's `Gn` oracle on symbolic multivectors and transcribed verbatim. The
  derivation harness is **`tools/derive_lean_algebra.py [n]`** (promoted from an adhoc script; parallels
  `tools/gen_specialized.py`, which generates the *Python* specialized classes). The multiplication-table
  lemmas (`e_1_sq`, anticommutation, `I_sq`) then independently confirm the transcription.

## The key technique: leaf vs structural (the maintainer's "magnitude-squared" insight)

The proofs split into two layers, and keeping the split clean is what makes them short:

- **Leaf lemmas** connect a definition to the 8-field coordinate representation. Proved *once* by
  `ext <;> ring` (or `field_simp`): the multiplication table, `mul_assoc`/distributivity/`smul` laws
  (`AlgebraLaws.lean`), the `dot`/`wedge` bilinearity lemmas, `normSq_evenVersor`, `versorFromVectors_mul_reverse`
  (`R R̃ = normSq·1`), `normSq_mul` (multiplicative). These are the bridge; there is nothing below them.
- **Structural layer** — everything built on the leaves — is **coordinate-free `rw` chains**:
  `inverse` (`R̃/normSq`), `versorFromVectors_mul_inverse` (`R R⁻¹ = 1`), `sandwich_carries_from_to`,
  `sandwich_comp`, `sandwich_add`/`_smul`, `project_eq_sub_reject`, `reject_perp` (both dims).

The **squared magnitude** `normSq = ⟨A Ã⟩` (NOT the `√` magnitude — proofs stay squared to avoid `√`)
and the `dot`/`wedge` **bilinearity lemmas** are what enable this. Concrete example: G2 `reject_perp`
went from a `vec`-form `field_simp` bash to `rw [dot_sub_left, proj, dot_smul_left]; field_simp; ring`
— coordinate-free and general in `a, b`. **Write proofs structurally; let only the leaves touch
coordinates.** (Follow-up audit: `tasks/lean-proofs-make-coordinate-free.md`.)

## Leaf-node index (the coordinate bridge — reuse these, don't re-derive inline)

Every proof should reach for a *named* leaf, not a fresh `ext <;> ring`. The leaves, by category
(2D `G2` + 3D `G3` unless noted):

- **Multiplication table:** `e_1_sq`/`e_2_sq`/`e_3_sq`, `e_1_mul_e_2`/…, `e_2_mul_e_1` (anticommute),
  `e_12_mul_e_3`, `I_sq` (`I² = −1`), `reverse_reverse`.
- **Algebra laws** (`AlgebraLaws.lean`): `mul_assoc`, `mul_add`/`add_mul`, `one_mul`/`mul_one`,
  `smul_mul`/`mul_smul`, `smul_smul`, `one_smul`, `vec_anticomm_perp`.
- **Inner product `·`:** `dot_comm` (symmetry), `dot_sub_left`/`dot_smul_left`/`dot_add_left`
  (bilinearity), `dot_vec` (`a·b = a₁b₁+…`).
- **Outer product `∧`:** `wedge_sub_right`/`wedge_smul_right`/`wedge_sub_left`/`wedge_smul_left`
  (bilinearity), `wedge_antisymm` (`a∧b = −(b∧a)`), `wedge_self_vec` (`a∧a = 0`).
- **The split:** `vec_mul_eq_dot_add_wedge` (`ab = a·b + a∧b`, G3), `vec_mul_perp` (`a⊥b ⟹ ab = a∧b`).
- **Magnitude (squared is the primitive):** `normSq_vec` (`|a|² = a₁²+…`), `normSq_wedge_vec`
  (`|a∧b|² = …`), `normSq_evenVersor`, `versorFromVectors_mul_reverse` (`R R̃ = |R|²·1`), `normSq_mul`
  (multiplicative); `mag_sq_vec`, `magnitude_vec` (bridge `magnitude` ↔ vector-only `mag`).
- **Sin/cos & Lagrange** (`Trig.lean`): `lagrange_property` (`(a·b)²+|a∧b|² = |a|²|b|²`),
  `cos_between`/`sin_between`, `cos_sq_add_sin_sq` (`cos²+sin²=1`), and `sandwich_preserves_cos`
  (a rotation preserves the cosine, hence the angle — coordinate-free).
- **Sandwich isometry leaves** (`Sandwich.lean`): `sandwich_preserves_dot`, `normSq_smul`,
  `normSq_reverse_sandwich` (`|RvR̃|²=|R|⁴|v|²`), `sandwich_preserves_normSq_of_vec` (`|RvR⁻¹|²=|v|²`),
  `magnitude_sandwich_vec`.
- **Duals / pseudoscalar:** `I_inv`, `I_mul_I_inv`, `dual`, `dual_wedge_perp_left`/`_right`.

**Note:** the squared magnitude `normSq_vec` is *the* "|a|²" primitive — "a vector dotted with itself"
is not its own leaf; route it through `normSq` (and phrase nondegeneracy as `normSq (vec a) ≠ 0`).

## Other techniques worth reusing

- **The even-versor bridge.** `versorFromVectors_eq_evenVersor` proves the a→b versor `= evenVersor …`
  (it is even: scalar + bivector). This lets the *general* `evenVersor` results (isometry
  `sandwich_preserves_dot`, `sandwich_fixes_own_bivector`/`_normal`) apply to the *actual* rotation
  `versorFromVectors a b` by instantiation — no re-proof.
- **Literal-then-instantiate, to avoid degree blow-up.** A coordinate proof about `a∧b` blows up
  (`field_simp` cross-multiplies degree-4 denominators → timeout) because `a∧b`'s entries are quadratic
  in `a,b`. Fix: prove the fact for a **literal bivector** `⟨0,0,0,0,p,q,r,0⟩` (free `p,q,r`, low degree),
  then instantiate at `a∧b`. Used in `proj_plane_eq_project_onto` (via `reject_eq_proj_normal`,
  `project_eq_sub_reject`).
- **Matrix-free rotation.** "Rotates the oriented angle correctly" = *oriented isometry*: preserves the
  dot (angle magnitude) AND fixes the plane bivector (orientation). With "carries a→b" that pins the
  rotation — **no rotation matrix, no double angle** needed. (`RotateComponents.lean`.)
- **`field_simp` gotchas.** (1) Provide the nonzero denominator in the form `field_simp` normalizes to
  (usually `^2` sums); it matches up to `ring`-normalization but not always across two different
  denominators — **unify denominators first** (e.g. `dot(dual B)(dual B) = normSq B`) to avoid a
  degree-8 blow-up. (2) `reverse` emits `-0` in negated slots; `simp` won't reduce `√(…-0…) = √(…0…)`,
  so peel with `congr 1; ring`. (3) A `G3`/`G2` algebra-law lemma name (`mul_smul`, `smul_smul`,
  `mul_one`, `one_smul`, `mul_assoc`) **clashes with Mathlib's ℝ version** — fully-qualify the G3/G2 one
  (`GacalcProofs.G3.mul_smul`) in `rw` chains.

## Hestenes projection / rejection (uniform, all grades)

gacalc's `project`/`reject` (base.py; Hestenes & Sobczyk p.18 eqs 2.9) are two formulas, uniform for a
vector or bivector blade `B`:

- `project_B A = (A · B) B⁻¹` — the component of `A` in `B`.
- `reject_B A = (A ∧ B) B⁻¹` — the component of `A` orthogonal to `B`.

Lean status: `proj`/`reject`/`project_onto` cover vector- and bivector-blades in 3D
(`Projection.lean`) and 2D (`Projection2D.lean`); `project_add_reject` (`(A·B)B⁻¹ + (A∧B)B⁻¹ = A`) is
the validating decomposition; `proj_plane_eq_project_onto` shows the normal-based plane projection
equals the Hestenes form. The blade inverse `B⁻¹` is `Sandwich.inverse` (`B̃/(B B̃)`, works for a simple
bivector: `B · inverse B = 1`).

**Terminology (maintainer, 2026-09-29):** the `·` here is **Hestenes' inner product**
`A·B = ⟨AB⟩_{|r−s|}` (defined for all grades in *Clifford Algebra to Geometric Calculus*, 1984) — for a
vector·bivector it is the grade-1 part (`inner_vb`, a vector), NOT the scalar `dot` (grade 0, which is
0 here). It is **not** the "left/right contraction," a later, slightly different notion (Lounesto;
Dorst–Fontijne–Mann); the two coincide for vector·bivector, hence are easy to conflate. gacalc's `<`/`>`
*are* genuine contractions (Taylor 2021) — a separate, intentional part of the library.

## Magnitude (Hestenes)

- `normSq A = ⟨A Ã⟩₀` — the **squared magnitude** `|A|²` (H&S p.13 eq 1.49, gacalc `magnitude_squared`;
  `⟨AÃ⟩ = ⟨ÃA⟩` as the scalar part is symmetric). The workhorse of the versor layer.
- `magnitude A = √(normSq A)` — the magnitude, correct for **all** grades. `mag = √(A·A)` is the older
  vector-only form (wrong sign for a bivector); `magnitude_vec` bridges them on vectors.

## Inventory (files in `proofs/GacalcProofs/`, 2026-09-29)

- `Lagrange.lean` — Lagrange identity 2D/3D (`|a|²|b|² = (a·b)² + |a∧b|²`).
- `G2.lean` / `G3.lean` — the algebras: product/wedge/reverse, basis elements, multiplication table,
  `I² = −1`, dot, dual, `I⁻¹`; `G3` also the fundamental identity `ab = a·b + a∧b` (`vec_mul_eq_dot_add_wedge`)
  and `vec_mul_perp`.
- `AlgebraLaws.lean` — associativity, distributivity, identity, scalar compatibility, `smul_smul`,
  `one_smul`, ⊥-anticommutation, for both algebras.
- `Sandwich.lean` — `normSq`/`magnitude`/`inverse`/`sandwich`; the sandwich is an isometry
  (`sandwich_preserves_dot`, length); fixes its own plane bivector and normal; the versor is invertible
  (`R R̃ = |R|²`, `R R⁻¹ = 1`); rotations compose (`sandwich_comp`); the even-versor bridge.
- `Rotation.lean` (2D angle-parameterized), `Rotation3D.lean` / `Versor2D.lean` (angle-free
  versor-from-vectors: bisector, `R·a = |a|·h`, `b·R = |b|·h`; the carries-a→b capstone
  `R a R⁻¹ = (|a|/|b|)·b`).
- `RotateComponents.lean` — the three matrix-free rotation goals for the actual a→b rotation (in the
  plane, oriented isometry, perpendicular fixed) + `sandwich_ahat` (â↦b̂).
- `Projection.lean` / `Projection2D.lean` — Hestenes `proj`/`reject`/`project_onto`, `project_add_reject`,
  `proj_plane = project_onto`, and the 2D cases.

Remaining (see the umbrella `tasks/investigate-lean-proofs-for-ga.md`): the Mathlib-rotation
*equivalence* proofs, the dot/wedge/pseudoscalar step-tasks' 3D from-rotation derivations.
