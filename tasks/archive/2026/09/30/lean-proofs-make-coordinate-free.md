# Lean proofs — made coordinate-free via a leaf/structural property algebra

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** the proof layer in `proofs/GacalcProofs/` — `AlgebraLaws.lean` (assoc, distributivity,
`one_mul`/`mul_one`, `smul_mul`/`mul_smul`/`smul_smul`/`one_smul`, ⊥-anticommutation) and the
`normSq`/`inverse`/`magnitude` abstractions (`Sandwich.lean`).

**Status:** done (2026-09-30, William Emerison Six <billsix@gmail.com>) — ready for the pre-squash tense
rewrite (this doc) and archival. `make lean` green throughout.
**Priority:** 7
**Difficulty:** 5

## BLUF

An audit + refactor: given the algebra-law, bilinearity, and magnitude(-squared) abstractions, the goal
was to re-prove as many coordinate proofs (`ext <;> ring` / `field_simp`) as cleanly reduced into short
structural `rw` chains, and to record which proofs *must* stay coordinate-based — the "leaf" lemmas that
connect an abstraction to the 8-field representation. The maintainer's steer was to treat the inner
product `·` and outer product `∧` as leaf nodes carrying algebraic properties (including the sine/cosine
characterization) and rebuild the higher geometric theorems on those properties. The outcome: a full
inner/outer *property algebra* of leaves, the flagship "a rotation preserves the whole angle" proved
coordinate-free, the tractable coordinate bashes converted to structural chains, and the leaf/structural
split recorded. Detail lives in git and in `tasks/reference/lean-ga-proof-architecture.md`.

## The two layers (the organizing idea)

- **Leaf lemmas** connect a definition to the coordinate representation (`normSq_evenVersor`, the
  multiplication table, `mul_assoc`/distributivity, the `dot`/`wedge` bilinearity lemmas, `normSq_vec`,
  `dot_vec`, …). Proved once by `ext <;> ring`; they are the bridge and correctly stay coordinate-proved
  — there is nothing below them.
- **Structural layer** is everything built on the leaves, via `rw` chains — coordinate-free at the call
  site.

## What was done

**Inner/outer property-algebra leaves (G2 + G3):**
- Symmetry / antisymmetry: `dot_comm` (`a·b = b·a`), `wedge_antisymm` (`a∧b = −(b∧a)`).
- **Full bilinearity:** `dot` and `wedge` distribute over `add`/`sub`/`smul` on **both** `_left` and
  `_right` (the missing right-side `dot_*`, the `wedge_add_*`, and G2 `wedge_sub_left` were added).
- **The fundamental split, general form:** an `IsVector` predicate (grade-1: the scalar/bivector/
  pseudoscalar parts vanish — there is no vector subtype in the structs) with `eq_vec_of_isVector` (the
  bridge to a coordinate literal), then `mul_eq_dot_add_wedge` (`a b = a·b + a∧b` for arbitrary grade-1
  `a, b`) and its corollary `mul_eq_wedge_of_perp` (`a·b = 0 ⟹ a b = a∧b`). This was the master rewrite
  turning a vector geometric product into inner + outer, coordinate-free. `IsVector` is closed under
  `smul`/`sub`/`vec` (`isVector_vec`, `IsVector.smul`, `IsVector.sub`). G2's split lives in
  `Projection2D.lean`, where both `dot` and `wedge` are in scope.
- **Lagrange as a property** and the **sin/cos characterization:** `lagrange_property`
  (`(a·b)² + |a∧b|² = |a|²|b|²`), `cos_between`/`sin_between`, and `cos_sq_add_sin_sq` (`cos²+sin²=1`, a
  corollary of Lagrange), in `Trig.lean`.

**Flagship — a rotation preserves the whole angle (cos AND sin), coordinate-free (G2 + G3):**
- `sandwich_preserves_cos` (`cos(RuR⁻¹, RvR⁻¹) = cos(u,v)`), from `sandwich_preserves_dot` (numerator) +
  `magnitude_sandwich_vec` (denominators). The magnitude leaf `sandwich_preserves_normSq_of_vec`
  (`|RvR⁻¹|²=|v|²`) went structural — the direct `field_simp` choked on the `|R|⁴` denominator — by
  factoring the inverse's scalar (`mul_smul`), `normSq_smul`, the pure-polynomial `|RvR̃|²=|R|⁴|v|²`
  (`normSq_reverse_sandwich`), then cancelling `(1/|R|²)²·|R|⁴ = 1`.
