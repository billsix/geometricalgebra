# Lean proofs: bring the corpus in line with the book, the Python and its own rules

**Status:** in progress — phases 1 to 4 done 2026-11-22; phases 5 to 8 remain
**Priority:** 5
**Difficulty:** 7
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)
**Source:** `tasks/review/2026/11/22/lean-proofs-fit-review.md` (sections A, B, C)

## BLUF

A full read of the 37 Lean files against the book and the Python found the mathematics right
and the definitions faithful, but the corpus uneven: the newest files follow the house rules,
the older ones do not, some material is unused, a few facts are proved several times, three
definitions differ from the book's or Python's with no theorem between them, and the book
states a handful of results Lean lacks. This task works through those in eight phases, cheapest
first. Done = each phase's list is cleared or explicitly declined, `make lean` passes with the
axioms gate, and `proofs/README.md` and `tasks/reference/lean-ga-proof-architecture.md`
describe the files that exist.

## The request (2026-11-22, the maintainer's words)

> take a look at all lean proofs that we made, and tell me if you think they are written as
> they should be, or if there are any extraneous ones, from your understanding of the book, and
> python code. read everything in the repo. make a task, and recommendations, and if needed, a
> reference doc

No new reference doc was needed: `tasks/reference/lean-ga-proof-architecture.md` is the
reference, and phase 8 updates it.

## Context

- Read first: the review record named in **Source** (its Summary, then the slice for the files
  you are touching); `tasks/reference/lean-ga-proof-architecture.md` (the rules: leaf versus
  structural, objects in and scalars only in the body, a `_coord` leaf only when fragile and
  shared by two object theorems, hypotheses, "Structural proofs over brute `ring`", build
  discipline); `tasks/reference/algebra-teaching-order.md`; `CLAUDE.md` "Coordinates only when
  needed" and "Every piece of math comes in three forms".
