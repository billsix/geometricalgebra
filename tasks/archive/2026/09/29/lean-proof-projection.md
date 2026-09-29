# Lean proof — projection correctness (2D and 3D; onto vectors and onto planes)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Status:** DONE 2026-09-29 (William Emerison Six <billsix@gmail.com>), `make lean` green.
**Priority:** 6 · **Difficulty:** 7

## BLUF

Proved that gacalc's projection/rejection work via the **uniform Hestenes forms** — `project_B A =
(A·B)B⁻¹`, `reject_B A = (A∧B)B⁻¹` (base.py; H&S p.18) — for a vector or bivector blade `B`, in 2D and
3D. Landed in `proofs/GacalcProofs/Projection.lean` and `Projection2D.lean`. Durable architecture,
techniques, and the terminology note live in `tasks/reference/lean-ga-proof-architecture.md`.

## What landed

- **3D `proj` (onto a vector)** `= (b·a/a·a)·a` + `reject_perp` (the rejection ⊥ `a`); `wedge_reject`;
  `dual_wedge_perp_left`/`_right` (the plane normal ⊥ both spanning vectors); `plane_eq_wedge`
  (`a(b − proj_a b) = a∧b`).
- **3D `reject` (Hestenes)** `(A∧B)B⁻¹`, proved `= b − proj_a b` for the vector case (`reject_vec_eq`).
- **3D `project_onto` (onto a plane)** `= (A·B)B⁻¹` using the grade-1 Hestenes inner product `inner_vb`;
  validated by `project_add_reject` (`(A·B)B⁻¹ + (A∧B)B⁻¹ = A`) and `proj_plane_eq_project_onto` (the
  normal-based construction equals the Hestenes form; assembled from literal-bivector lemmas
  `reject_eq_proj_normal` + `project_eq_sub_reject` to avoid a degree blow-up).
- **2D cases** (`Projection2D.lean`): G2 `wedge`/`proj`/`reject`, `reject_perp` (structural, via the new
  G2 `dot_sub_left`/`dot_smul_left`), and the onto-the-pseudoscalar-plane case (`vec_wedge_I_eq_zero`,
  `reject_from_I_eq_zero` — a 2D vector has no perpendicular component to the whole plane).
- **Magnitude** (maintainer ask): the squared magnitude `normSq = ⟨AÃ⟩` (H&S p.13 eq 1.49) was already
  the workhorse; added the general `magnitude = √normSq` (all grades), bridged to the vector-only `mag`.
- **`tools/derive_lean_algebra.py`** — promoted from the adhoc G3-derivation script; emits any 𝒢ₙ's
  product/wedge/reverse formulas from the `Gn` oracle for verbatim Lean transcription.

## Resolved decisions

- **Blade inverse** `B⁻¹` = `Sandwich.inverse` (`B̃/(B B̃)`), works for a simple bivector.
- **Terminology:** the inner product in `(A·B)B⁻¹` is **Hestenes' inner product** `⟨AB⟩_{|r−s|}`, NOT the
  later "contraction" (they coincide for vector·bivector). Detail in the architecture reference doc.
- The 3D versor sandwich this task once "fed" **landed independently** (even-versor/quaternion route in
  `Sandwich.lean`), not via the projection decomposition.

## Follow-on

The audit of how much more of the proof layer can be made coordinate-free is its own task:
`tasks/lean-proofs-make-coordinate-free.md`.
