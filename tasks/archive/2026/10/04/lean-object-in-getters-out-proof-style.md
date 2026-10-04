# Lean proofs: "geometric objects in, components out" — dissolve the scalar `_coord` layer

**Status:** DONE & ARCHIVED 2026-10-04 (`make lean` green). Polynomial tier converted; coordinate core
retained by documented decision (maintainer approved option (a), 2026-10-04). **Consolidated record** — this
doc absorbed the earlier statement-lift task [[lean-lift-theorem-statements-to-objects]] (now a superseded
stub). Optional follow-up: [[push-delicate-coordinate-core-tier]].
**Priority:** 6 (was 4; the valuable bulk is done, the remainder is an optional high-risk tier)
**Difficulty:** 7

> **Where it stands (2026-10-04):** every theorem whose proof is **polynomial** is now object-in /
> getters-in-body (Sandwich full, RotateComponents `rotation_preserves_dot`, Reflect, G3 self-products,
> Projection2D, Projection3D 3/4, Trig `lagrange_property`, the pure-poly ProjectionRotation scaffold
> leaves). The **coordinate core is retained by design** for the non-polynomial tier — sqrt/`magnitude`/
> `normalizeVec` proofs, the divide-by-`normSq(a∧b)` (degree-blowup) plane projections, the cos/sin/angle
> and literal-then-instantiate exceptions, and the delicate `calc`/`set` capstones
> (`projRotation_eq_sandwich`/`_isometry`, the bisector machinery, `reject_vec_eq`, `cos_sq_add_sin_sq`,
> `sin_between_eq_abs_signed_vec`, CrossStandardPosition). Those public statements are already object-in;
> only their private coordinate scaffold stays coordinate. The `_coord`-deletion + dead-bridge sweep is
> done (see below). **Optional follow-up:** push the delicate tier — would need new object
> `magnitude`/`normalizeVec` lemmas first; higher risk, low marginal value. Per-file detail and the reusable
> recipes/dead-ends are below and in `tasks/reference/lean-ga-proof-architecture.md`.

## BLUF

Convert every Lean theorem about geometric objects to the **"geometric objects in, scalars in the body,
geometric objects out"** style (in = the function's parameters, out = its conclusion, in-the-body = the
implementation): take the **object** (`{a : G3} (ha : IsVector a)`, `{R} (hR : IsEvenVersor R)`,
`{B} IsBivector`, `{T} IsTrivector`) and conclude about objects, and only where the proof needs coordinates,
**destructure it in the body** (`obtain ⟨…⟩ := ha; simp only
[defs, those-zeros]; ring`, computing on `a.c1`/`a.c12` getters) — **never** take free scalars
`(a1 a2 a3 : ℝ)` and *construct* `vec a1 a2 a3` inside. This **eliminates the scalar-taking `_coord`
leaves** (the `foo_coord (reals) : P (vec reals)` + `foo {obj} := by have h := foo_coord …; rwa [← eq_vec]`
pattern): the object theorem absorbs its own computation, and shared computation is shared through **object**
theorems (a composite like `cos` composes the object `dot`/`magnitude`, not a scalar `_coord`). "Done" =
no scalar-coordinate `_coord` leaf remains (except the genuine-scalar and form-D exceptions below), `make
lean` green.

## Context / why

Maintainer direction (2026-10-03): "take geometric objects as inputs, and then in the body, get their
components, rather than taking scalars as inputs, and then constructing geometric objects." The ℝ→object
STATEMENT sweep (`tasks/lean-lift-theorem-statements-to-objects.md`, Increments 1–23) made the *public*
theorems object-form, but did so with a uniform `_coord`-leaf + thin-bridge mechanism — which keeps a
scalar-taking layer underneath. This task removes that layer: the proof destructures the object directly.

**Two inline shapes (prefer the first):**
- **`obtain` (pure):** `obtain ⟨hs, h12, …⟩ := ha; simp only [sandwich, mul, reverse, normSq, hs, h12, …];
  field_simp; ring` — works on `R.s`/`a.c1` getters, no `vec`/`evenVersor` ever reconstructed. This is the
  maintainer's intent.