- `sandwich_preserves_sin` (`sin(RuR⁻¹, RvR⁻¹) = sin(u,v)`), built on the **outermorphism leaf**
  `sandwich_preserves_wedge` (`(RuR⁻¹)∧(RvR⁻¹) = R(u∧v)R⁻¹` — the outer-product twin of
  `sandwich_preserves_dot`) plus `sandwich_preserves_normSq_of_wedge` (`|R(u∧v)R⁻¹|²=|u∧v|²`, the isometry
  extended to grade 2). Both went structural over pure-`ring` cores (`wedge_reverse_sandwich`,
  `normSq_reverse_sandwich_wedge`) — the direct `field_simp`/`ring` on the wedge-of-sandwiches **timed
  out**, so the structural route was necessary, not merely cleaner. Orientation of the plane itself is
  `rotation_fixes_plane_bivector`.

**Versor-hypothesis sweep:** every sandwich lemma's nondegeneracy hypothesis became
`normSq (evenVersor …) ≠ 0` (the versor's squared magnitude, "R is invertible"), not the raw coordinate
sum `s²+c12²+c13²+c23² ≠ 0`; the coordinate form is recovered inside each proof only where `field_simp`
needs it (`rw [normSq_evenVersor] at hr`). This let `RotateComponents` drop its `normSq_evenVersor`
downgrade (it already carried the meaningful `normSq (versorFromVectors …) ≠ 0`), and the grade-2 isometry
leaves are stated on `wedge (vec u)(vec v)` directly — no bivector-coordinate literal.

**Coordinate bashes converted to structural chains:**
- `plane_eq_wedge` (`a (b − proj_a b) = a∧b`): `mul_eq_dot_add_wedge` splits `a r = a·r + a∧r`, the scalar
  part dies by `reject_perp` (via `dot_comm`), the wedge part folds to `a∧b` by `wedge_reject`.
- `reject_vec_eq` (Hestenes, `(b∧a)a⁻¹ = b − proj_a b`): `b∧a = ba − (b·a)·1` (the split rearranged), then
  `(b∧a)a⁻¹ = b(a a⁻¹) − (b·a)a⁻¹ = b − proj_a b` using the new blade-inverse identity
  `mul_vec_inverse_self` (`a a⁻¹ = 1`, from `reverse_vec` + `mul_vec_self` (`a a = |a|²·1`) +
  `1/|a|²·|a|² = 1`) and `sub_mul`/`mul_assoc`.

**De-duplication sweep:** the codebase was already largely de-duplicated. The remaining `ext <;> ring`
proofs are leaf lemmas (kept coordinate-proved) and the `field_simp` proofs are inherently coordinate
(the `sandwich_*` and literal-bivector `1/normSq` field bashes). Two facts that were still re-derived
inline in more than one proof were promoted to named leaves and reused: `dot_self_vec_eq_normSq`
(`a·a = |a|²` — was inline in `plane_eq_wedge` and `reject_vec_eq`) and `wedge_vec_eq_biv` (`a∧b` = the
plane-bivector literal — was inline in `proj_plane_eq_project_onto` and `RotateComponents`).

**Cross-project distillation:** the coordinates-first-then-leaves workflow and its gotchas were written
up in `runClaudeInContainer` / `runCrushInContainer` `tasks/reference/lean-proof-methodology.md`.

## Limits and decisions

- The leaf properties themselves (symmetry, bilinearity, the split, Lagrange) and the two preservation
  lemmas (`sandwich_preserves_dot`/`_wedge`) stay coordinate-proved — they are the bridge. The gain was
  entirely in the high-level geometric theorems.
- `project_add_reject` was left as a coordinate proof: it is about a literal bivector `B` (already
  de-duped via `normSq_biv`), and a structural form would need a bivector-inverse story — lower value.
- The remaining 2-site micro-`have`s (e.g. `normSq (evenVersor s c12 0 0) = s²+c12²` in the `*_fixes_*`
  proofs) were left as-is: routing them through `normSq_evenVersor` leaves a `0²` residue and does not
  shorten the proof.

## Open questions (resolved)

1. ~~How far to push conversions that are "structural but not shorter"?~~ **Resolved** — only converted
   when both coordinate-free *and* no longer than the `ext <;> ring`; a one-line coordinate leaf was left
   as-is (legibility/generality was the goal, not coordinate-freeness for its own sake).
2. ~~Add a general `grade`-projection abstraction to unify the graded inner/outer products?~~
   **Resolved: no** — kept the per-grade-pair forms; a general graded-projection is a bigger design that
   only pays off with more grades.

## Pointers

- Leaf-node index and the leaf/structural split: `tasks/reference/lean-ga-proof-architecture.md`.
- The magnitude unification that fed this (one `magnitude = √normSq`, `mag`/`magnitude_vec` deleted):
  `tasks/archive/2026/09/29/lean-proofs-magnitude-and-conciseness-sweep.md`.
