# Lift Lean theorem statements from coordinate tuples to geometric objects (corpus-wide sweep)

> **SUPERSEDED & ARCHIVED 2026-10-04 — folded into
> [[lean-object-in-getters-out-proof-style]]** (sibling: `lean-object-in-getters-out-proof-style.md`).
> This was the earlier "lift ~224 ℝ-arg *statements*" framing; once the maintainer clarified the intent as
> "geometric objects in, scalars in the body, geometric objects out," the two became the **same effort** and
> the object-in-getters doc carries the live per-file record, recipes, and final tier split. Kept here as the
> historical origin (the A/B/C judgment framework below is harvested into
> `tasks/reference/lean-ga-proof-architecture.md`). Outcome: polynomial tier DONE; coordinate core retained
> by decision. Do not resume from this doc — see the consolidated record.

## BLUF

Across `proofs/GacalcProofs/*.lean`, **~224 of 323 theorems take `ℝ` arguments** — many as raw vector
*coordinates* (`theorem wedge_is_antisym_part (u1 u2 v1 v2 : ℝ) …`). Where the `ℝ` args are a vector's
coordinates, the theorem should instead take the **geometric object** and be stated at the right
level. Per-theorem judgment (the maintainer's framework): **(A)** if it's a structural fact, take
objects and prove it **coordinate-free**; **(B)** else take the object, verify its type (`IsVector`),
and **pull out coordinates inside the proof** (`obtain ⟨…⟩ := ha; simp …; ring`); **(C)** keep `ℝ`
only where the args are genuinely scalars — a pure scalar identity, or an irreducible scalar
*parameter* (a rotation's `cos`/`sin`, a scalar multiple `k`, a versor's components). Most of the 224
are A/B candidates. "Done" = every A/B theorem lifted, callers updated, `make lean` green, and the
remaining `ℝ`-taking theorems are only genuine-scalar (C) cases.

**Status:** in progress — large incremental sweep (reopened 2026-10-03 from the first increment).
**Priority:** 5. **Difficulty:** 7 (scale + caller cascades).
**Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).
**See also:** `CLAUDE.md` › "Coordinates only when needed"; `tasks/reference/lean-ga-proof-architecture.md`
(leaf-vs-structural; the object→coord `obtain` bridge).

## The judgment framework (apply per theorem)

For each theorem with `ℝ` arguments, ask what each `ℝ` arg *is*:

- **A — coordinate-free object.** The fact is structural (holds by algebra: bilinearity, assoc,
  `IsVector`). State it `{a b : G_n} (ha : IsVector a) …` and prove with `rw`/property lemmas, no field
  access. Best outcome. Examples already in this form: `G3.mul_eq_dot_add_wedge`, `sandwich_*`
  property lemmas.
- **B — object-in, pull-coords.** The fact is geometric but the proof needs the coordinate
  computation. Take the object + `IsVector`, then `obtain ⟨hs, …⟩ := ha` and `simp only [defs, those
  field-zeros]; ring`. The *statement* speaks objects; only the proof touches coordinates. This is the
  pattern used for the perp/parallel lemmas (`cross_perp_left_dot`, `wedge_parallel_smul`, …).
- **C — genuine ℝ, keep.** Two sub-cases:
  - *Pure scalar identity* — no GA object in the statement at all: `Lagrange.lean`'s `lagrange_2d`,
    `lagrange_3d` (real polynomial identities). Keep exactly as `(… : ℝ)`.
  - *Scalar parameter* — the `ℝ` is a rotation `cos`/`sin`, a scalar multiple `k`, or a versor
    component, not a vector coordinate. Keep that `ℝ`; lift only the *vector* args (if any) to objects.
    E.g. `rotYZ_preserves_dot (c s : ℝ) (u v : G3)` is already right; `rotXY_vec (c s x y z : ℝ)`
    keeps `c s` and could take a vector object for `x y z` — but a theorem whose RHS is an explicit
    computed coordinate-vector (`= vec (c*x−s*y) …`) is a **coordinate-computation leaf**: keep it
    coordinate (stating it over an object RHS is awkward and adds nothing).

The test the maintainer gave: *does this require reals, or could it take geometric objects used
coordinate-free (A), or an object-then-pull-coords (B)?* Prefer A, then B; fall to C only for genuine
scalars.

**Realistic scope (sharpened 2026-10-03 after triaging Reflect/Normalize/Cross/Measures).** The raw
"~224 take ℝ" overstates the *convertible* set. A large fraction are **form D — coordinate
*formulas*** whose RHS is an explicit coordinate expression (`cross_vec`, `dual_vec`, `normSq_vec`,
`rotXY_vec`, `signedArea_eq`, …): the formula *is* the content, so they legitimately keep ℝ, and many
are heavily cited leaves (`cross_vec` has 6 callers, `normSq_vec` 31) — do NOT convert them. The
genuinely convertible set is the **structural/geometric facts (A/B)**. Two further frictions: (1)
many A/B facts *chain through* the D formula-leaves (`reflectVec_eq`→`reject_vec_eq`,
`area_sq_vec`→`normSq_wedge_vec`, `normSq_wedge_eq_lagrange`→`lagrange_property`) — to state those
over objects, bridge in the proof via `eq_vec_of_isVector`/`IsVector` field-zeros, or convert
bottom-up; (2) the `obtain …; simp [defs, field-zeros]; ring` pattern converts cleanly only when the
proof is a *self-contained* coordinate computation. So: convert the self-contained A/B facts first
(cheap, often uncited), then the chained A/B facts with the bridge, and leave D/C as coordinate.

## Inventory (ℝ-taking theorems per file, 2026-10-03)

`Sandwich` 37, `CrossStandardPosition` 20, `G3` 18, `ProjectionRotation3D` 16, `Rotation2D` 16,
`StandardPosition` 14, `ProjectionRotation2D` 13, `G2` 11, `Projection2D` 11, `AlgebraLaws` 8,
`Projection3D` 8, `Trig` 8, `Measures` 6, `Versor2D` 6, `Exp` 5, `RotateComponents` 5, `TrigEquiv` 5,
`Cross` 4, `Rotation3D` 4, `Contractions` 3, `Lagrange` 2 (both C), `Normalize` 2, `Reflect` 2,
`Predicates3D` 1, `StudentTrigForms` 1. (Re-derive with:
`awk '/^theorem /{h=1;b=""} h{b=b$0} /:= *by|:=$/{if(b~/: ℝ/)print FILENAME; h=0}' *.lean | sort | uniq -c`.)

## Method (large, cascade-aware — do it bottom-up, verify each step)

1. **Order bottom-up.** Converting a theorem's signature breaks its callers, so convert the leaves it
   rests on first, then the theorem, then its callers — or convert a theorem and fix all citers in the
   same step. Check citers first: `grep -rn '\bNAME\b' *.lean`.