- **`rw [eq_vec_of_isVector ha]` (lighter):** turns the goal into the `vec`-literal form so an existing
  coordinate proof runs verbatim. Reuses the proof but technically re-mentions `vec a.c1 a.c2 a.c3`; use
  only when a verbatim fragile proof must be preserved.

**Sharing moves to the object level.** The reason the `_coord` leaves looked "shared" (audit in the lift
task) is that higher theorems were *also* `_coord`, so they shared the lower `_coord`. Once every theorem
is object-form and composites compose object sub-lemmas (as `sandwich_preserves_cos`/`sin` now do — bucket
1), each leaf's `_coord` loses its coordinate callers and dissolves into its own object proof.

## What is DONE (bucket 1, 2026-10-03, `make lean` green)

Inlined the clean single-caller pass-throughs, deleting their `_coord`: `vec_mul_mul_self` (Rotation3D),
`sandwich_evenVersor_vec_isVector` (Sandwich), `rotation_fixes_plane_bivector`/`rotation_preserves_dot`
(RotateComponents), `reverse_versorFromVectors_mul` (ProjectionRotation2D, in the pure `obtain` form), and
`sandwich_preserves_cos`/`sin` (G2+G3, Trig — now **fully object**, composing the object `dot`/`wedge`/
`magnitude` isometries, zero coords). (`rotation_fixes_normal` was left as `_coord`+wrapper — its wrapper
does a `cross b a`↔explicit-normal reconciliation that a forward `rw [eq_vec]` can't do cleanly; it belongs
with the delicate set below.)

## The conversion inventory (per file)

Target: dissolve each scalar `_coord`. Counts are approximate and include G2/G3 twins.

### (A) `_coord` leaves to dissolve into object proofs — the bulk

- **Sandwich.lean (~22):** `normSq_evenVersor`-adjacent + `sandwich_preserves_dot`/`_normSq_of_vec`/
  `magnitude_sandwich_vec`/`_wedge`/`_normSq_of_wedge` (G2+G3), `versorFromVectors_mul_reverse`/`_inverse`,
  `mul_biv_*`/`mul_triv_*`, `normSq_reverse_sandwich(_wedge)`, `wedge_reverse_sandwich`,
  `sandwich_carries_from_to`, `sandwich_comp`, `sandwich_fixes_own_bivector`/`_normal`,
  `sandwich_fixes_orthogonal`/`plane_invariant`. **Leaves:** `obtain` the versor/vector zeros + `field_simp;
  ring`. **Composites** (`magnitude_sandwich_vec` via `_normSq_of_vec`; `sandwich_comp` via `inverse_mul`)
  compose object sub-lemmas.
- **ProjectionRotation3D.lean (~16):** the scaffold `_coord` (`plane_pythagorean`, `project_perp_reject`,
  `inplane_perp_reject`, `project_onto_in_plane_self`, `reject_in_plane_self`, `wedge_vec_wedge_self`,
  `inner_vb_mul_reverse_self`, `normSq_mul_vec`, bisector trio, `versor_mul_project_eq`/`_reject_comm`) +
  the delicate capstones `projRotation_isometry`/`_eq_sandwich`/`carries_from_to`.
- **ProjectionRotation2D.lean (~7):** `mul_vec_self`, `reject_plane_eq_zero`, `magnitude_sq_of_normSq`,
  `normSq_mul_three_vec`, `versorFromVectors_mul_vec_eq`, `key_reverse_sq`, `fhat_that_eq_reverse_mul_inverse`.
- **Projection3D.lean (4):** `plane_eq_wedge`, `mul_vec_inverse_self`, `reject_vec_eq`, the bivector-plane
  `project_add_reject`/`reject_eq_proj_normal`/`project_eq_sub_reject` (→ `obtain` on `IsBivector`).
- **Projection2D.lean (5):** `wedge_reverse_sandwich`, `normSq_reverse_sandwich_wedge`,
  `sandwich_preserves_wedge`/`_normSq_of_wedge`, `reject_from_I_eq_zero`.
