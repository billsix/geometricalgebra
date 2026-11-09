# Lift Lean theorem statements from coordinate tuples to geometric objects (corpus-wide sweep)

**Created:** 2026-10-03 · **Completed:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)
**Superseded by:** `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`, the consolidated
record. Once the maintainer stated the intent as "geometric objects in, scalars in the body, geometric
objects out", this statement-lift and that proof-style refactor became the same effort; this doc is the
historical origin. Its A/B/C judgment framework was harvested into
`tasks/reference/lean-ga-proof-architecture.md` ("Coordinates only when needed"), referenced from
`CLAUDE.md`. Outcome: the polynomial tier was done and the coordinate core was retained by decision.

## Summary

On 2026-10-03, ~224 of the 323 theorems in `proofs/GacalcProofs/*.lean` took `ℝ` arguments, many of them
raw vector coordinates (`theorem wedge_is_antisym_part (u1 u2 v1 v2 : ℝ) …`). Over Increments 1–23 (all
2026-10-03, `make lean` green after each) every user-facing geometric theorem was restated over objects
(`IsVector`, plus the new `IsEvenVersor`, `IsBivector`, `IsTrivector` predicates); the remaining `ℝ`-taking
theorems were all classified as justified. The `_coord`-leaf + bridge mechanism this sweep used was then
dissolved by the sibling task.

## The judgment framework (the maintainer's, applied per theorem)

For each `ℝ` argument, ask what it *is*:

- **A — coordinate-free object.** A structural fact: take `{a b : G_n} (ha : IsVector a)` and prove it with
  `rw`/property lemmas, no field access (e.g. `G3.mul_eq_dot_add_wedge`).
- **B — object in, coordinates pulled in the proof.** A geometric fact whose proof needs the coordinate
  computation: take the object + `IsVector`, then `obtain ⟨hs, …⟩ := ha; simp only [defs, field-zeros]; ring`.
