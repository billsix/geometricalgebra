# Lean proofs: bring the corpus in line with the book, the Python and its own rules

**Status:** done 2026-11-22/23 (done-record). The phase 5 leftovers are carried by
`tasks/lean-proofs-fit-cleanup-leftovers.md`.
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)
**Source:** `tasks/review/2026/11/22/lean-proofs-fit-review.md` (sections A, B, C)

## What the task was

The maintainer asked whether the Lean proofs were written as they should be and whether any were
extraneous, judged against the book and the Python. Three readers read all 37 files; the frozen record above
found the mathematics right and the definitions faithful but the corpus uneven. This task worked through the
findings in eight phases, cheapest first, on branches `task-batch-2026-11-22`, `lean-phase-3` to `lean-phase-8`
(each merged by the maintainer). Every phase ended with `lake build`, the `sorry` scan and the axioms gate green
(1123 declarations on `propext`, `Classical.choice`, `Quot.sound` after phase 7).

## What was done, by phase

1. **Citations and docs.** `proofs/README.md` and the architecture doc named the 35 modules; eleven `-- twin:` tags
   were added on the Lean side; book pages and notebooks that cited the wrong theorem or a vanished one were fixed.
2. **Removed what nothing used.** `RotateComponents.lean` and `Normalize.lean` (`normalizeVec` moved into
   `ProjectionRotation3D`), 13 wrappers of `ProjectionRotation3D`, nine `CrossStandardPosition` lemmas, the
   `IsScalar` apparatus and unused recognizers, and about 15 single theorems. The one-shot helper that did
   the deletions was removed at archive and is in git history.
3. **One proof per fact.** `isEvenVersor_versorFromVectors` moved to `Sandwich`, so the general even-versor lemmas
   serve everywhere (five special cases deleted); four 𝒢₃ `_coord` twins went; `expBivector` is
   `fullAngleRotor`; `|uvec α| = 1` is stated once; 2D and 3D `mul_proj_eq_dot`/`mul_reject_eq_wedge` agree.
4. **Proved by the reason the book gives.** `dual_perp_dot` (regroup, a vector squared is a number),
   `G2.vec_anticomm_perp` (each product is its wedge), `rotPlane_conj_collapse` (from `rotPlane_comm`), the
   versor-bisector identities (from `(b a) a = |a|² b`), `Trig.lagrange_property` and
   `normSq_versorFromVectors` (through `Lagrange.lean`), and `sandwich_fixes_own_*` (through
   `sandwich_of_commute`).
5. **Restated over objects.** `RotateFromTo2D`, `CrossStandardPosition.cross_via_reduction_of_vectors` (through
   `alignSP`), `Measures` (`G2.signedArea`, `G2.area`), `G1` (`IsVector` objects, `sub`/`neg`, the addition laws)
   and `ProjectionRotation3D` (no `_coord` theorem left; the plane lemmas take any bivector; `hfn`/`htn` derived).
6. **Where Lean differed from the book or Python.** Contractions are zero when the left grade exceeds the right;
   the book's rotate / keep the rest / rotate back rejection is proved equal to Python's
   (`rejectSP_eq_rotate_keep_rest`); the peel's coordinates and the iterated rejection are proved equal to
   `frame.py`'s; `proj_a b = (b·a)*a⁻¹` is proved in 3D.
7. **Results the book states that Lean lacked.** Reflection as `d * v * d⁻¹`, twice, in 2D, and the plane mirror's
   length; `rotor θ = exp(−(θ/2)*e₁₂)` and the general-plane form; the `rot`/`rotPlane` bridge and the blend for
   `rot`; `unitPlane` and the plane rotor as a rotor; the small multiplication, dual, cross and inverse facts;
   rejection from a plane without a volume; student-form meaning gates that exclude the `0/0` case.
8. **Recorded what is now true.** The inventory and coverage map of
   `tasks/reference/lean-ga-proof-architecture.md` were rewritten from the files, stale passages about `IsScalar`
   and the deleted theorems were corrected, and the table "which rotation development backs which book page and
   Python function" was added there. `tools/check_lean_arch_doc_names.py` (promoted from this task's scratch
   script) lists backticked names in that document that no Lean file declares; it is a report, not a gate.

## Left over

The phase 5 items that were not finished are in `tasks/lean-proofs-fit-cleanup-leftovers.md` (the three coordinate
leaves of `ProjectionRotation3D`, `hrn`, the `Bootstrap2D`/`RotateFromTo2D` overlap, `G2`'s late sections). The
Python `exp` docstring does not yet cite `rotor_eq_expBivector`.

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

All 2026-11-22 to 2026-11-23 (William Emerison Six <billsix@gmail.com> authorized each phase).

1. The maintainer's question; a usage count of all 692 theorems (`tasks/adhoc/lean-proofs-fit-review/lean_usage.py`,
   which undercounts unused theorems, as its docstring says); three readers; the frozen record.
2. Four questions went to the maintainer (`StudentTrigForms`, `RotateComponents`, `Lagrange`,
   `ProjectionRotation3D`); the answers are the Decisions above.
3. Phases 1 and 2 ran in the 2026-11-22 batch; phases 3 to 8 followed one branch each, the maintainer merging
   between them.