2. **Per file / small batch:** apply the A/B/C judgment, rewrite signatures + proofs, update every
   citer, then `make lean` (`proofs/check.sh`) green before moving on. Never leave the tree red.
3. **Scalar params stay ℝ** (don't try to objectify a rotation's `cos`/`sin`); only vector-coordinate
   args become objects.
4. **Keep the dot/wedge primitive**; an object theorem drops to coordinates once via `obtain`.

## Progress

- **Increment 1 (done, archived content folded in):** the perpendicularity/parallelism facts were
  lifted to object-level + nonzero-guarded, and their `_dot`/wedge helpers (`dual_perp_dot`,
  `reject_perp_dot`, `cross_perp_left_dot`/`_right_dot`, `dual_wedge_perp_left_dot`/`_right_dot`,
  `wedge_parallel_smul`, `proj_plane_perp_normal_dot`) made object-level (form B). The student-facing
  `StudentTrigForms.lean` theorems are object-level. `make lean` green.
- **Increment 2 (done 2026-10-03, `make lean` green):** `G2.lean`'s dot/wedge-part theorems
  `dot_is_sym_part`, `wedge_is_antisym_part`, `dot_eq_coord_sum` → form B (`{a b : G2}` + `IsVector`,
  coords pulled in the proof). These had no code callers (only docstring mentions, names unchanged), so
  no cascade. Left coordinate for now: `vec_mul` (it sits *before* `IsVector` in the file — needs a
  reorder — and is the product-in-coordinates bridge, borderline C/D), `normSq_vec` (31 callers —
  defer with care), `reverse_vec` (2 callers; the object form `reverse_of_isVector` already exists),
  `dual_vec`/`dual_vec_perp` (coordinate leaves under the object forms), `vec_eq_smul`/
  `eq_vec_of_isVector` (the bridge itself).
- **Judgment framework extracted (2026-10-03):** the A/B/C rule is now durable in
  `tasks/reference/lean-ga-proof-architecture.md` › "Coordinates only when needed", referenced from
  `CLAUDE.md`.
- **Increment 3 — `Cross.lean` (done, green):** `cross_anticomm_vec` → `cross_anticomm`
  (`{a b} IsVector`), `dot_cross_eq_signedVolume` → `{a b c} IsVector` (form B). Kept `cross_vec`
  (6 callers) and `dual_vec` as form-D coordinate formulas.
- **Increment 4 — `Contractions.lean` (done, green):** `leftContraction_vec_vec`,
  `rightContraction_vec_vec` → `{a b} IsVector`; `leftContraction_scalar_vec` → `(α : ℝ) {b} IsVector`
  (α is a scalar parameter — stays `ℝ`). All form B.

## Where the sweep stands (2026-10-03) — the clean tier is exhausted; remaining is keeps + a hard tier

After triaging `Exp`/`TrigEquiv`/`Versor2D`/`AlgebraLaws`/`Trig`/`Rotation3D`/`RotateComponents`, the
raw "~224 take ℝ" resolves into:

- **Already form A — no work:** `AlgebraLaws`'s `mul_assoc`/`mul_add`/`one_mul`/`smul_mul`/… already
  take `(a b c : G_n)` objects (the `ℝ` is only the scalar `k`).
- **C — keep (scalars/angles/identities):** `exp`'s angle `θ`, `uvec`'s angle `α`/`β`,
  `lagrange_property`/`lagrange_2d/3d`, `cos_sq_add_sin_sq`, the `smul k` parameter, versor components.
- **D — keep (coordinate FORMULAS, heavily-cited leaves):** `normSq_vec` (31 callers), `cross_vec`
  (6), `dot_vec`, `magnitude_sq_vec` (6), `rotXY_vec`, `signedArea_eq`, `dual_vec` — RHS *is* the
  coordinate expression; converting them is wrong.
- **Hypothesis-side `(h : dot = 0)`:** `vec_anticomm_perp`, `mul_eq_wedge_of_perp`, … → the separate
  `tasks/prefer-sine-cosine-presentation-followups.md`.
- **The CAPTURED clean A/B tier:** the perp/parallel facts + G2 dot/wedge-part + `Cross` + `Contractions`
  (increments 1–4). This was the self-contained, uncited, no-cascade set — now done.
- **The HARD cascaded tier (remaining real work):** geometric facts stated over vector coordinates
  AND versor-component scalars, with many callers — `versor_mul_from_eq_bisector`/`from_mul` (G2: 7+5
  callers; G3 twins), `sandwich_preserves_cos/sin`, `rotation_fixes_plane/normal/perp`,
  `sandwich_ahat`, `reflectVec_eq`, `area_sq_vec`, `normSq_wedge_eq_lagrange`,
  `sin_between_eq_abs_signed_vec`, and the `Sandwich`/`StandardPosition`/`ProjectionRotation` bodies.
  These need (a) possibly an **`IsVersor`/object-versor** predicate (several take `evenVersor s c12 …`
  components), (b) bridging through the D formula-leaves, and (c) updating many call sites — a
  deliberate **bottom-up sub-project**, not quick grinding. Recommend tackling it per cascade-cluster
  (or deciding some are genuinely coordinate-computational and stay D).

**Net:** the easy, safe conversions are captured and green. The remainder is either a legitimate
keep (the large majority) or the hard cascaded tier above, which is distinct, careful work.

## Increment 5 — the `versor_mul` cascade cluster (done 2026-10-03, `make lean` green)

First hard-tier cluster. Converted the four bisector-identity theorems to object form:
`versor_mul_from_eq_bisector` / `from_mul_versor_eq_bisector` in **both** `Versor2D.lean` (G2) and
`Rotation3D.lean` (G3) now take `{fromV toV : G_n} (hf : IsVector fromV) (ht : IsVector toV)`. Pattern
used (the reusable **cascaded-cluster recipe**): keep the coordinate proof verbatim as a `_coord`
leaf; the object theorem bridges with `have h := …_coord fromV.c1 … toV.c3; rwa [← eq_vec_of_isVector
hf, ← eq_vec_of_isVector ht] at h` (rewriting the concrete `vec …` back to the object — the `←`
direction avoids the forward-rewrite motive problem). Added `G2.isVector_vec` (G3 already had it).
Updated the 5 real call sites (`Sandwich.lean` ×4, `ProjectionRotation3D.lean` ×1) to pass
`isVector_vec …` proofs. `make lean` green.

**Process note (lesson):** verify `make lean` by reading check.sh's `[lean] OK`/`FAILED` line or its
real exit code — NOT a `… | grep | tail` whose trailing `[exited with code 0]` is the *pipeline's*
exit and masks a failed build. (This masked a broken `Contractions.lean` `ext <;> ring` — simp already
closed the goal — caught and fixed here.)

