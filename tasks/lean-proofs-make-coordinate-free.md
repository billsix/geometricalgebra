# Lean proofs — how much more can be made coordinate-free?

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** the landed proof layer (`proofs/GacalcProofs/`): `AlgebraLaws.lean` (assoc, distributivity,
`one_mul`/`mul_one`, `smul_mul`/`mul_smul`/`smul_smul`/`one_smul`, ⊥-anticommutation), the `dot`/`wedge`
bilinearity lemmas (`dot_sub_left`/`dot_smul_left`, `wedge_sub_right`/`wedge_smul_right`, now in both G2
and G3), and the `normSq`/`inverse`/`magnitude` abstractions (`Sandwich.lean`).

**Status:** proposed — needs go-ahead (2026-09-29, William Emerison Six <billsix@gmail.com>)
**Priority:** 7
**Difficulty:** 5

## BLUF

An audit + refactor: given the aggregate of algebra-law, bilinearity, and magnitude(-squared)
abstractions now proved, **re-prove as many of the existing coordinate proofs (`ext <;> ring` /
`field_simp`) structurally (coordinate-free) as cleanly reduce**, and record which proofs *must* stay
coordinate-based (the "leaf" lemmas that connect an abstraction to the 8-field representation). The
lesson from this session (the maintainer's magnitude-squared question): the right scalar abstractions
+ their algebra lemmas turn coordinate bashes into short structural `rw` chains — e.g. G2 `reject_perp`
went from a `vec`-form `field_simp` to `rw [dot_sub_left, proj, dot_smul_left]; field_simp; ring`,
general in `a, b`. "Done" = each proof that *can* be made structural is, `make lean` green, with a short
reference note on the leaf/structural split.

## Context — the two layers

- **Leaf lemmas (must stay coordinate):** the ones that connect a definition to the coordinate
  representation — e.g. `normSq_evenVersor = s²+…`, `versorFromVectors_mul_reverse` (`R R̃ = normSq·1`),
  `normSq_mul` (multiplicative), the multiplication-table lemmas, `mul_assoc`/distributivity, the
  `dot`/`wedge` bilinearity lemmas themselves. These are proved once by `ext <;> ring` and are the
  bridge; they should NOT be "made coordinate-free" (there's nothing below them).
- **Structural layer (candidates to convert):** everything built *on* the leaves. Several are already
  structural (`versorFromVectors_mul_inverse`, `sandwich_carries_from_to`, `sandwich_comp`,
  `sandwich_add`/`smul`, `project_eq_sub_reject`, the 3D + new 2D `reject_perp`). Candidates still doing
  coordinate work that *might* reduce structurally with the existing lemmas.

## Progress (2026-09-29, autonomous session)

Landed and `make lean` green:
- **Inner/outer property leaves** (G2 + G3): `dot_comm`, `dot_add_left`, `wedge_antisymm`,
  `wedge_sub_left`/`wedge_smul_left` (G3), `wedge_sub_right`/`wedge_smul_right`/`wedge_self_vec` (G2).
- **Lagrange-as-property + sin/cos** (`Trig.lean`, both algebras): `lagrange_property`,
  `cos_between`/`sin_between`, `cos_sq_add_sin_sq` (`cos²+sin²=1`) — the sine/cosine leaves.
- **General magnitude** `|A| = √(normSq A)` (all grades) — the **single** magnitude concept after the
  2026-09-29 unification (the vector-only `mag = √(a·a)` and the `magnitude_vec` bridge were deleted;
  `normSq`/`magnitude` moved into `G2.lean`/`G3.lean`). See the archived
  `tasks/archive/2026/09/29/lean-proofs-magnitude-and-conciseness-sweep.md`.
- **Named coordinate leaves** `normSq_vec`/`dot_vec`/`normSq_wedge_vec` (G2 + G3); the **leaf-node index**
  recorded in `tasks/reference/lean-ga-proof-architecture.md`.
- **De-dup sweep (partial):** `Trig` `cos_sq_add_sin_sq` haves collapsed to leaf one-liners;
  `Projection` `reject_vec_eq`/`plane_eq_wedge` use `normSq_vec` and phrase nondegeneracy as
  `normSq (vec a) ≠ 0` (dropped the redundant `dot_self_vec` — self-dot is just the squared magnitude).
- **Cross-project distillation:** `runClaudeInContainer`/`runCrushInContainer`
  `tasks/reference/lean-proof-methodology.md` (coordinates-first-then-leaves workflow + the gotchas).

- **Flagship DONE:** **a rotation preserves the cosine of the angle, coordinate-free** —
  `sandwich_preserves_cos` (`cos(RuR⁻¹, RvR⁻¹) = cos(u,v)`, G2 + G3), from `sandwich_preserves_dot`
  (numerator) + `magnitude_sandwich_vec` (denominators). Since `cos` determines the unoriented angle,
  the rotation preserves the angle. The magnitude leaf `sandwich_preserves_normSq_of_vec`
  (`|RvR⁻¹|²=|v|²`) was done **structurally** (the direct `field_simp` choked on the `|R|⁴` denominator):
  factor the inverse's scalar (`mul_smul`), `normSq_smul`, the pure-polynomial `|RvR̃|²=|R|⁴|v|²`
  (`normSq_reverse_sandwich`), then cancel `(1/|R|²)²·|R|⁴ = 1`.

**Remaining (optional):**
- **`sandwich_preserves_sin`** (⟹ the *oriented* angle, not just `cos`): needs
  `|wedge(RuR⁻¹)(RvR⁻¹)| = |u∧v|`. Cleanest route: the sandwich is an **outermorphism**
  (`wedge(Ru R⁻¹)(Rv R⁻¹) = sandwich R (u∧v)`, from conjugation being multiplicative + grade-preserving)
  plus `normSq` preserved on the *bivector* `u∧v` (a bivector is a blade in 3D, so `normSq_reverse_sandwich`
  extends to it). The orientation itself is already covered for the rotation by `rotation_fixes_plane_bivector`.
- A fuller de-dup pass over the remaining inline coordinate derivations (limited by the `a*a` vs `a^2`
  form friction — some genuinely need a `ring` bridge, e.g. `plane_eq_wedge`'s field computation).

## Inner/outer-product property layer (maintainer steer, 2026-09-29) — the main thrust

Treat the **inner product `·` and outer product `∧` as leaf nodes carrying algebraic properties**
(including the sine/cosine characterization), then rebuild the higher proofs on those properties
instead of coordinates. This is the same trade `normSq` + `dot`-bilinearity already bought, extended to
a fuller inner/outer *property algebra*. What exists already: `vec_mul_eq_dot_add_wedge` (the split
`ab = a·b + a∧b`, G3), `dot_sub_left`/`dot_smul_left`, `wedge_sub_right`/`wedge_smul_right`,
`wedge_self_vec`, G2 `vec_mul`/`dot_is_sym_part`/`wedge_is_antisym_part`, Lagrange 2D/3D.

**Leaf properties to add (proved once by `ext`/`ring` — the coordinate bridge):**
- [ ] **Symmetry / antisymmetry:** `dot_comm` (`a·b = b·a`), `wedge_antisymm` (`a∧b = −(b∧a)` for
      vectors). Neither is a named lemma yet.
- [ ] **Full bilinearity:** the `add`-versions and the missing side (`dot_add_*`, `wedge_add_*`,
      left/right) — currently only `sub`/`smul` on one side.
- [ ] **The fundamental split, general form:** a version of `ab = a·b + a∧b` over *arbitrary* vectors
      (the current one is vector-literal only). The master rewrite turning geometric-product goals into
      inner+outer — highest leverage.
- [ ] **Lagrange as a property (coordinate-free):** `(a·b)² + |a∧b|² = |a|²|b|²` in terms of
      `dot`/`normSq`/`wedge` (proved by unfolding). This is the sin/cos Pythagorean.
- [ ] **The sin/cos characterization:** `cos a b := (a·b)/(|a||b|)`, `sin a b := |a∧b|/(|a||b|)`, with
      **`cos² + sin² = 1`** a one-line corollary of Lagrange-as-property. The maintainer's sine/cosine
      leaves.

**Payoff — proofs that go coordinate-free (best first):**
- [ ] **"Rotation preserves the *oriented angle*"** (the top spike). Have `sandwich_preserves_dot`
      (the `cos` numerator). Add ONE leaf — **`sandwich_preserves_wedge`** (outer product preserved,
      like `preserves_dot`) — then "preserves the oriented angle" = "preserves `cos` AND `sin`" falls
      out coordinate-free from the sin/cos properties. Realizes the sine/cosine idea literally.
- [ ] **`plane_eq_wedge`** — from the `field_simp` bash to structural: `a·r + a∧r` via the general
      split, scalar part killed by `reject_perp`, wedge part by `wedge_reject`.
- [ ] **`reject_vec_eq` / `project_add_reject`** — reduce to `ab = a·b + a∧b` + `B B⁻¹ = 1`
      manipulations rather than coordinates.

**Limits (stay coordinate-proved — correct, they are the bridge):** the leaf properties themselves
(symmetry, the split, Lagrange, bilinearity) and the two *preservation* lemmas
(`sandwich_preserves_dot`/`_wedge`). The gain is entirely in the high-level geometric theorems.

## Plan (audit, then convert the tractable ones)

- [ ] **Inventory** every theorem whose proof is `ext <;> ring` / `field_simp` / `simp; ext; ring`, and
      tag each: (a) *leaf* (keep — connects to coordinates), (b) *convertible* (a structural `rw`-chain
      exists using the algebra-law / bilinearity / normSq lemmas), (c) *inherently coordinate* (a genuine
      polynomial identity with no shorter structural form, e.g. `plane_eq_wedge`, the `sandwich_*` field
      computations that clear `1/normSq`).
- [ ] **Convert the (b) cases.** Likely candidates: `wedge_reject` (already partly structural),
      `plane_eq_wedge` (could use `vec_mul_perp` + `wedge_reject` given a "rejection is a vec" bridge),
      the `reject_vec_eq` family, and any G2 proof that now has G2 bilinearity lemmas available.
- [ ] **Add small missing algebra lemmas** where a conversion is one lemma short (e.g. a `dot_comm`, a
      `mul_add`-for-vectors, wedge antisymmetry `wedge_comm_neg`), only when they unlock a conversion.
- [ ] **Record the split** in `tasks/reference/lean-for-gacalc.md`: which lemmas are the coordinate
      bridge and which are structural — the "leaf vs structural" architecture, as guidance for future
      proofs (write the structural form; let a few leaves touch coordinates).
- [ ] `make lean` green throughout; no proof gets *longer* (revert a conversion that doesn't shorten).

## Final step (maintainer, 2026-09-29): leaf-node index + de-duplication sweep

- [ ] **Build named leaf lemmas** for the coordinate facts re-derived inline all over the proofs — first
      the magnitude/product-on-vectors ones: `normSq_vec` (`normSq (vec a) = a₁²+…`), `dot_vec`
      (`dot (vec a)(vec b) = a₁b₁+…`), `normSq_wedge_vec` (`|a∧b|² = …`), for **both G2 and G3**. (There
      are ~26 inline `normSq (vec …) = …²` / `dot (vec …)(vec …) = …` re-derivations right now — e.g. in
      `Trig.lean`, `Rotation3D.lean`/`Versor2D.lean` `mag_sq_vec`, `Projection.lean` `plane_eq_wedge`,
      `reject_vec_eq`, the `Sandwich.lean` `*_fixes_*`/`normSq_evenVersor` haves.)
- [ ] **Index the leaf nodes** in `tasks/reference/lean-ga-proof-architecture.md` — one list of every
      coordinate-bridge lemma (`normSq_vec`, `dot_vec`, the multiplication table, bilinearity, the
      fundamental split, Lagrange-property, …), so future proofs reach for a named leaf, not `ext; ring`.
- [ ] **Scan every proof and de-duplicate:** wherever a proof re-derives one of those facts inline (or
      bashes coordinates for something a landed result already gives), rewrite it to **use the leaf node
      / prior result** instead — compacting the proof and making it legible, not coordinates everywhere.
      `make lean` green throughout; revert any rewrite that doesn't actually shorten/clarify.

## Open questions

1. How far to push conversions that are "structural but not shorter"? (Rec: only convert when it is
    *both* coordinate-free *and* no longer than the `ext <;> ring` — the goal is legibility/generality,
    not coordinate-freeness for its own sake; a one-line `ext <;> ring` leaf is fine as-is.)
2. Worth adding a general `grade`-projection / `r_vector_part` abstraction (like `inner_vb`'s grade-1
    extraction) to unify the graded inner/outer products, or keep the per-grade-pair forms? (Rec: keep
    per-grade for now; a general graded-projection is a bigger design and only pays off with more grades.)