- **Nothing in the record was compiled.** Treat each deletion, restatement and "follows from"
  as a lead: make the change, build, and read a failure before concluding (the architecture
  doc's "Hypotheses" section says how).
- Build: `make lean` re-runs the image build when nested; use the gate's own `podman run` line
  from the architecture doc's "Build discipline", or `lake env lean <file>` for one file.
- Overlapping open task: `tasks/lean-proofs-remove-extras.md` (extra hypotheses, no-op tactics,
  a warnings gate). Its items are still present. Do it first or fold it into phase 2; do not
  redo its audit.
- Parked tasks this one does not reopen: `tasks/lean-frame-coverage.md`,
  `tasks/lean-frame-class-invertible-function.md`,
  `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`,
  `tasks/grade-simp-tactic-reduce-proof-boilerplate.md`.
- The Lean proofs are a private oracle for the mathematics (the architecture doc's program
  decision 1), so removing a theorem breaks no consumer. A theorem the book, a notebook or a
  docstring cites is not removed without fixing the citation in the same change.

## Done so far

**Phases 1 and 2** (2026-11-22, William Emerison Six <billsix@gmail.com> authorized the batch), one work commit.
Verified by a full `lake build` and `proofs/check.sh` (no `sorry`; the axioms gate reports 1058 declarations on the
three standard axioms), plus `make format`, `make check-notebooks`, `make test` and `make docs`.

- **Phase 1 (citations and docs):** `proofs/README.md` says 35 modules and lists `Bootstrap2D`, `GeneralInverse`,
  `RotateFromTo2D` and `StandardPosition2D`; the architecture doc's inventory lists `Rotor` and `GeometryObjects2D`
  and its coverage map names `in_plane` and `rotXY`/`rotXZ`/`rotYZ`/`rotPlane` instead of the vanished
  `rotate_in_xy_plane`. `proof-projection.py` is tagged with the 2D theorem and cites `StandardPosition2D.lean`.
  Eleven `-- twin:` tags were added on the Lean side (`G3.project_add_reject`, `G3.mul_proj_eq_dot`,
  `G3.mul_eq_proj_dot_add_reject_wedge`, `G3.dual_wedge_perp_left_dot`/`_right_dot`, `G3.reflectVec_eq`,
  `G3.reflectPlane_eq_neg_reflectVec_dual`, `G2.mul_proj_eq_dot`, `G2.mul_reject_eq_wedge`, `G2.dual_perp_dot`,
  `G2.dual_perp`, `G2.projectSP_eq_proj`). Citations fixed: `rotation-from-vectors.rst` and its notebook name the
  angle-free theorems (`rotateFromToProj_normalize`, `rotPlane_fromTo_eq_vec_mul`, `projRotation_eq_vec_mul`);
  `proof-rotate-from-a-to-b.rst` no longer says `rotPlane_conj_collapse` rests on `rotPlane_comm`;
  `bootstrap-rotation.rst` cites `rot_polar`; `defining-g2.py` says associativity is proved for the line, the plane
  and space; `proof-projection-3d.rst` no longer claims a notebook runs `project_sp`; `blade-square-sign.rst` cites
  `I_sq_eq_sign`. Doc comments: Lean's `dot` is Python's `scalar_product` (the book's dot on two vectors only), the
  `GeneralInverse` module doc, and the stale headers of `Sandwich.lean` and `Rotation3D.lean`.
- **Phase 2 (remove what nothing uses):** `RotateComponents.lean` and `Normalize.lean` are deleted (`normalizeVec`,
  which `ProjectionRotation3D` still needs, moved into that file beside its 2D twin); 13 object wrappers of
  `ProjectionRotation3D`; the nine projection/rejection lemmas of `CrossStandardPosition`; the `IsScalar` apparatus
  and unused recognizers (2 definitions, 14 theorems); `Measures.area_sq_vec`, `normSq_wedge_eq_lagrange`,
  `G2.dual_vec_perp`, `G2.vec_mul`, `G2.dot_eq_coord_sum`, `G2.normSq_wedge_vec`, `MathlibBridge.toC_rot_rot`,
  `IsRotor.isEvenVersor`, `IsRotor.normSq_eq_one`, `mul_reverse_self_of_isRotor`, `reverse_mul_self_of_isRotor`,
  `G3.reverse_mul_vec` and `Rotation2D.rotor_unit'`. Nothing else needed them: the build passed first time.
  Kept for phase 4: `Rotation3D.vec_mul_mul_self`.
- Not done from phase 1: the doc comments of §B.1f that sit on proofs phases 3 to 7 rewrite anyway (`Rotor`'s
  antiparallel wording, `Rotation2D`'s header, `TrigEquiv`'s header and unused import, `PlaneRotation3D`'s
  "Corollaries" heading, the missing comments in `Sandwich`).
- The helper that made the deletions was `tasks/adhoc/lean-proofs-fit-cleanup/delete_decls.py` (one-shot; `git rm`
  with the task, when it is archived).

**Phase 3** (2026-11-22, one work commit; `lake build`, the `sorry` scan and the axioms gate pass, 1048 declarations):

- `isEvenVersor_versorFromVectors` (2D and 3D) moved from `Rotor.lean` into `Sandwich.lean`, so the general
  `mul_reverse_self_of_isEvenVersor` / `mul_inverse_self_of_isEvenVersor` serve everywhere. Deleted the five special
  cases: `G2.versorFromVectors_mul_reverse`, `G3.versorFromVectors_mul_reverse`, `…_mul_reverse_coord`,
  `…_mul_inverse_coord` and `G3.versorFromVectors_mul_inverse`; `sandwich_carries_from_to` (both) and
  `ProjectionRotation3D` call the general lemmas.
- The four 𝒢₃ `_coord` twins (`wedge_self_vec_coord`, `mul_vec_self_coord`, `dot_self_vec_eq_normSq_coord`,
  `vec_mul_eq_dot_add_wedge`) are gone; their nine call sites (five in `Projection3D`, three lines of one proof in
  `StandardPosition`, one in `ProjectionRotation3D`) use `wedge_self_vec`, `mul_vec_self`, `dot_self_vec_eq_normSq`,
  `mul_eq_dot_add_wedge` and `reverse_of_isVector`. `G1.vec_mul_eq_dot_add_wedge` stays.
- `Exp.expBivector` is defined as `Rotation2D.fullAngleRotor`, with `expBivector_eq_fullAngleRotor` (`rfl`).
- 2D/3D drift: 3D `mul_proj_eq_dot` and `mul_eq_proj_dot_add_reject_wedge` end in `scalar (dot b a)` as the 2D
  ones do; `Projection3D.plane_eq_wedge` is renamed `mul_reject_eq_wedge`, the 2D name.
- `|uvec α| = 1` once: `normSq_uvec` and `magnitude_uvec` live next to `uvec` in `Rotation2D.lean`;
  `TrigEquiv.uvec_magnitude` and the `Rotor` copies are gone. `ReciprocalFrame2D`'s `normSq_wedge_vec'` lost its prime
  (the `G2` copy it duplicated went in phase 2), and `ReciprocalFrame3D.normSq_wedge_vec3` is proved through
  `G3.normSq_wedge_vec`. `ProjectionRotation2D.reverse_versorFromVectors_mul` (unused) is deleted.
- Left as they are, on purpose: `mul_eq_proj_dot_add_reject_wedge` is a different proof of the product split (from
  projection and rejection, the non-circular route the book teaches), so it stays beside `mul_eq_dot_add_wedge`;
  `ReciprocalFrame3D`'s `det3` against `signedVolume` waits for phase 5's object-form rewrite.

**Phase 4** (2026-11-22, one work commit; `lake build`, the `sorry` scan and the axioms gate pass, 1050 declarations;
the 16 build warnings are all in files and lines this phase did not touch):

- `Predicates2D.dual_perp_dot` is the book's proof from `dual.rst`: `rw [dot_comm, dot, dual, ← mul_assoc,
  mul_vec_self]`, then a number times `I⁻¹` has no plain-number part. `G2.vec_anticomm_perp` is the three-rewrite chain
  of its 𝒢₃ twin (`mul_eq_wedge_of_perp` twice, `wedge_antisymm`).
- `rotPlane_conj_collapse` now uses `rotPlane_comm` and `rotPlane_comp`, as the book says: commute the middle rotation
  outward, compose the align with the un-align into `rotPlane 1 0`, which is the identity.
- `versor_mul_from_eq_bisector` and `from_mul_versor_eq_bisector` (𝒢₃ in `Rotation3D`, 𝒢₂ in `Versor2D`) are
  structural: `R a = (b a) a + |a||b| a`, `(b a) a = |a|² b`, then `|a|` factors out. The four `_coord` leaves and the
  `magnitude_sq_vec`-driven `linear_combination`s are gone; `vec_mul_mul_self` (now also in 𝒢₂, and without the
  unused `IsVector b` hypothesis) is used, with a new `vec_mul_self_mul` for the companion. Both theorems lost the
  hypothesis they did not need (`ht` for the first, `hf` for the second); `Sandwich` and `ProjectionRotation3D` callers
  were updated. `magnitude_sq_vec` stays (`CrossStandardPosition` uses it).
- `Trig.lagrange_property` (𝒢₂ and 𝒢₃) is `linear_combination (-1) * lagrange_2d/3d …`, so `Lagrange.lean` is now
  imported and used. `Rotor.normSq_versorFromVectors` (both) goes through a new `normSq_versorFromVectors_eq`
  (`(|a||b| + a·b)² + |a∧b|²`, by `ring` on the components) and `Trig.lagrange_property`, then `linear_combination`;
  `Rotor` imports `Trig` for it.
- `sandwich_fixes_own_bivector` and `sandwich_fixes_own_normal` rest on a new `sandwich_of_commute` (`R x = x R` gives
  `R x R⁻¹ = x` through `R R⁻¹ = 1`) and two commutation leaves, `evenVersor_mul_bivector_comm` and
  `evenVersor_mul_normal_comm` (`ring`, no `field_simp`). The two `_coord` theorems are gone.
- Not changed: `tasks/push-delicate-coordinate-core-tier.md` (proposed) still lists the deleted `_coord` leaves in its
  "retained set"; it was already out of date after phase 3, and it is reworked, not patched, if it is ever started.
- Docs: the architecture doc no longer names the deleted `G2.dual_vec_perp`.

**Remaining, in order:** 5 (restate the scalars-in
files over objects; the largest, `ProjectionRotation3D.lean` last), 6 (where Lean differs from the book or Python),
7 (results the book states that Lean lacks), 8 (rewrite the inventory and coverage map from the files as they then
stand). These are proof rewrites with a full `lake build` (about 20 minutes) per iteration. The task's own plan
allows splitting 5 and 7 into step tasks if they grow; phases 5 to 7 together are a multi-session job.

## Recommendations, by phase

Section references are to the review record (`§A.2` = slice A, heading 2).

### Phase 1. Citations and docs (no proof changes)

- `proofs/README.md`: 37 modules, not 34; add `Bootstrap2D`, `GeneralInverse`,
  `RotateFromTo2D`, `StandardPosition2D` (§C.1).
- `tasks/reference/lean-ga-proof-architecture.md`: the inventory lacks `GeometryObjects2D` and
  `Rotor`; the coverage map lists `rotate_in_xy_plane`, which no longer exists (§C.1).
- `notebooks/proof-projection.py` is tagged `twin: GacalcProofs.G3.projectSP_eq_proj`; the 2D
  page's twin is the `G2` theorem in `StandardPosition2D.lean` (§C.4).
- `notebooks/rotation-from-vectors.py` and `book/docs/rotation-from-vectors.rst` credit theorems
  that do not say what the page claims (§B.4a).
- `twin:` tags with no Lean side: `G2.mul_proj_eq_dot`, `G2.mul_reject_eq_wedge`,
  `G2.dual_perp`, and the seven listed in §C.4; `Predicates2D.dual_perp_dot` lacks the tag
  `notebooks/dual.py` carries (§A.1, §B.4b).
- `notebooks/defining-g2.py` says associativity is proved "in every dimension"; Lean has
  n = 1, 2, 3 (§A.4). `GeneralInverse.lean`'s doc promises a 𝒢₃ vector case that is not there.
- `book/docs/proof-projection-3d.rst` says a notebook runs `project_sp`; none does (§C.4).
- `book/docs/blade-square-sign.rst` cites no Lean though `I_sq_eq_sign` proves its claim (§A.4).
- Doc comments: Lean's `dot` is Python's `scalar_product` (`⟨A * B⟩`), equal to the book's dot
  only on two vectors; say so where it is defined and fix `dot_eq_rVectorPart_zero`'s comment
  (§A.1). The stale headers of §B.1f and §C.1.

### Phase 2. Remove what nothing uses

Confirm each by deleting and building.

- Whole files: `RotateComponents.lean` (six theorems, no mention anywhere; superseded by
  `projRotation_eq_sandwich` and `rotorSandwich_planeRotor`), `Normalize.lean` (superseded by
  the hypothesis-free `Rotor` version on the same definition). `Lagrange.lean` stays and is
  put to use in phase 4 (decision 3).
- `ProjectionRotation3D.lean`: the 13 unused object wrappers at its end (§C.2).
- `CrossStandardPosition.lean`: the nine projection/rejection lemmas that feed only each other,
  unless phase 5 gives them a capstone (§C.2).
- The `IsScalar` apparatus and unused recognizers, 2 definitions and 14 theorems (§A.2).
- Singles: `Rotation3D.vec_mul_mul_self` (unless phase 4 uses it), `Measures.area_sq_vec`,
  `normSq_wedge_eq_lagrange`, `G2.dual_vec_perp`, `G2.vec_mul`, `G2.dot_eq_coord_sum`,
  `G2.normSq_wedge_vec`, `MathlibBridge.toC_rot_rot`, `IsRotor.isEvenVersor`,
  `IsRotor.normSq_eq_one`, `mul_reverse_self_of_isRotor`, `reverse_mul_self_of_isRotor`,
  `G3.reverse_mul_vec`, `rotor_unit'` (§A.2, §B.2).
- Keep, though uncited: the laws, the multiplication table, and the endpoints the readers
  marked "keep" (§A.2, §B.2 "Endpoints", §C.2).

### Phase 3. One proof per fact

- `R * R̃ = |R|²` for the from-vectors versor is proved four times and `R * R⁻¹ = 1` three
  times. Move `isEvenVersor_versorFromVectors` up into `Sandwich.lean` and derive the rest from
  the general even-versor lemmas (§B.3).
- 𝒢₃'s `_coord` twins (`wedge_self_vec_coord`, `mul_vec_self_coord`,
  `dot_self_vec_eq_normSq_coord`, `vec_mul_eq_dot_add_wedge`): move the nine call sites onto
  the object theorems and delete the twins (§A.1).
- `Exp.expBivector` and `Rotation2D.fullAngleRotor` are one definition in two files (§B.1).
- 2D/3D twins that drifted: `mul_proj_eq_dot` ends in `smul … one` in 𝒢₃ and `scalar` in 𝒢₂;
  `mul_eq_proj_dot_add_reject_wedge` restates `mul_eq_dot_add_wedge` with an extra hypothesis;
  `plane_eq_wedge` is the 3D `mul_reject_eq_wedge` under another name (§C.3).
- The duplicates the 2026-11-08 review listed and that remain (`normSq_uvec` versus
  `uvec_magnitude`, the `ReciprocalFrame` restatements).

### Phase 4. Prove by the reason the book gives

- `Predicates2D.dual_perp_dot`: `book/docs/dual.rst` exists to show the argument needs no
  coordinates; the proof is `ring` (§A.1).
- `G2.vec_anticomm_perp`: its 𝒢₃ twin is a three-`rw` chain (§A.1).
- `rotPlane_conj_collapse`: the book says it rests on `rotPlane_comm`; the proof does not use
  it, and no proof does (§B.1b).
- `versor_mul_from_eq_bisector`: goes through four one-consumer `_coord` leaves while
  `vec_mul_mul_self`, written for the structural proof, sits unused (§B.1b).
- `normSq_versorFromVectors` says "by Lagrange" and does not call `lagrange_property`;
  `sandwich_fixes_own_*` say "commutes with `R`" and are `field_simp; ring` (§B.1b).
- Make `Trig.lagrange_property` and `normSq_versorFromVectors` call `Lagrange.lean`'s
  identities (decision 3).

### Phase 5. Restate the scalars-in files over objects

- `RotateFromTo2D.lean` takes `ma`, `mb` as free reals throughout; `Bootstrap2D` redoes part of
  it in object form (§B.1c).
- `ProjectionRotation3D.lean`: 16 `_coord` leaves, none shared by two object theorems; 11 are
  `rw` chains or plain `ring`. Rewrite in `ProjectionRotation2D.lean`'s style; state the two
  heavy versor leaves over `IsBivector B`; `hfn`, `htn`, `hrn` follow from `hpn` (§C.1). Done
  last (decision 4).
- `CrossStandardPosition.cross_via_reduction_of_vectors` takes seven reals; restate through
  `alignSP` (§C.1).
- `G1.lean`'s vector theorems; `Measures.G2.signedArea` over four reals with `mul`, against the
  object-level `signedVolume` with `wedge`; add `G2.area` (§A.1).
- `G1`/`G2` section order against `G3` and `algebra-teaching-order.md`; 𝒢₁ addition laws (§A.1).

### Phase 6. Where Lean differs from the book or the Python

- `Contractions.leftContraction` / `rightContraction` subtract grades in ℕ, so a higher left
  grade gives the scalar part where `base.left_contraction` gives zero. Match Python, and prove
  more than the two vector cases, or scope the definition to `k ≤ m` (§A.1).
- `rejectSP` is `a − projectSP` (as Python), but the book and
  `tasks/reference/reduction-to-standard-position.md` define rejection as rotate, keep y,
  rotate back. Prove the two equal, or change the page (§C.1).
- The peel inverse divides by `|w|²` where `frame.py` divides by `w · v`, and uses plane
  rejection for `w₃` where Python iterates vector rejections. Prove the equality (§C.1).
- `proj = (b · a) * a⁻¹` is proved in 2D only (§C.1).

### Phase 7. Results the book states that Lean lacks

Each gets the three forms only where a form is missing; the book and notebook sides exist.

- Reflection: `b * a * b⁻¹`, reflecting twice is the identity, the 2D case, the plane mirror as
  an isometry (§C.4).
- `exp(−(θ/2) * i)` is the rotor, which `base.exp`'s docstring and
  `notebooks/displayrotations.py` state (§B.4c).
- The bridges between the rotation developments: `rot θ` and `rotPlane c s` (the book's blend
  formula is proved for `rotPlane` only); the 3D plane rotor and `normalize (a ∧ b)` (§B.3).
- Small ones: `e₁ * e₁₂ = e₂` and `e₂ * e₁₂ = −e₁` (also needed by
  `tasks/book-plot-by-table-quarter-turn.md`), `I` commutes in 𝒢₃, the dual of a 2D vector is a
  vector of the same length, the cross product is a vector, `a * a⁻¹ = 1` for a 𝒢₂ vector,
  rejection from a plane without the volume hypothesis (§A.4, §C.4).
- `StudentTrigForms.lean` (decision 1): make the book pages and notebooks cite its
  cosine/sine theorems where they now cite the `_dot` forms, and fix the meaning gates that
  still admit the `0/0` case, such as `cross_perp_left` when `a ∥ b` (§B.1e, §B.2).

### Phase 8. Record what is now true

Rewrite the inventory and coverage map of `tasks/reference/lean-ga-proof-architecture.md` from
the files as they then stand, and add the table "which rotation development backs which book
page and Python function" from §B.3. That doc is the reference; no new reference doc is needed.

## Order and size

Phases 1 to 3 are mechanical and can go in one sitting each. Phases 4 to 7 are proof work; 5 is
the largest (`ProjectionRotation3D.lean` alone is 507 lines). Each phase is its own commit
boundary. If phases 5 and 7 grow, split them into step tasks under this one.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22, each on the agent's recommendation:

1. **`StudentTrigForms.lean` is kept and cited.** The book and notebooks cite its cosine/sine
   theorems, and its meaning gates are fixed. Why: `CLAUDE.md` "Presenting to students" makes
   the cosine/sine form the one a reader sees; the book citing the `_dot` forms is the drift.
   Rejected: cutting the file to what is cited today.
2. **`RotateComponents.lean` is deleted** (after a build confirms nothing needs it). Its
   results follow from `projRotation_eq_sandwich` and `rotorSandwich_planeRotor`.
3. **`Lagrange.lean` is kept and used.** The proofs that say "by Lagrange" call it. Why: the
   program decisions name the Lagrange identity as a result, and phase 4 wants those proofs to
   show their reason. Rejected: deleting the file.
4. **`ProjectionRotation3D.lean` is rewritten in the 2D file's object style**, as the last
   piece of phase 5. Why: it backs `transforms.projection_rotation` in space. Rejected: only
   deleting its unused wrappers.

## History

All on 2026-11-22 (William Emerison Six <billsix@gmail.com>).

1. The maintainer asked whether the Lean proofs are written as they should be and whether any
   are extraneous, judged against the book and the Python. A usage count of all 692 theorems
   was made first (`tasks/adhoc/lean-proofs-fit-review/lean_usage.py`; it matches short names
   and so undercounts unused theorems, as its docstring says).
2. Three readers each read a third of the 37 files in full with the Python, pages and notebooks
   they mirror. Their reports, and a summary, are the frozen record
   `tasks/review/2026/11/22/lean-proofs-fit-review.md`. Nothing was compiled.
3. This task was written from the record as eight phases. Four questions went to the
   maintainer (`StudentTrigForms`, `RotateComponents`, `Lagrange`, `ProjectionRotation3D`); the
   answers are the Decisions above and were folded into phases 2, 4, 5 and 7.