## Increment 6 — `Measures.lean` G3 geometric facts (done 2026-10-03, `make lean` green)

`area_sq_vec`, `normSq_wedge_eq_lagrange`, `normSq_wedge3_eq_signedVolume_sq`, `volume_sq_vec` →
`{a b [c] : G3} IsVector` (form B). Self-contained ones via `obtain`+`simp`+`ring`
(`normSq_wedge3`); chained ones bridge to the kept D-leaves — `area_sq_vec` to `normSq_wedge_vec`
(forward `rw [eq_vec_of_isVector …]` inside the `0 ≤ …` side goal), `normSq_wedge_eq_lagrange` to
`lagrange_property` (`rw [← eq_vec_of_isVector …] at h; linarith`). Both `normSq_wedge3` citers were
in-file (`volume_sq_vec`), updated. **Kept form D:** `signedArea`/`signedArea_eq`/`signedArea_sq` (the
2D signed-area *formula*), `normSq_wedge_vec`, `lagrange_property` (coordinate leaves bridged to).

## Increment 7 — `Reflect.lean` (done 2026-10-03, `make lean` green)

`reflectVec_eq`, `normSq_reflectVec` → `{d v : G3} IsVector` + `normSq d ≠ 0` (form B). Both chain
(through `reject_vec_eq`/`proj`/`normSq_vec`), so used the cascaded recipe: kept the coordinate proofs
verbatim as `reflectVec_eq_coord`/`normSq_reflectVec_coord`, object forms bridge via
`rwa [← eq_vec_of_isVector …] at h` — and the `normSq … ≠ 0` **hypothesis** bridges with
`(by rw [← eq_vec_of_isVector hd_isv]; exact hd)`. Both were uncited externally.

## Increment 8 — `TrigEquiv.lean` `sin_between_eq_abs_signed_vec` (done 2026-10-03, `make lean` green)

Cascaded form B. `sin_between_eq_abs_signed_vec (a1 a2 b1 b2 : ℝ)` → kept verbatim as
`sin_between_eq_abs_signed_vec_coord`; added object `{a b : G2} (ha hb : G2.IsVector)` bridging via
`rwa [← G2.eq_vec_of_isVector ha, ← G2.eq_vec_of_isVector hb] at h`. The sole caller `sin_between_uvec`
rewrites `uvec → vec` then applies the *coord* lemma, so it was repointed to
`sin_between_eq_abs_signed_vec_coord` (no object bridge needed there — it already has coordinate vecs in
hand). `signed_sin_between_uvec` is form C (genuine angle parameters α, β — stays ℝ).

## Increment 9 — `RotateComponents.lean` all 5 (done 2026-10-03, `make lean` green)

Here the `(a1 a2 a3 b1 b2 b3 …)` args are **vector** coordinates — `a`, `b` are the two vectors that
define the rotation plane (`versorFromVectors a b`), and `u`, `v` are vectors acted on — so these are
form B, *not* the C-keep "versor components". All 5 are uncited (Stage-1 building blocks). Converted:
- `sandwich_ahat` → `{a b : G3} IsVector` + `magnitude a/b ≠ 0` (`_coord` leaf + `rwa [← eq_vec …]` bridge).
- `rotation_fixes_plane_bivector` → `{a b} IsVector`, RHS `wedge b a` (`_coord` leaf + bridge).
- `rotation_preserves_dot` → `{a b u v} IsVector` (`_coord` leaf + bridge).
- `rotation_fixes_normal` → `{a b} IsVector`, acted-on vector restated coordinate-free as the cross
  product **`cross b a`** (= the explicit normal `vec (b2*a3−b3*a2) (−(b1*a3−b3*a1)) (b1*a2−b2*a1)`,
  verified against `cross_vec`). `_coord` leaf + bridge; the `−(x−y)` vs `cross_vec`'s `y−x` sign is
  reconciled by a one-line scalar `ring` (`hsign`) rather than an 8-component `ext` (which emitted
  non-fatal `info` spam — avoided). Added `import GacalcProofs.Cross`.
- `rotation_fixes_perp` → `{a b} IsVector` + scalar `k`, RHS `smul k (cross b a)`; pure object proof
  `rw [sandwich_smul, rotation_fixes_normal ha hb hr]` (linearity over the object normal — no `_coord`).

This resolves the normal/perp pair that was first scoped as a deferral: the `cross`-object restatement is
the right coordinate-free form, and the sign reconciliation is a one-liner.

## Increment 10 — `IsEvenVersor` foundation (done 2026-10-03, `make lean` green)

