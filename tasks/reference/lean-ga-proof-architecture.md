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
- **Inner product `·`:** `dot_comm` (symmetry); **full bilinearity** — `dot_add`/`dot_sub`/`dot_smul`
  in both `_left` and `_right` forms; `dot_vec` (`a·b = a₁b₁+…`); `dot_self_vec_eq_normSq`
  (`a·a = |a|²` — the bridge that reads a `dot a a` hypothesis as the `normSq` primitive).
- **Outer product `∧`:** **full bilinearity** — `wedge_add`/`wedge_sub`/`wedge_smul` in both `_left` and
  `_right` forms; `wedge_antisymm` (`a∧b = −(b∧a)`), `wedge_self_vec` (`a∧a = 0`), `wedge_vec_eq_biv`
  (`a∧b` = the plane-bivector literal in coordinates).
- **The split:** `vec_mul_eq_dot_add_wedge` (`ab = a·b + a∧b`, coordinate-literal form) and its
  arbitrary-vector form `mul_eq_dot_add_wedge` (over the `IsVector` grade-1 predicate, with
  `eq_vec_of_isVector` the bridge to a literal); the orthogonal corollaries `vec_mul_perp` /
  `mul_eq_wedge_of_perp` (`a⊥b ⟹ ab = a∧b`). G2 + G3 (G2's split lives in `Projection2D.lean`, where
  `dot` and `wedge` are both in scope). `IsVector` is closed under the operations used to build a
  rejection: `isVector_vec`, `IsVector.smul`, `IsVector.sub`.
- **Blade inverse (vectors):** `reverse_vec` (`reverse` fixes a vector), `mul_vec_self` (`a a = |a|²·1`),
  and `mul_vec_inverse_self` (`a a⁻¹ = 1` for `|a|² ≠ 0`) — the `B B⁻¹ = 1` identity that turns a
  Hestenes `(…)a⁻¹` proof structural. With these, `plane_eq_wedge` (`a (b − proj_a b) = a∧b`) and
  `reject_vec_eq` (`(b∧a)a⁻¹ = b − proj_a b`) are now structural `rw`-chains on the split, not
  `field_simp` bashes.
- **Magnitude (squared is the primitive):** `normSq_vec` (`|a|² = a₁²+…`), `normSq_wedge_vec`
  (`|a∧b|² = …`), `normSq_evenVersor`, `versorFromVectors_mul_reverse` (`R R̃ = |R|²·1`), `normSq_mul`
  (multiplicative); `magnitude_sq_vec` (`|a|² = a₁²+…` via `normSq_vec` under the `√`). There is **one**
  magnitude concept — `magnitude = √normSq`, all grades; the old vector-only `mag = √(a·a)` was deleted
  and unified into `magnitude` (2026-09-29).
- **Sin/cos & Lagrange** (`Trig.lean`): `lagrange_property` (`(a·b)²+|a∧b|² = |a|²|b|²`),
  `cos_between`/`sin_between`, `cos_sq_add_sin_sq` (`cos²+sin²=1`), and `sandwich_preserves_cos` /
  `sandwich_preserves_sin` — a rotation preserves the cosine AND sine, hence the whole angle,
  coordinate-free (G2 + G3).
- **Sandwich isometry leaves** (`Sandwich.lean`): `sandwich_preserves_dot`; the outermorphism
  `sandwich_preserves_wedge` (`(RuR⁻¹)∧(RvR⁻¹)=R(u∧v)R⁻¹`); `normSq_smul`; the pure-`ring` cores
  `normSq_reverse_sandwich` (`|RvR̃|²=|R|⁴|v|²`) and `normSq_reverse_sandwich_wedge` (grade-2 twin);
  the isometries `sandwich_preserves_normSq_of_vec` (`|RvR⁻¹|²=|v|²`) and
  `sandwich_preserves_normSq_of_wedge` (`|R(u∧v)R⁻¹|²=|u∧v|²`); `magnitude_sandwich_vec`.
- **Duals / pseudoscalar:** `I_inv`, `I_mul_I_inv`, `dual`, `dual_wedge_perp_left`/`_right`.

**Note:** the squared magnitude `normSq_vec` is *the* "|a|²" primitive — "a vector dotted with itself"
is not its own leaf; route it through `normSq` (and phrase nondegeneracy as `normSq (vec a) ≠ 0`).

**Note (versor-hypothesis convention, 2026-09-29):** every sandwich lemma states its nondegeneracy as
`normSq (evenVersor …) ≠ 0` (the versor's squared magnitude — "R is invertible"), **never** the raw
coordinate sum `s²+c12²+… ≠ 0`; the coordinate form is recovered inside a proof only where `field_simp`
needs it (`rw [normSq_evenVersor] at hr`). Likewise the grade-2 isometry leaves are stated on
`wedge (vec u)(vec v)`, not a bivector-coordinate literal. This is the interface half of the
"carry the meaningful quantity, not a coordinate sum" rule.

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
- `magnitude A = √(normSq A)` — the magnitude, correct for **all** grades. This is the **single**
  magnitude concept: the older vector-only `mag = √(A·A)` (wrong sign for a bivector) was deleted and its
  uses folded into `magnitude` (2026-09-29). `normSq`/`magnitude` live in `G2.lean`/`G3.lean` (below the
  algebra, above every consumer).

## Inventory (files in `proofs/GacalcProofs/`, 2026-09-29)

- `Lagrange.lean` — Lagrange identity 2D/3D (`|a|²|b|² = (a·b)² + |a∧b|²`).
- `G2.lean` / `G3.lean` — the algebras: product/wedge/reverse, basis elements, multiplication table,
  `I² = −1`, dot, dual, `I⁻¹`; `normSq`/`magnitude` (+ `normSq_vec`, and `normSq_wedge_vec` in `G3`);
  `G3` also the fundamental identity `ab = a·b + a∧b` (`vec_mul_eq_dot_add_wedge`) and `vec_mul_perp`.
- `AlgebraLaws.lean` — associativity, distributivity, identity, scalar compatibility, `smul_smul`,
  `one_smul`, ⊥-anticommutation, for both algebras.
- `Sandwich.lean` — `inverse`/`sandwich` (`normSq`/`magnitude` moved down to `G2`/`G3`); the sandwich is an isometry
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