- **G3.lean (3):** `mul_vec_self`/`dot_self_vec_eq_normSq`/`wedge_self_vec` (shared leaves; `obtain` form).
- **Trig.lean (2):** `lagrange_property` (G2+G3). **CrossStandardPosition (3):** `cross_rot*_equivariant`.
  **Reflect (2), RotateComponents (1: `rotation_fixes_normal`+`sandwich_ahat`), Rotation3D/Versor2D (bisector
  `_coord`), TrigEquiv (`sin_between_eq_abs_signed_vec`).**

### (B) form-D `vec`-literal bridge lemmas — THE KEY DECISION

`normSq_vec`, `dot_vec`, `cross_vec`, `dual_vec`, `wedge_vec_eq_biv`, `normSq_wedge_vec`, `magnitude_sq_vec`,
`vec_mul` (G2), `vec_eq_smul`, `reverse_vec`, `signedArea_eq`/`_sq`, `vec_mul_eq_dot_add_wedge`,
`vec_mul_perp`, `normSq_biv`/`_triv`. These take vector coordinates and their **RHS is coordinate
arithmetic** (`= a1²+a2²+a3²`, `= vec (a2*b3−…)`). Two options:
1. **Flip to object-in** (`{a} IsVector : normSq a = a.c1² + a.c2² + a.c3²`) — matches the style literally,
   but the RHS is still getter-arithmetic and these are used corpus-wide as `rw`-unfold lemmas (**high
   blast radius**).
2. **Leave them / let them go vestigial** — in the `obtain`-getters style, proofs unfold the *definitions*
   (`simp only [normSq, mul, …]`) + the obtained zeros, rather than `rw [normSq_vec]`. So these vec-literal
   unfolds become rarely-needed; keep as the irreducible `vec`-constructor base, or delete the dead ones.
   `vec_mul_eq_dot_add_wedge`/`vec_mul_perp`/`dual_vec_perp` already have object companions
   (`mul_eq_dot_add_wedge`/`mul_eq_wedge_of_perp`/`dual_perp`).

**Recommendation: option 2** — don't flip the definitional unfolds (no readability gain + high blast);
remove any that become unused once (A) is done. **This is the main thing to confirm.**

### (C) coordinate-parameterized defs/theorems — the rotation is DEFINED by coordinates

`rotXY_vec`/`rotXZ_vec`/`rotYZ_vec` (unfold a plane rotation of a `vec`), `rotYZ_fixes_e1`,
`rotXY_aligns_xy`/`rotXZ_aligns_xz`/`rotate_b_to_e1`/`_magnitude`, `reduceToPlane_a_on_e1`/`_b_in_plane`,
`Exp.expBivector*`/`normSq_expBivectorGeneral`. The cos/sin (or `p q r`) here **are** `b`'s coordinates / the
construction's input. The *vector* arg can become an object (`{b} IsVector`) with the rotation params read
off its getters, but the statement stays intrinsically coordinate. **Low value; defer.** (`Exp` needs the
`exp` *function* redefined to take a bivector object — a def redesign, separate.)

### (D) genuine scalars — KEEP as-is (the exceptions the maintainer named)

`Rotation2D.lean` (entire angle layer: `θ`/`α`/`β` angles, `rot` on `ℝ×ℝ` pairs — no G-object exists),
`Lagrange.lean` `lagrange_2d`/`lagrange_3d` (pure real identities, no GA object), the `cos_between`/
`sin_between`/`versorFromVectors` scalar params, the `k` scalar multiples, and the companion discharge
lemmas `isVector_vec`/`isBivector_bivector`/`isTrivector_trivector`/`isEvenVersor_evenVersor`.

## Risks / what I'd watch

1. **Chain-wide, not one-at-a-time.** A composite's object proof needs its sub-lemmas object *first*; convert
   bottom-up (leaves → composites), `make lean` green each step. Shared `_coord` can't be deleted until all
   its callers are object.
2. **Delicate proofs** (`projRotation_eq_sandwich` plen~55, `_isometry` plen~42, `key_reverse_sq`,
   `versor_mul_from_eq_bisector`, the √-structural cores): `obtain`+`field_simp`/`ring` should work (ring is
   name-agnostic), but `set`/`calc` proofs may need care. Keep an `eq_vec`-reconstruction fallback for any
   that fight the `obtain` form.
3. **This reverses the `_coord`+bridge pattern from Increments 9–23.** Expect churn on just-done work; net
   result is fewer symbols and a single object theorem each.