- **C — genuine `ℝ`, kept.** A pure scalar identity (`lagrange_2d`, `lagrange_3d`), or a scalar *parameter*
  (a rotation's `cos`/`sin`, a scalar multiple `k`); only vector args next to it are lifted.
- **D — coordinate formula, kept.** A theorem whose RHS *is* coordinate arithmetic (`cross_vec`, `dual_vec`,
  `normSq_vec`, `rotXY_vec`, `signedArea_eq`, …): the formula is the content, and many are heavily cited
  `rw`-unfold leaves (`normSq_vec` had 31 callers, `cross_vec` 6). Converting them would be wrong.

The maintainer's test: *does this require reals, or could it take geometric objects coordinate-free (A),
or object-then-pull-coords (B)?* Prefer A, then B. Open question 1 (confirm the C-keep boundary: pure
identities and scalar parameters stay `ℝ`, coordinate-computation leaves stay coordinate) was applied as
recommended; the record shows no separate answer.

Per-file `ℝ`-taking counts at the start (2026-10-03): `Sandwich` 37, `CrossStandardPosition` 20, `G3` 18,
`ProjectionRotation3D` 16, `Rotation2D` 16, `StandardPosition` 14, `ProjectionRotation2D` 13, `G2` 11,
`Projection2D` 11, `AlgebraLaws` 8, `Projection3D` 8, `Trig` 8, `Measures` 6, `Versor2D` 6, `Exp` 5,
`RotateComponents` 5, `TrigEquiv` 5, `Cross` 4, `Rotation3D` 4, `Contractions` 3, `Lagrange` 2 (both C),
`Normalize` 2, `Reflect` 2, `Predicates3D` 1, `StudentTrigForms` 1.

Method: bottom-up (convert the leaves a theorem rests on first, or fix all citers in the same step; check
citers with `grep -rn '\bNAME\b'`), one file or small batch at a time, never leaving the tree red.

## Increments (all 2026-10-03)

- **1–4, the clean tier (self-contained, uncited, no cascade).** The perpendicularity/parallelism facts and
  their `_dot`/wedge helpers (form B, nonzero-guarded); `G2`'s `dot_is_sym_part`, `wedge_is_antisym_part`,
  `dot_eq_coord_sum`; `Cross` (`cross_anticomm_vec` → `cross_anticomm`, `dot_cross_eq_signedVolume`);
  `Contractions` (`leftContraction_scalar_vec` keeps its scalar `α`).
- **5, the `versor_mul` bisector cluster** (`Versor2D`, `Rotation3D`). This set the **cascaded-cluster
  recipe**: keep the coordinate proof verbatim as a `_coord` leaf, and bridge the object theorem with
  `have h := …_coord …; rwa [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht] at h` (the `←` direction
  avoids the forward-rewrite motive problem). `G2.isVector_vec` was added; 5 call sites were updated.
  **Lesson:** `make lean` had to be verified by `check.sh`'s `[lean] OK`/`FAILED` line or its real exit
  code, not a `… | grep | tail` whose exit code is the pipeline's; that masking hid a broken
  `Contractions.lean` `ext <;> ring`, which was then fixed.
- **6–9.** `Measures` G3 facts (`area_sq_vec`, `normSq_wedge_eq_lagrange`, `normSq_wedge3_eq_signedVolume_sq`,
  `volume_sq_vec`); `Reflect` (the `normSq ≠ 0` hypothesis bridged with `(by rw [← eq_vec_of_isVector …];
  exact hd)`); `TrigEquiv.sin_between_eq_abs_signed_vec`; all 5 `RotateComponents` theorems, whose
  coordinates turned out to be vector coordinates (form B, not "versor components").
  `rotation_fixes_normal` was restated coordinate-free with the normal as **`cross b a`**, the sign gap
  reconciled by a one-line scalar `ring` rather than an 8-component `ext`.
- **10–11, `IsEvenVersor`.** Open question 2 was answered **(a) lift them** (the maintainer, 2026-10-03: "I'd
  like to not take reals, and I think we can make this work"). Terminology per the maintainer: a **versor**
  is even (not necessarily unit), a **rotor** is a unit versor. `IsEvenVersor` (G2: `c1 = c2 = 0`; G3: also
  `c3 = c123 = 0`), the bridge `eq_evenVersor_of_isEvenVersor` and `isEvenVersor_evenVersor` were added, and
  the whole `sandwich_preserves_*` family (Sandwich, Projection2D, Trig) was lifted to
  `{R} (hR : IsEvenVersor R) (hr : normSq R ≠ 0)`. The unit-rotor layer (sandwich with reverse) went to
  `tasks/archive/2026/10/05/lean-unit-versors-rotors-sandwich-with-reverse.md`.
- **12–15.** `ProjectionRotation2D`'s 4 user-facing results, applying the maintainer's feedback ("still looks
  like you are adding lots of reals instead of geometric objects"): only one new `_coord` symbol was minted,
  shared by the other three. This fixed the calibration **A → inlined B → a named `_coord` only when shared
  by ≥ 2 callers**, recorded in the architecture doc. `ProjectionRotation3D`'s 3 capstones were long and
  delicate (`set`/`calc`, heartbeat bumps), so each kept its proof verbatim as a `_coord` leaf (the
  delicate-proof exception). `StandardPosition` (`mul_proj_eq_dot`, `mul_eq_proj_dot_add_reject_wedge`,
  inlined) and `Projection3D.reject_vec_eq`.
- **16, `IsBivector`.** Open question 3 (add `IsBivector` to lift the plane-projection cluster, or leave it
  coordinate) was answered **(a) yes** (the maintainer, 2026-10-03). `IsBivector`, `eq_bivector_of_isBivector`
  and `isBivector_bivector` were added; `project_add_reject`, `reject_eq_proj_normal`, `project_eq_sub_reject`
  and `proj_plane_eq_project_onto` were lifted.
- **17–20, four diff reviews** (each at the maintainer's ask, over `git diff master..HEAD`). They found
  `Trig.cos_sq_add_sin_sq` and `Normalize`'s two theorems; `wedge_antisymm` and G3 `vec_anticomm_perp` (now
  a coordinate-free form-A proof); `sandwich_carries_from_to`; and in the fourth pass nothing. G2
  `vec_anticomm_perp` stayed coordinate for a layering reason: `G2.dot` lives in `Versor2D.lean`, above
  `AlgebraLaws.lean`.
- **21, the scaffold.** The open decision was whether to objectify the internal scaffold whose user-facing
  deliverables were already object (default: keep coordinate). The maintainer decided 2026-10-03: "yes, if
  they objectify without breaking the proofs." About 32 scaffold lemmas in `ProjectionRotation3D` (13),
  `ProjectionRotation2D` (8), `Rotation3D` (1) and `Sandwich` (≈10) gained object wrappers over `_coord`
  leaves. The mechanical rename was a one-shot codemod `rename_to_coord.py` (removed at archive; in git
  history). **Mistake made and fixed:** the codemod was not idempotent; a second run renamed the new
  wrappers (32 lines). The "run twice, expect zero changes" check caught it; the 32 lines were reverted and
  a single-use guard added.
- **22–23.** At the maintainer's broad discretion ("do all the rest you can … take a vector as input, use
  getters"): `IsTrivector` completed the grade family; `mul_triv_*`, `sandwich_fixes_own_bivector`/`_normal`
  (plane/normal read from `R`'s getters), `lagrange_property`, and the `G3` self-product leaves were lifted;
  `CrossStandardPosition`'s `cross_rot{XY,XZ,YZ}_equivariant` were lifted with angle scalars `c s`.

## What stayed coordinate, and why

- **Form-D unfold bridges** (`normSq_vec`, `dot_vec`, `cross_vec`, `dual_vec`, `wedge_vec_eq_biv`,
  `normSq_wedge_vec`, `magnitude_sq_vec`, `signedArea_eq`, `vec_mul`, `vec_eq_smul`, `normSq_triv`,
  `versorFromVectors_eq_evenVersor`): an object form only moves the coordinates onto the RHS as getters,
  and they are the base `IsVector`/`eq_vec` bridge *to*. Those with geometric content already had object
  companions (`mul_eq_dot_add_wedge`, `mul_eq_wedge_of_perp`, `dual_perp`; `reverse_of_isVector`).
- **The `Rotation2D` angle layer:** `θ`/`α`/`β` are angles and `rot θ (x, y)` acts on `ℝ × ℝ` pairs.
- **Coordinate-parameterized defs:** `rotXY_aligns_xy`/`rotate_b_to_e1(_magnitude)` (the cos/sin are `b`'s
  coordinates) and `Exp.expBivectorGeneral`/`normSq_expBivectorGeneral` (defined on `(p q r)`). These need a
  def redesign, not a statement lift; noted as a follow-up, not done.
- **Pure real identities** (`lagrange_2d`/`lagrange_3d`) and the companion helpers (`isVector_vec`, …).
- **`CrossStandardPosition`'s capstone completion** was its own task,
  `tasks/archive/2026/10/22/lean-cross-standard-position-capstone.md`.

## Follow-on

The maintainer then clarified the deeper intent: proofs should take objects and destructure them via
getters, with no separate scalar `_coord` layer. That reversed this sweep's "keep the `_coord` leaf" stance
and was done in `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`.