Open Q2 resolved **(a) lift them** (maintainer, 2026-10-03: "I'd like to not take reals, and I think we can
make this work"). Terminology: gacalc/Python calls an even multivector a **versor**; a **rotor** is a *unit*
versor — so the predicate is `IsEvenVersor`, with no magnitude constraint. Added to `Sandwich.lean` for both
algebras:
- `IsEvenVersor (R : G2) := R.c1 = 0 ∧ R.c2 = 0`; `IsEvenVersor (R : G3) := R.c1=0 ∧ R.c2=0 ∧ R.c3=0 ∧ R.c123=0`.
- `eq_evenVersor_of_isEvenVersor : R = evenVersor R.s R.c12 [R.c13 R.c23]` (bridge, modeled on
  `eq_vec_of_isVector`), and `isEvenVersor_evenVersor` (companion, like `isVector_vec`).

A unit-rotor layer (so the sandwich can use **reverse** instead of **inverse**, `R v R̃`) is the separate
follow-up `tasks/lean-unit-versors-rotors-sandwich-with-reverse.md`.

## Increment 11 — the `evenVersor`-component `sandwich_preserves_*` family → object versors (done 2026-10-03, `make lean` green)

Lifted the whole family to `{R : G_n} (hR : IsEvenVersor R) (hr : normSq R ≠ 0)` + `IsVector` operands,
coordinate proofs kept verbatim as `_coord` leaves, object forms bridged via
`rwa [← eq_evenVersor_of_isEvenVersor hR, ← eq_vec_of_isVector …] at h` (and the `normSq R ≠ 0` hypothesis
with the by-term reverse rewrite). Converted:
- `Sandwich.lean`: G2 + G3 `sandwich_preserves_dot`, `sandwich_preserves_normSq_of_vec`,
  `magnitude_sandwich_vec`; G3 `sandwich_preserves_wedge`, `sandwich_preserves_normSq_of_wedge`,
  `sandwich_evenVersor_vec_isVector` (no `normSq ≠ 0` needed), `sandwich_comp` (two versors `R1 R2`, `v`
  stays a free object).
- `Projection2D.lean`: G2 `sandwich_preserves_wedge`, `sandwich_preserves_normSq_of_wedge`.
- `Trig.lean`: G2 + G3 `sandwich_preserves_cos`, `sandwich_preserves_sin`.
- Callers repointed to `_coord`: the in-`Sandwich` `magnitude_sandwich_vec_coord` bodies, every `Trig`
  `cos`/`sin` `_coord` body, and `RotateComponents.rotation_preserves_dot_coord`.

**Kept coordinate (internal leaves / form D):** `normSq_evenVersor`, `normSq_reverse_sandwich(_wedge)`,
`wedge_reverse_sandwich`, `normSq_biv`/`_triv`, `mul_biv`/`_triv_*`, `versorFromVectors_*`,
`versorFromVectors_eq_evenVersor` (the a→b↔evenVersor bridge), `normSq_mul`/`inverse_mul`, and the
own-plane/own-normal/plane-restricted lemmas `sandwich_fixes_own_bivector`/`_normal`,
`sandwich_fixes_orthogonal`/`sandwich_plane_invariant` (the user-facing object forms of the first two are
`rotation_fixes_*` in `RotateComponents`, done in Increment 9; the plane-restricted pair takes a
*constrained* versor `evenVersor s c12 0 0`, lower value).
## Increment 12 — `ProjectionRotation2D.lean` 4 user-facing theorems (done 2026-10-03, `make lean` green)

**Applies the maintainer's 2026-10-03 feedback** ("still looks like you are adding lots of reals instead of
geometric objects"): minimize new reals-taking symbols. The 4 user-facing results — `projRotation_eq_vec_mul`,
`projRotation_carries_from_to`, `projRotation_isometry`, `projRotation_eq_sandwich` — are now object-form
(`{f t v : G2} IsVector` + `normSq ≠ 0`). Only **one** new `_coord` symbol was minted: `projRotation_eq_vec_mul_coord`,
**shared by the other three proofs** (justified). The other three are object wrappers whose proofs
`rw [eq_vec_of_isVector …]` to drop to coordinates and then reuse `projRotation_eq_vec_mul_coord` + the
**pre-existing** internal leaves (`mul_vec_self`, `reject_plane_eq_zero`, `magnitude_sq_of_normSq`,
`normSq_mul_three_vec`, `fhat_that_eq_reverse_mul_inverse`) — no new reals symbols for those three. The
internal computation leaves stay coordinate: they are the irreducible layer (esp. the √-bearing versor
identities `key_reverse_sq`/`fhat_that_eq_reverse_mul_inverse`, which have no coordinate-free proof here).

The calibration (**A → inlined-B → named `_coord` only when shared by ≥2 callers**) is now recorded in
`tasks/reference/lean-ga-proof-architecture.md` (the B bullet).

## Increment 13 — `ProjectionRotation3D.lean` 3 user-facing theorems (done 2026-10-03, `make lean` green)

`projRotation_carries_from_to`, `projRotation_isometry`, `projRotation_eq_sandwich` → object-form
(`{f t v : G3} IsVector` + `normSq f/t ≠ 0`, plane `normSq (wedge f t) ≠ 0`, and for the capstone
`normSq (versorFromVectors f t) ≠ 0`). `projRotation_perp` already took objects. Unlike the 2D twin
(Increment 12), these three proofs are **long and delicate** — orthogonality cores (`inplane_perp_reject`,
`project_perp_reject`), `set`/`calc`, and `set_option maxHeartbeats` bumps — so per the calibration's
delicate-proof exception each coordinate proof is kept **verbatim** as a `_coord` leaf with a thin object
bridge (`rwa [← eq_vec_of_isVector …] at h`); inlining would have put the eq_vec rewrites and hypothesis
bridges through those fragile `field_simp; ring` cores. All three were uncited (only cross-referenced in
2D comments). The pre-existing warnings in the `_coord` bodies (unused `hn`, a no-op `ring`) are unchanged
and not introduced here.

## Increment 14 — `StandardPosition.lean` (done 2026-10-03, `make lean` green)

Most of this file was **already object-form** and needed no change: `rotXY_smul`/`rotXY_sub`/`rotXZ_smul`,
`rotXY_preserves_dot`/`rotXZ_preserves_dot`, `proj_rotXY_equivariant`/`proj_rotXZ_equivariant`,
`vecReject_rotXY_equivariant` all take `u v a b : G3` objects — their `(c s : ℝ)` are genuine rotation
cos/sin parameters (C-keep), not vector coordinates. Converted the two versor-free geometric-product
results to object form with **inlined** proofs (no new `_coord` symbols, per the maintainer's reduce-reals
feedback): `mul_proj_eq_dot` (`a (proj_a b) = (b·a)·1`) and `mul_eq_proj_dot_add_reject_wedge`
(`a b = (a·b)·1 + a∧b`, built from project/reject) → `{a b : G3} IsVector` + `normSq a ≠ 0`; each drops to
coords via `eq_vec_of_isVector` and reuses the existing coordinate helpers (`mul_vec_self`,
`dot_self_vec_eq_normSq`, `plane_eq_wedge`), with `mul_eq_…` calling the now-object `mul_proj_eq_dot` via
`isVector_vec`.

**Kept coordinate (coords genuinely needed in the statement):** `rotXY_aligns_xy`/`rotXZ_aligns_xz`/
`rotate_b_to_e1`/`rotate_b_to_e1_magnitude` — these rotate `b` onto the x-axis using cos/sin that *are*
`b`'s own coordinates (`b1/k`, `−b2/k`, …), so the statement is intrinsically about `b`'s components; and
the pure computation leaves `mul_vec_self`/`dot_self_vec_eq_normSq`/`plane_eq_wedge` (in `G3`/`Projection3D`).

## Increment 15 — `Projection3D.lean` `reject_vec_eq` (done 2026-10-03, `make lean` green)

Converted the user-facing Hestenes-rejection identity `reject_a b = b − proj_a b` to object form
(`{a b : G3} IsVector` + `normSq a ≠ 0`); kept the non-trivial proof verbatim as `reject_vec_eq_coord`
(externally cited by `Reflect.reflectVec_eq_coord`, which was repointed to `_coord`) with a thin object
bridge. The other vector-ish helpers here stay coordinate as internal computation leaves: `wedge_reject`
(feeds `plane_eq_wedge`), `mul_vec_inverse_self` (feeds `reject_vec_eq_coord`), `plane_eq_wedge` itself
(shared across `StandardPosition`/`Measures`). The already-object theorems need no change: `reject_perp_dot`,
`dual_wedge_perp_left/right_dot`, `proj_plane_perp_normal_dot`, `add_eq_left_sub`.

## Increment 16 — `IsBivector` + the plane-projection cluster (done 2026-10-03, `make lean` green)

Open Q3 resolved **(a) yes** (maintainer, 2026-10-03). Added `IsEvenVersor`'s sibling to `G3.lean`:
`IsBivector (B : G3) := B.s = 0 ∧ B.c1 = 0 ∧ B.c2 = 0 ∧ B.c3 = 0 ∧ B.c123 = 0` (grade-2), bridge
`eq_bivector_of_isBivector : B = bivector B.c12 B.c13 B.c23`, companion `isBivector_bivector`. Lifted the
plane-projection cluster in `Projection3D.lean` to object form:
- `project_add_reject`, `reject_eq_proj_normal`, `project_eq_sub_reject` → `{B : G3} (hB : IsBivector B)
  (hBn : normSq B ≠ 0)` + a vector object, bridging through `_coord` leaves.
- `proj_plane_eq_project_onto` → `{a b c : G3} IsVector` (its plane is `wedge a b`, so vectors suffice),
  **inlined** — drops to coords and reuses `reject_eq_proj_normal_coord`/`project_eq_sub_reject_coord`,
  no `_coord` symbol minted.
- `_coord` leaves are justified-shared: `project_add_reject_coord` by `ProjectionRotation3D` (×2, repointed)
  + `project_eq_sub_reject_coord`; the reject/project `_coord` by the inlined `proj_plane_eq_project_onto`.

Kept coordinate (the irreducible plane-computation leaves): `project_onto`/`reject`/`inner_vb`/`proj`/`proj_plane`
defs, `mul_vec_inverse_self`, `wedge_reject`, `plane_eq_wedge`, and the `ProjectionRotation3D` scaffold
(`project_onto_in_plane_self`, `inner_vb_mul_reverse_self`, orthogonality cores) — all form-D/√-structural.

## Increment 17 — final sweep (`cos_sq_add_sin_sq`, `Normalize`) (done 2026-10-03, `make lean` green)

A `git diff master..HEAD` review (maintainer ask) surfaced four missed vector-coordinate theorems, now
object-form (inlined, uncited → no new reals symbols):
- `Trig.cos_sq_add_sin_sq` (G2 **and** G3) — the Pythagorean angle identity `cos² + sin² = 1` for two
  vectors → `{a b : G_n} IsVector` + `normSq a/b ≠ 0`. (The `cos_sq_add_sin_sq` in `TrigEquiv`/`Exp`/
  `Rotation2D` is Mathlib's `Real.cos_sq_add_sin_sq` via `open Real`, not ours — ours was uncited.)
- `Normalize.normSq_normalizeVec` / `magnitude_normalizeVec` — "normalize gives unit length" → `{a : G3}
  IsVector` + `normSq a ≠ 0`.

**Verified non-gaps (checked, correctly left coordinate):** `G2.dual_vec_perp` already has the object
companion `dual_perp` (StudentTrigForms) and is a documented bridge; `lagrange_2d`/`lagrange_3d` and
`lagrange_property` are pure/Lagrange identities (the object `normSq_wedge_eq_lagrange` already sits on
`lagrange_property`); `sandwich_fixes_own_bivector`/`_normal` are internal leaves whose object forms are
`RotateComponents.rotation_fixes_*` (done Inc 9); `sandwich_fixes_orthogonal`/`plane_invariant` take a
*constrained* plane versor (lower value).

**One latent item (NOT this sweep — a def redesign):** `Exp.normSq_expBivectorGeneral (p q r)` is
coordinate-*parameterized* because `expBivectorGeneral` is **defined** on `(p q r)`, not on a bivector
object (cf. `rotate_b_to_e1`, defined by `b`'s coords). Making it object needs redefining the `exp`
function to take an `IsBivector` object — a def change, out of scope for lifting theorem *statements*.
Candidate follow-up, noted not done.

## Increment 18 — second diff-review sweep (`wedge_antisymm`, `vec_anticomm_perp`) (done 2026-10-03, `make lean` green)

A second `git diff master..HEAD` review (maintainer ask) found two more vector-coordinate geometric facts
that lacked object companions (their duals/siblings were already object — `cross_anticomm`,
`mul_eq_wedge_of_perp`):
- `wedge_antisymm` (G2 **and** G3) — `a∧b = −(b∧a)` for vectors → `{a b : G_n} IsVector` (inlined).
- `vec_anticomm_perp` **G3** — perpendicular vectors anticommute (`u·v = 0 ⟹ uv = −(vu)`) →
  `{a b : G3} IsVector (h : dot a b = 0)`, now a fully **coordinate-free (form A)** proof:
  `rw [mul_eq_wedge_of_perp ha hb h, mul_eq_wedge_of_perp hb ha hba, wedge_antisymm ha hb]`.

**`vec_anticomm_perp` G2 stays coordinate — a genuine layering constraint, not an oversight:** `G2.dot`
lives in `Versor2D.lean`, which is imported *above* `AlgebraLaws.lean` where this lemma sits, so the G2
lemma at this layer cannot state a `dot u v = 0` hypothesis (hence its raw `u1*v1+u2*v2 = 0`). Relocating
it to the dot layer would be the follow-up; it is uncited.

### Exhaustive final audit (all non-`_coord` reals theorems classified)

After a definitive scan (every object-equality conclusion on `vec`-literals, every operator), the remaining
reals-taking theorems are ALL justified:
- **Bridge/computation leaves (form D)** — `normSq_vec`, `dot_vec`, `cross_vec`, `dual_vec`, `mul_vec_self`,
  `dot_self_vec_eq_normSq`, `wedge_vec_eq_biv`, `normSq_wedge_vec`, `vec_mul`, `vec_eq_smul`, `reverse_vec`,
  `wedge_self_vec` (`a∧a=0`; G3's feeds `wedge_reject`), `signedArea_eq/sq`, `magnitude_sq_vec`,
  `vec_mul_mul_self`, `reject_from_I_eq_zero`, `vec_wedge_I_eq_zero`, `plane_eq_wedge`, `wedge_reject`,
  `mul_vec_inverse_self`, `vec_mul_eq_dot_add_wedge`/`vec_mul_perp`/`dual_vec_perp` (object companions
  `mul_eq_dot_add_wedge`/`mul_eq_wedge_of_perp`/`dual_perp` exist), and the versor/√-structural plane
  leaves (`normSq_evenVersor`, `normSq_reverse_sandwich(_wedge)`, `versorFromVectors_*`, `normSq_biv/triv`,
  `mul_biv/triv_*`, `key_reverse_sq`, `inplane_perp_reject`, `plane_pythagorean`, …).
- **Scalar-parameter / linearity (C-keep)** — everything with a `k`/`c`/`s`/`m` scalar arg: `*_smul`,
  `*_add`/`*_sub` (object operands), `sandwich_smul`, the `rotXY/rotXZ_*` family, `one_smul`.
- **Pure/Lagrange identities (C-keep)** — `lagrange_2d/3d`, `lagrange_property`.
- **Companion helpers** — `isVector_vec`, `isBivector_bivector`, `isEvenVersor_evenVersor`.
- **Coordinate-parameterized defs (def-redesign, not statement-lift)** — `rotXY_aligns_xy`/
  `rotate_b_to_e1(_magnitude)` (cos/sin ARE `b`'s coords), `Exp.normSq_expBivectorGeneral`
  (`expBivectorGeneral` defined on `(p q r)`). Noted as follow-ups.
- **Internal leaves with object forms at the user layer** — `sandwich_fixes_own_bivector/_normal`
  (→ `rotation_fixes_*`), `sandwich_fixes_orthogonal/plane_invariant` (constrained plane versor).
- **`G2.vec_anticomm_perp`** — layering (above).
- **Separate task** — all of `CrossStandardPosition.lean` (`tasks/lean-cross-standard-position-capstone.md`).

**Conclusion: the statement-lifting sweep is exhaustively complete.** Every remaining `ℝ` is either the
irreducible coordinate foundation, a genuine scalar/identity, a companion helper, a coordinate-parameterized
def (needs a def redesign, not a lift), or the separately-tracked capstone.

## Increment 19 — third diff-review sweep (`sandwich_carries_from_to`) (done 2026-10-03, `make lean` green)

A third `git diff master..HEAD` review (maintainer ask), this time via a **complete categorized dump of
every non-`_coord` reals theorem** (full statements, all operators), found one more user-facing miss:
- `sandwich_carries_from_to` (G2 **and** G3) — "the versor from `a`,`b` carries `a` to `b`:
  `R a R⁻¹ = (|a|/|b|)·b`" → `{a b : G_n} IsVector` + `magnitude b ≠ 0` + `normSq (versorFromVectors a b) ≠ 0`.
  Its proof is delicate (bisector assembly, `field_simp`), so kept verbatim as `_coord` + object bridge; the
  sole `rw` caller `RotateComponents.sandwich_ahat_coord` was repointed to `_coord` (G2 version was uncited).

With this, the audit is confirmed exhaustive: the remaining object-conclusion-over-vectors theorems are all
**internal plumbing** (`versorFromVectors_mul_reverse`/`_inverse` — `rw` steps inside the delicate
`sandwich_carries_from_to_coord`/route-equivalence proofs; the bisector leaves; `sandwich_fixes_own_*` whose
object forms are `rotation_fixes_*`), or the justified buckets below.

## Increment 20 — fourth diff-review: audit stable, no top-level miss (2026-10-03)

A fourth `git diff master..HEAD` review (maintainer ask), via a complete dump of every non-`_coord`
reals theorem **including Prop/predicate conclusions** and the previously-unopened files (`Predicates2D/3D`,
`StudentTrigForms`, `GradeProjection`, `G1`, `Contractions`, `Rotation2D`), found **no top-level
user-facing result still taking coordinates** — the first clean pass (Increments 17–19 each had found one:
`cos_sq_add_sin_sq`, `wedge_antisymm`/`vec_anticomm_perp`, `sandwich_carries_from_to`). No code change.

Confirmed justified: `Rotation2D` is the **angle-parameterized** layer (`θ/α/β` angle scalars; `rot θ (x,y)`
acts on `ℝ×ℝ` pairs — a different representation, not G-vectors); `Predicates*`/`StudentTrigForms`/
`Contractions` are already object (their `ℝ` are genuine `k`/`α` scalars).

### Open decision — objectify the internal SCAFFOLD layer, or keep it coordinate?

The remaining vector-coordinate theorems whose *statements* could still be objectified are all **internal
scaffold / plumbing** whose user-facing deliverables are already object: `plane_pythagorean`,
`project_perp_reject`, `inplane_perp_reject`, `project_onto_in_plane_self`, `reject_in_plane_self`,
`wedge_vec_wedge_self`, `inner_vb_mul_reverse_self`, `normSq_mul_vec`, the bisector identities
(`normalizeVec_to_mul_versor_eq_bisector`, `vec_mul_bisector_eq`, `normalizeVec_mul_versor_eq_reverse`),
`versor_mul_project_eq`/`versor_mul_reject_comm` (ProjectionRotation3D); the PR2D √-route lemmas
(`key_reverse_sq`, `fhat_that_eq_reverse_mul_inverse`, `versorFromVectors_mul_vec_eq`,
`reverse_versorFromVectors_mul`, `normSq_mul_three_vec`); `versorFromVectors_mul_reverse`/`_inverse`,
`sandwich_fixes_own_bivector`/`_normal` (Sandwich); `vec_mul_mul_self` (Rotation3D).
- **Keep coordinate (recommended):** no reader cites them (the deliverables — `projRotation_*`,
  `sandwich_carries_from_to`, `rotation_fixes_*` — are object), their proofs are delicate (√-structural
  `field_simp`), and objectifying would mint ~15–20 new `_coord` reals symbols — the "lots of reals" the
  maintainer flagged. This is the **form-D / computation-layer** bucket.
- **Objectify (maximal purity):** every geometric *statement* object-form, accepting the extra `_coord`
  leaves. `plane_pythagorean` is the most standalone (a natural first if a partial pass is wanted).

**Status: awaiting the maintainer's call; default is keep-coordinate.** The form-D bridge leaves
(`normSq_vec`, `dot_vec`, `cross_vec`, `mul_vec_self`, …), scalars/identities/companions, the
coordinate-parameterized defs (`rotate_b_to_e1`, `Exp.*`), and the `CrossStandardPosition` capstone are
**not** part of this decision — they stay coordinate unconditionally.

### DECISION: objectify the scaffold (maintainer, 2026-10-03 — "yes, if they objectify without breaking the proofs")

Method per lemma: keep the delicate proof verbatim as `_coord`, add an object wrapper bridging via
`rwa [← eq_vec/eq_bivector/eq_evenVersor …] at h`, repoint the (coordinate) callers to `_coord`. The object
statement must be **free of bare coordinate arithmetic** after lifting (else it is form-D and stays).
Predicates used: `IsVector`, `IsEvenVersor`, `IsBivector` (all already exist).

**DONE (Increment 21, 2026-10-03, `make lean` green).** All listed scaffold lemmas are now object-form:
each coordinate proof kept verbatim as `_coord`, an object wrapper added bridging via
`rwa [← eq_vec/eq_bivector/eq_evenVersor …] at h`, and every (coordinate) caller repointed to `_coord`.
The mechanical rename+repoint was done by `tasks/adhoc/lean-lift-scaffold/rename_to_coord.py` (whole-word
`\bNAME\b` → `NAME_coord` on code lines, docstrings skipped); the object wrappers were added by hand.
`G3.mul_vec_self` and the other form-D bridge leaves were deliberately left coordinate (see below).
- **Mistake made + fixed within this unit:** the codemod was not idempotent — a second run re-matched the
  new wrapper defs (`theorem NAME {…}`) and appended `_coord`, colliding with the leaves (32 lines). Caught
  by the convention's "run twice, expect zero changes" check; reverted the 32 wrapper defs (uniquely
  identifiable as `theorem NAME_coord` lines containing `{`) and added a single-use guard to the codemod
  (refuses once the "Object-form wrappers" blocks exist). Rebuilt green after the revert.

**Objectified (Increment 21), by file:**
- **`ProjectionRotation3D`** (13): `plane_pythagorean`, `project_perp_reject`, `inplane_perp_reject`,
  `project_onto_in_plane_self`, `reject_in_plane_self`, `wedge_vec_wedge_self`, `inner_vb_mul_reverse_self`,
  `normSq_mul_vec` (→ `(M : G3) {a} IsVector`), `normalizeVec_to_mul_versor_eq_bisector`,
  `vec_mul_bisector_eq`, `normalizeVec_mul_versor_eq_reverse`, `versor_mul_project_eq`,
  `versor_mul_reject_comm` (all over `{a b [c] : G3} IsVector`).
- **`ProjectionRotation2D`** (8): `mul_vec_self` (G2 local), `reject_plane_eq_zero`,
  `magnitude_sq_of_normSq`, `normSq_mul_three_vec`, `versorFromVectors_mul_vec_eq`,
  `reverse_versorFromVectors_mul`, `key_reverse_sq`, `fhat_that_eq_reverse_mul_inverse`.
- **`Rotation3D`** (1): `vec_mul_mul_self` (→ `{a b} IsVector`, `= smul (normSq a) b`). (`magnitude_sq_vec`
  stays — RHS `a1²+a2²+a3²` is form-D.)
- **`Sandwich`** (≈10): `versorFromVectors_mul_reverse` (G2+G3), `versorFromVectors_mul_inverse` (G3),
  `mul_biv_reverse_self`/`mul_biv_inverse_self` (→ `{B} IsBivector`), `normSq_reverse_sandwich` (G2+G3),
  `normSq_reverse_sandwich_wedge` (G2+G3), `wedge_reverse_sandwich` (G2+G3) (versor ones → `{R} IsEvenVersor`
  + `{v}/{u v} IsVector`).

**Deliberately NOT objectified (stay coordinate, with reason):**
- **G3 core bridge leaves** (`mul_vec_self`, `normSq_vec`, `dot_vec`, `cross_vec`, `dual_vec`,
  `wedge_vec_eq_biv`, `dot_self_vec_eq_normSq`, `normSq_wedge_vec`, `magnitude_sq_vec`, …) — form-D (RHS is
  coordinate arithmetic) and/or the widely-used foundation; converting is circular and high-blast-radius.
- **`sandwich_fixes_own_bivector`/`_normal`** — the acted-on bivector/normal is the versor's *own* grade-2
  part (built from the same `s p q t`); the object deliverables are `rotation_fixes_plane_bivector`/`_normal`
  (already object, Inc 9).
- **`mul_triv_reverse_self`/`mul_triv_inverse_self`/`normSq_triv`** — would need a new `IsTrivector`
  predicate for a single pseudoscalar coordinate; marginal, deferred (add `IsTrivector` only if wanted).
- **`versorFromVectors_eq_evenVersor`** — RHS is the versor's components as explicit coordinate formulas
  (form-D bridge).

## Increment 22 — remaining cleanly-objectifiable leaves (done 2026-10-03, `make lean` green)

Maintainer (2026-10-03): "do all the rest you can … objectify stuff and make calls on their coordinates …
take a vector as input, use getters" — broad discretion while away. Objectified every remaining leaf whose
object form is a genuine improvement (RHS is object ops, or a new predicate completes the family), keeping
the pure coordinate-unfold bridges coordinate (see below).
- **New predicate `IsTrivector`** (G3.lean) + `eq_trivector_of_isTrivector` + `isTrivector_trivector` —
  completes the grade family (`IsVector`/`IsBivector`/`IsTrivector`).
- **Sandwich:** `mul_triv_reverse_self`, `mul_triv_inverse_self` → `{T : G3} IsTrivector`;
  `sandwich_fixes_own_bivector`/`_normal` → `{R : G3} IsEvenVersor` with the plane/normal via R's getters
  (`bivector R.c12 R.c13 R.c23`, `vec R.c23 (-R.c13) R.c12`).
- **Trig:** `lagrange_property` (G2+G3) → `{a b} IsVector : dot a b ^2 + normSq (wedge a b) = normSq a * normSq b`.
- **G3.lean core self-product leaves:** `mul_vec_self` (`mul a a = smul (normSq a) one`),
  `dot_self_vec_eq_normSq` (`dot a a = normSq a`), `wedge_self_vec` (`wedge a a = zero`; G2 twin too) →
  `{a} IsVector`. Wrappers placed at the end of the G3 namespace (the leaves predate `IsVector`); callers
  (Projection3D/Reflect/StandardPosition/ProjectionRotation3D, ≤5 each) repointed to `_coord`.

## Increment 23 — `CrossStandardPosition` cross-equivariance (done 2026-10-03, `make lean` green)

The one inconsistency in the (otherwise mostly-object) capstone file: `cross_rotXY_equivariant`,
`cross_rotXZ_equivariant`, `cross_rotYZ_equivariant` still took vector coordinates while their `proj`/
`vecReject` equivariance siblings (in `StandardPosition`/here) were already object. Lifted all three to
`{a b : G3} IsVector` + angle scalars `c s` (`_coord` leaf + object bridge; all uncited). The rest of the
file stays coordinate by nature: the `rotXY_vec`/`rotXZ_vec`/`rotYZ_vec` unfolds (form-D), `rotYZ_fixes_e1`/
`rotYZ_aligns_yz`/`reduceToPlane_*` (coordinate-parameterized — the cos/sin ARE the coordinates), and the
reduced-frame `proj_reduced`/`vecReject_reduced`/`cross_reduced` (the zero-coordinates `(m,0,0)`/`(b1,b2,0)`
are the essential "standard position" content). This is the sweep's cross-product analogue of the
already-object proj/rotation equivariance; it is NOT the separate capstone-*completion* task
(`tasks/lean-cross-standard-position-capstone.md`), which remains its own initiative.

## FOLLOW-ON: proof-style refactor (dissolve the scalar `_coord` layer) — 2026-10-03

The STATEMENT sweep (this task) made the public theorems object-form, but via a `_coord`-leaf + bridge
mechanism that keeps a scalar-taking layer. The maintainer then clarified the deeper intent: proofs should
take objects and **destructure them via getters** (`obtain ⟨…⟩ := ha; compute on a.c1`), with no separate
scalar-taking `_coord` leaf. That is a distinct, corpus-wide refactor tracked in its own task —
**`tasks/lean-object-in-getters-out-proof-style.md`** — which supersedes this task's "keep the `_coord`
leaf" stance (Increments 21/the audit). Its **bucket 1 is done** (the clean single-caller pass-throughs
inlined, incl. `sandwich_preserves_cos`/`sin` now fully object; `make lean` green); buckets 2/3 (shared +
delicate) are feasible via the same `obtain`-getters approach and are enumerated there.

## Objectification EXHAUSTED (2026-10-03) — what is left is genuinely un-objectifiable

Every theorem whose statement can meaningfully become object-form now is. The remaining `ℝ`-taking theorems
cannot be improved by taking an object + getters, and stay coordinate **by nature**:
- **Pure coordinate-unfold bridges** — `normSq_vec`, `dot_vec`, `cross_vec`, `dual_vec`, `wedge_vec_eq_biv`,
  `normSq_wedge_vec`, `magnitude_sq_vec`, `signedArea_eq/sq`, `vec_mul`, `vec_eq_smul`, `normSq_triv`,
  `versorFromVectors_eq_evenVersor`. Their RHS **is** coordinate arithmetic (`= a1²+a2²+a3²`,
  `= vec (a2*b3−…)`, …), so an object form would only move the coordinates into getters on the RHS — no
  readability gain, and these are used corpus-wide as `rw`-unfold lemmas (high blast). `reverse_vec` already
  has the object companion `reverse_of_isVector`.
- **The `Rotation2D` angle layer** — `θ/α/β` are genuine angle scalars and `rot θ (x,y)` acts on `ℝ×ℝ`
  pairs (the classical coordinate representation); there is no G-vector object to take.
- **Coordinate-parameterized defs** — `rotXY_aligns_xy`/`rotate_b_to_e1(_magnitude)` (the cos/sin ARE `b`'s
  coordinates) and `Exp.expBivectorGeneral`/`normSq_expBivectorGeneral` (the `exp` fn is defined on `(p q r)`);
  these need a *def* redesign, not a statement lift.
- **Pure real identities** — `lagrange_2d`/`lagrange_3d` (`(a1²+a2²)(b1²+b2²) = …`): no GA object in the
  statement at all.
- **Companion helpers** (`isVector_vec`, `isBivector_bivector`, `isTrivector_trivector`,
  `isEvenVersor_evenVersor`) and the **`CrossStandardPosition` capstone** (its own task).

## Convergence status (2026-10-03) — the sweep's main phase is COMPLETE

The user-facing geometric theorems are now object-form across the touched files (Sandwich/Trig/Projection2D
versor cluster, RotateComponents, TrigEquiv, Measures, Cross, Contractions, Reflect, ProjectionRotation2D/3D,
StandardPosition, Projection3D `reject_vec_eq` **and the `IsBivector` plane cluster**). Two predicates now
carry grade-structure as objects: `IsVector`, `IsEvenVersor` (Inc 10–11), `IsBivector` (Inc 16). What remains
is **not** sweep work — it is the foundation and a separately-tracked capstone:

1. **The coordinate bridge layer** — the G2/G3 `vec`-literal lemmas (`normSq_vec`, `dot_vec`, `mul_vec_self`,
   `cross_vec`, `dual_vec`, `plane_eq_wedge`, `wedge_reject`, `mul_vec_inverse_self`, `magnitude_sq_vec`, …)
   and the √-structural/orthogonality leaves (`key_reverse_sq`, `inplane_perp_reject`, `project_perp_reject`,
   `project_onto_in_plane_self`, …). These **stay coordinate** (form D): they are what
   `IsVector`/`eq_vec`/`eq_bivector`/`eq_evenVersor` bridge *to*; converting is circular, and the ones with
   geometric content already have object companions (`mul_eq_dot_add_wedge`, `mul_eq_wedge_of_perp`,
   `dual_perp`). This is the irreducible base of the whole development.
2. **`CrossStandardPosition` capstone** (~20 theorems) — tracked separately in
   `tasks/lean-cross-standard-position-capstone.md`, not part of this sweep.

**So this sweep's remaining actionable work is done.** Closing it out (archive) is appropriate once the
maintainer has committed Increments 12–16; the capstone and the coordinate foundation are intentionally
out of scope.

## Open questions

1. Confirm the C-keep boundary: pure identities (`lagrange_*`) and scalar *parameters* (rotation
   `cos`/`sin`, `k`) stay `ℝ`; coordinate-*computation* leaves (`rotXY_vec`-style, whose RHS is an
   explicit computed coordinate-vector) also stay coordinate. My recommendation: yes — convert only
   theorems whose `ℝ` args are vector coordinates and that state a geometric fact. (The "versor
   components" sub-case is split out into Q2.)

2. **RESOLVED (a), 2026-10-03** — lifted the `evenVersor`-component `sandwich_preserves_*` family to an
   object **versor** `{R : G_n} (hR : IsEvenVersor R) (hr : normSq R ≠ 0)` (Increments 10–11). Terminology
   per the maintainer: versor = even (not necessarily unit); rotor = unit versor, tracked separately in
   `tasks/lean-unit-versors-rotors-sandwich-with-reverse.md` (unit rotors → sandwich with reverse).

3. **Introduce an `IsBivector` predicate to objectify the plane-projection cluster?** `project_add_reject`,
   `reject_eq_proj_normal`, `project_eq_sub_reject` (and `proj_plane_eq_project_onto`, whose plane is
   `wedge a b` and could instead take `a`, `b` as vectors) state their plane as a coordinate bivector
   `(bivector p q r)`. Lifting them needs `IsBivector (B : G3) := B.s = 0 ∧ B.c1 = 0 ∧ B.c2 = 0 ∧ B.c3 = 0
   ∧ B.c123 = 0` + `eq_bivector_of_isBivector : B = bivector B.c12 B.c13 B.c23` + `isBivector_bivector`,
   then `{B : G3} (hB : IsBivector B) (hBn : normSq B ≠ 0)` + vector objects, bridging as usual. Exactly the
   `IsEvenVersor` pattern (Q2). **My recommendation: (a) yes** — a plane bivector is a geometric object.
   Caveat: `project_add_reject` is cited coordinate-style by `ProjectionRotation3D` (plane_pythagorean,
   the `hsplit`), so it needs a `_coord` leaf + object wrapper (shared → justified), not a bare rename.
   Alternative **(b)** leave the plane cluster coordinate (it is lower-level than the sandwich/rotation
   results). Pick (a) or (b).
   **RESOLVED (a), 2026-10-03** — `IsBivector` added, plane cluster lifted (Increment 16).