4. **Docstring hygiene:** when merging a `_coord`+wrapper into one theorem, delete the *stale* leaf docstring
   (two `/-- … -/` in a row is a Lean parse error — this bit bucket 1; caught by a "two docstrings before one
   decl" scan).

## End-of-conversion cleanup sweep (planned; maintainer asked 2026-10-03 "are those components even used?")

After every `_coord` is deleted, run a dead-code sweep:

1. **Dead whole lemmas** — the form-D `vec`-literal bridges (Decision 1 below) and any leaf/helper left
   unreferenced once the `obtain`-getters proofs stopped calling them. Find with
   `rg '\btheorem (\w+)\b'` → for each, `rg '\bNAME\b'` across `proofs/` and drop the zero-other-hit ones
   (version-aware of the G2/G3 twin names). This is the valuable sweep.
2. **Unused `obtain` bindings** — none expected: every destructured name is passed into the proof's
   `simp only [… , hR1, hvs, …]` list, so Lean's `unusedVariables` linter stays quiet. If a trim ever
   leaves a binding unreferenced, Lean warns; fix by `⟨_, _, h, _⟩`-style holes.
3. **Redundant `simp only` args (LOW VALUE — skip unless asked).** The full grade-predicate destructuring is
   included uniformly; `simp only` ignores a rule that doesn't fire, so extra args are harmless. Trimming
   them to the minimal set is per-theorem guesswork that needs a rebuild to confirm each wasn't load-bearing
   — not worth it against the readability gain.

## Decisions (maintainer, 2026-10-03 — "go with your recommendations")

1. **(B) form-D `vec`-unfold bridges: LEAVE coordinate** (`normSq_vec`, `dot_vec`, `cross_vec`, `dual_vec`,
   `wedge_vec_eq_biv`, `normSq_wedge_vec`, `magnitude_sq_vec`, `vec_mul`, `vec_eq_smul`, `reverse_vec`,
   `signedArea_eq/_sq`, `normSq_biv/_triv`). **Decided AGAINST flipping them to object-in.** Why: their RHS
   *is* coordinate arithmetic, so an object form (`normSq a = a.c1²+a.c2²+a.c3²`) only moves the coordinates
   onto the RHS as getters — no readability gain — while they are used corpus-wide as `rw`-unfold lemmas
   (high blast radius). They are the irreducible `vec`-constructor base. **Action:** after (A), delete any
   that end up unused (the `obtain`-getters proofs unfold *definitions* `simp only [normSq, mul, …]` rather
   than these vec-literal lemmas, so several may go dead); keep the rest.
2. **(C) coordinate-parameterized rotation-alignment / `Exp` defs: STAY coordinate.** Decided against
   objectifying the vector arg, because the cos/sin (or `p q r`) genuinely *are* the construction's scalar
   input, so the statement is intrinsically coordinate (and `Exp` would need a `def` redesign).

## Implementation progress (A — dissolve the `_coord` leaves)

Bottom-up (leaves → composites), `obtain`-getters for leaf computations, compose-object for composites,
`make lean` green + stage each step. Delete a `_coord` only once no object theorem and no other `_coord`
references it. Log increments here.

### Finding — TEXTUAL ORDERING is a hard constraint on compose-object (2026-10-03)

A composite's object proof `rw [leaf_lemma hR hu hv]` only compiles if the **object** `leaf_lemma` is
defined **textually above** the composite. The lift increments (9–23) added every object form as a
*separate* decl in an **end-of-namespace wrapper block**, so for a leaf consumed by an *earlier* composite
(e.g. `wedge_reverse_sandwich` at Sandwich.lean:643 consumed by `sandwich_preserves_wedge` at :398) the
compose-object rewrite is a **forward reference → "Unknown identifier"**. The `_coord` bridge never hit this
because the `_coord` leaves sit in the main body, already in correct dependency order (leaf `_coord` before
composite `_coord`).

**Mechanic that avoids it — convert IN-PLACE, not as a parallel block.** Rewrite each `_coord` leaf's body
to `obtain`-getters and **rename it in place** (drop the `_coord` suffix), then delete the duplicate
end-block object wrapper; because the `_coord` decls are already ordered leaf-before-composite, in-place
replacement preserves the ordering automatically and no leaf needs moving. For a leaf whose object wrapper
is in the end block AND whose consumer is earlier, either (a) move the self-contained object leaf up to
just above its first consumer, or (b) leave that one composite on its `_coord` bridge until the final
deletion sweep. This refines Risk 1: "bottom-up" must mean *bottom-up in the file*, not just in the
dependency DAG.

### Increment 1 — Sandwich.lean leaves (2026-10-03, `make lean` green, staged)

- Converted to self-contained `obtain`-getters (object-native, no `_coord`): `normSq_reverse_sandwich`,
  `normSq_reverse_sandwich_wedge`, `wedge_reverse_sandwich` (G3), `versorFromVectors_mul_reverse`,
  `mul_biv_reverse_self`, `mul_triv_reverse_self`. `magnitude_sandwich_vec` (G3) converted to compose-object
  (`simp [magnitude]; rw [sandwich_preserves_normSq_of_vec …]`) — its dep is above it, so no forward ref.
- **Left on the `_coord` bridge pending the reorg** (forward-reference the three leaves above, which are in
  the end block): `sandwich_preserves_normSq_of_vec`, `sandwich_preserves_wedge`,
  `sandwich_preserves_normSq_of_wedge`. These 3 composites convert to compose-object once their object
  leaves are moved up (per the Finding). Still green via the bridge.

### Increment 2 — Sandwich.lean G3 vec/wedge sub-cluster FULLY object-native + `_coord`-free (2026-10-03, green, staged)

Applied the in-place mechanic to the whole vec/wedge-preservation sub-cluster. Each leaf `_coord` was
rewritten to `obtain`-getters **and renamed in place** (drop `_coord`); the end-block object duplicates
were deleted; the composites now compose the in-place object leaves; and the orphaned `_coord` composites
were deleted. Net for this sub-cluster: 6 symbols → 6 (one object theorem each), no `_coord` left.

- **Leaves (now `obtain`-getters, in place):** `normSq_reverse_sandwich`, `wedge_reverse_sandwich`,
  `normSq_reverse_sandwich_wedge` (G3).
- **Composites (now compose-object, no forward ref — leaves sit above them):**
  `sandwich_preserves_normSq_of_vec` (`rw [sandwich, inverse, mul_smul, normSq_smul,
  normSq_reverse_sandwich hR hv]; field_simp [hr]`), `sandwich_preserves_wedge`,
  `sandwich_preserves_normSq_of_wedge`, `magnitude_sandwich_vec`.
- **Deleted (orphaned):** `*_coord` twins of all six, plus the three end-block object duplicates.
- **Confirms:** `field_simp [hr]` closes the composite with `hr : normSq R ≠ 0` (object form) exactly as it
  did with the coord-form hypothesis — the structural proof is grade-predicate-agnostic.

### Increment 3 — Sandwich.lean G2 vec cluster object-native; `dot` identified as a FIGHTER (2026-10-03, green, staged)

- **Converted (object-native, `_coord`-free):** G2 `normSq_reverse_sandwich` (obtain leaf),
  `sandwich_preserves_normSq_of_vec` + `magnitude_sandwich_vec` (compose-object). Deleted the G2
  `normSq_reverse_sandwich` end-block wrapper and the three orphaned `_coord` (leaf, vec composite,
  magnitude). G2 `versorFromVectors_mul_reverse` wrapper kept on its bridge because its `_coord` is still
  consumed by the delicate `sandwich_carries_from_to_coord`.

### Increment 4 — `sandwich_preserves_dot` (G2 + G3) getter-native; the "divide-by-`normSq`" pattern SOLVED (2026-10-03, green, staged)

What first looked like a fighter is not one. A *direct* `obtain`-getter dot proof fails
(`simp [normSq,…] at hr ⊢; field_simp [hr]; ring` → `unsolved goals`): the sandwich's `inverse` puts
`(normSq R)²` in the denominator, and a raw getter unfold **expands** it (`s⁴+2s²c²+c⁴`), so
`field_simp [hr]` can't match `hr : normSq R ≠ 0`. **The fix is the same atomic-`normSq` leaf pattern the
vec/wedge composites already use** — the leaf keeps `normSq R` *un-expanded* on its RHS, so the composite
cancels it as an atom:

- Added leaf **`dot_reverse_sandwich`** (G2 + G3): `(R u R̃) · (R v R̃) = normSq R ² · (u · v)`, proved by
  `obtain`-getters + pure `ring` (atomic `normSq R`, the dot twin of `normSq_reverse_sandwich`).
- **`sandwich_preserves_dot`** (both grades) is now `simp only [sandwich, inverse, mul_smul];
  rw [dot_smul_left, dot_smul_right, dot_reverse_sandwich hR hu hv]; field_simp [hr]` — fully
  getter-native, no `_coord`. Both `dot_smul_left/right` already exist (G3 `G3.lean:171,183`; **G2**
  `Versor2D.lean:33,52` — my first grep wrongly checked only `G2.lean`, so **no new lemmas were needed**).
- **External consumer fixed:** `RotateComponents.rotation_preserves_dot` previously reconstructed to
  coordinates to call `sandwich_preserves_dot_coord`; it now derives
  `IsEvenVersor (versorFromVectors a b)` (via `versorFromVectors_eq_evenVersor` + `isEvenVersor_evenVersor`)
  and composes the object `sandwich_preserves_dot` directly.

**Upshot / generalization:** there is **no "fighter" class** here — any preservation proof that divides by
`normSq R` becomes getter-native by introducing a `_reverse_sandwich`-style leaf that keeps `normSq R`
atomic, then composing with `field_simp [hr]`. This is the recipe for the remaining division-proofs.

### Increment 5 — Sandwich.lean inverse-self composites getter-native (2026-10-03, green, staged)

`mul_biv_inverse_self`, `mul_triv_inverse_self`, `versorFromVectors_mul_inverse` (all G3) now compose their
already-object `_reverse_self` leaves directly: `rw [inverse, mul_smul, <leaf> h…, smul_smul,
one_div_mul_cancel h…, one_smul]`. Deleted the orphaned `mul_biv_reverse_self_coord`,
`mul_biv_inverse_self_coord`, `mul_triv_reverse_self_coord`, `mul_triv_inverse_self_coord`.
**Kept** `versorFromVectors_mul_inverse_coord` (still consumed by `ProjectionRotation3D.lean:377,400`) and
the G2 `versorFromVectors_mul_reverse` bridge + its `_coord` (consumed by `sandwich_carries_from_to_coord`).

**Sandwich.lean status:** every vec / wedge / dot / inverse-self / reverse-self cluster (G2 + G3) is now
fully object-native getter form. **Remaining on the `_coord` bridge — the delicate capstones only:**
`sandwich_carries_from_to` (G2 + G3; `set`/`calc`, bisector machinery), `sandwich_fixes_own_bivector`,
`sandwich_fixes_own_normal`, `sandwich_comp`. Each divides by `normSq`, so the atomic-`normSq`-leaf recipe
(Increment 4) applies, but they are `calc`/`set`-heavy — convert one at a time with a verify, and keep the
`eq_vec`-reconstruction fallback (Risk 2) for any that resist.

### Per-file progress (2026-10-03, each `make lean` green + staged)

- **Reflect.lean — DONE.** `reflectVec_eq` (structural over object `reject_vec_eq`, `proj` abstract),
  `normSq_reflectVec` (getter form; clean `^2` denominator-nonzero via `← normSq_vec,
  ← eq_vec_of_isVector`). Both `_coord` deleted.
- **G3.lean — object wrappers DONE** (`wedge_self_vec`, `dot_self_vec_eq_normSq`, `mul_vec_self` → obtain
  getters). **Kept** their three leaf `_coord` (`wedge_self_vec_coord`, `dot_self_vec_eq_normSq_coord`,
  `mul_vec_self_coord`) — consumed coordinate-wise by Projection2D/3D, StandardPosition,
  ProjectionRotation2D/3D; deletable only in the final sweep once those are converted.
- **CrossStandardPosition.lean — LEAVE (Decision C).** `cross_rotXY/XZ/YZ_equivariant` are cos/sin-
  parameterized; the object wrappers already take `a b : G3` and use getters in the body feeding the
  coordinate rotation core, which is the legitimate scalar exception. No change.

- **Projection2D.lean — DONE.** `wedge_self_vec` (obtain) + the full G2 wedge/sandwich cluster
  (`wedge_reverse_sandwich`, `normSq_reverse_sandwich_wedge` obtain leaves; `sandwich_preserves_wedge`,
  `sandwich_preserves_normSq_of_wedge` compose-object) — in-place mechanic, all 5 `_coord` deleted.
- **Projection3D.lean — 3 of 4 bivector proofs DONE.** `project_add_reject`, `reject_eq_proj_normal`
  (getter-native: `obtain` the bivector/vector zeros, keep `normSq B` grouped as `B.c12²+B.c13²+B.c23²`
  via `hd` / `hd2`, `field_simp [hBn]`), `project_eq_sub_reject` (now `add_eq_left_sub _ _ _
  (project_add_reject …)` — composes the object). **Two getter gotchas found & fixed:** `inner_vb` builds
  a `vec`, so `vec` must be in the `simp` set to kill `(vec …).c12`; and the RHS `= a` exposes `a`'s
  non-vector components only *after* `ext`, so the zero-substitution (`has, ha12, …`) must be repeated
  **after** `ext`. **`reject_vec_eq` LEFT on its bridge** — structural coordinate proof (Hestenes split via
  `vec_mul_eq_dot_add_wedge`, `mul_vec_inverse_self`, …, many coord-lemma deps), a fighter. **`_coord`
  kept** (reject_vec_eq_coord feeds the bridge; project_add_reject_coord feeds ProjectionRotation3D +
  project_eq_sub_reject_coord; the now-orphaned ones go in the final sweep).

- **Trig.lean — `lagrange_property` (G3 + G2) DONE** (obtain-getters, pure `ring`). **`cos_sq_add_sin_sq`
  LEFT bridged** — a sqrt/`magnitude` proof needing `Real.sq_sqrt` + positivity on the explicit
  sum-of-squares (no object `normSq_nonneg` lemma exists); cos/sin/angle exception. `sandwich_preserves_cos`
  /`_sin` were already object-native (compose the object dot/wedge/magnitude isometries).
- **CrossStandardPosition.lean, TrigEquiv.lean — LEAVE.** Cos/sin-parameterized rotations and the
  unit-vector/signed-area `sin_between_eq_abs_signed_vec`; object wrappers already take vectors, scalar
  cos/sin core is the named exception.
- **ProjectionRotation2D.lean, ProjectionRotation3D.lean — RETAINED COORDINATE CORE (delicate tier).** The
  public capstones (`projRotation_eq_sandwich`, `projRotation_isometry`, `projRotation_carries_from_to`)
  are already object-signatured; their proofs are `calc`/`rw`-chains assembled from scaffold `_coord`
  leaves that are **sqrt/`magnitude`/`normalizeVec`-based** (`key_reverse_sq`, `fhat_that_eq_reverse_mul_inverse`,
  `magnitude_sq_of_normSq`, the bisector lemmas) — not polynomial, so they resist `obtain`+`ring` and are
  the Risk-2 "keep the coordinate core / eq_vec-reconstruction" cases. Converting them is a high-risk,
  low-net-reduction effort (the leaf `_coord` must stay to feed the capstones regardless). **Decision: leave
  these two files' scaffold + capstones on the coordinate core**, documented; the public API is already
  objects-in. Revisit only if the maintainer wants the delicate tier pushed (would likely need new object
  `magnitude`/`normalizeVec` lemmas first).
  - **Pure-polynomial scaffold leaves DID convert** (getter-native, their `_coord` kept for the capstones):
    2D `mul_vec_self`, `normSq_mul_three_vec` (and `reverse_versorFromVectors_mul` was already obtain); 3D
    `wedge_vec_wedge_self`. **Gotcha confirmed:** `versorFromVectors` (G2) is `magnitude`-based (sqrt), so
    `versorFromVectors_mul_vec_eq` is NOT polynomial — a getter+`ring` attempt left `f.magnitude *
    t.magnitude` atoms unsolved; reverted to its bridge. The `reject`/`project_onto (wedge a b)` leaves in
    3D divide by `normSq(wedge a b)` (quadratic in a,b) — the degree-blowup case the literal-bivector
    `_coord` exists to avoid — so they stay coordinate.

### Final `_coord`-deletion sweep — DONE (2026-10-04, `make lean` green, staged)

Ran the sweep (`grep` every `_coord` def, count non-definition code uses):

- **No `_coord` is orphaned.** Every remaining `_coord` is still consumed by a **retained coordinate-core**
  proof — StandardPosition, Projection3D's bridged `reject_vec_eq` and the `proj_plane_eq_project_onto`
  chain, and the two ProjectionRotation files' capstones + scaffold. The deletable ones were already removed
  **in-place** as each file was converted (Reflect, Projection2D, and the Sandwich clusters the maintainer
  has since committed). So the sweep deletes **no further `_coord`** — correct, not a miss.
- **Dead helper/bridge lemmas removed:** `normSq_triv` (Sandwich.lean — orphaned when
  `mul_triv_reverse_self_coord` was deleted; its only caller) and `signedArea_sq` (Measures.lean — the
  Decision-1 form-D bridge, a trivial restatement, unused). The other form-D `vec`-literal bridges
  (`normSq_vec` 31 uses, `cross_vec` 8, `wedge_vec_eq_biv` 9, `normSq_biv` 8, `magnitude_sq_vec` 6,
  `dot_vec`/`dual_vec`/`vec_mul`/`vec_eq_smul`/`reverse_vec`/`signedArea_eq`/`vec_mul_eq_dot_add_wedge` 1–3)
  are still live — kept.
- **A whole-library "zero code use" scan** flags ~100 names, but almost all are the library's **public
  deliverable theorems** (`sandwich_preserves_cos`, `proj_plane_eq_project_onto`, `mul_vec_self`, …) — used
  by no other proof because they *are* the output. Zero-use is therefore **not** a deletion criterion here;
  only genuine scaffold/bridge helpers were removed.
- **Unused `obtain` bindings:** none — every destructured hypothesis is referenced in its proof's
  `simp only [… , hR1, hvs, …]` list, so Lean's `unusedVariables` linter stays quiet (verified: build has no
  warnings surfaced). Redundant `simp only` args left as-is per the agreed low-value call.

### Previously-owed sweep notes (superseded by the DONE section above)

Per the cleanup-sweep plan above: grep each remaining `_coord` for live references and delete the ones left
unreferenced after this pass (e.g. Projection3D's `project_eq_sub_reject_coord`, possibly
`reject_eq_proj_normal_coord`), version-aware of the G2/G3 twins. The leaf `_coord` kept for external/delicate
consumers (`G3.{wedge_self_vec,dot_self_vec_eq_normSq,mul_vec_self}_coord`, `project_add_reject_coord`,
`reject_vec_eq_coord`, `lagrange_property_coord`, the ProjectionRotation scaffold, the form-D `vec`-literal
bridges in Decision 1) stay until their consumers are converted or are accepted as the coordinate core.

## Converted files summary (2026-10-03, all `make lean` green + staged)

Sandwich (full: vec/wedge/dot/inverse-self/reverse-self, G2+G3), RotateComponents (`rotation_preserves_dot`),
Reflect (full), G3 (self-product wrappers), Projection2D (full wedge cluster), Projection3D (3 of 4 bivector
proofs), Trig (`lagrange_property` G2+G3). Retained coordinate core (documented, by design): the two
ProjectionRotation files, CrossStandardPosition, TrigEquiv, `cos_sq_add_sin_sq`, `reject_vec_eq`, and the
form-D `vec`-literal bridges.

## Other files — remaining (same mechanic, bottom-up per file)

`ProjectionRotation3D` (16), `ProjectionRotation2D` (7), `Projection3D` (4), `Projection2D` (5 — note it has
its own G2 copies of `wedge_reverse_sandwich_coord` etc.), `Reflect` (2), `G3` (3), `CrossStandardPosition`
(3), `Trig` (2 lagrange), `TrigEquiv` (1), `Rotation3D`/`Versor2D` (bisector — delicate). Leaves →
`obtain`-getters + `ring`/`ext`; composites → compose-object (atomic-`normSq` leaf where there's division);
delicate capstones last. Build green + stage per file.
