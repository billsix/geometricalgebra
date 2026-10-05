# Lean: the 3D half-angle rotor rotates by its angle (`bivector_rotation` / `plane_rotation`)

**Status:** done 2026-10-05 (gate `[lean] OK`, `PlaneRotation3D.lean` built with no warnings); archived 2026-10-05
**Priority:** 6 **Difficulty:** 6
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>), spun out of
`tasks/archive/2026/10/04/lean-coverage-extend-transforms-frame-gn.md`. **Completed:** 2026-10-05.
**Harvested to:** `tasks/reference/lean-ga-proof-architecture.md` (the rotor paragraph + the coverage row),
`tasks/reference/unit-bivector-and-rotors.md` §7 item 5.
**Ad-hoc script:** `tasks/adhoc/lean-rotor-3d-angle-theorem/cofactors.py` (one-shot; removed in the archive commit —
its output is baked into the proof, and the technique is described in the module header and the architecture doc).

## BLUF

Python's `transforms.bivector_rotation(B)(θ)` / `plane_rotation(a, b)(θ)` build the half-angle rotor
`R = cos(θ/2) − sin(θ/2)·i` for a unit bivector `i` and apply `R v R̃`. Lean had proven this rotates by θ only in
𝒢₂ for the `e₁₂` plane; in 𝒢₃ it had unit-ness and "fixes its own plane and normal", but no theorem connected
the **angle** to the sandwich for a general plane. Proved it: `PlaneRotation3D.rotorSandwich_planeRotor`,
`R v R̃ = reject i v + cos θ · project_onto i v + sin θ · inner_vb v i` for every vector `v` — perpendicular
part fixed, in-plane part rotated by θ with orientation — plus the student-facing
`cos_between (R v R̃) v = cos θ` for in-plane `v` and "the normal is fixed".

## Context

- Lean's `G3` is a coordinate struct; rotors are the predicate `IsRotor` (`Sandwich.lean`, 2026-10-05), and the
  reverse sandwich is `Rotor.rotorSandwich`. `project_onto i v = (v ⌋ i) i⁻¹`, `reject i v = (v ∧ i) i⁻¹`,
  `inner_vb v i` = the grade-1 part of `v i` = `v ⌋ i` (`Projection3D.lean`).
- The interpolation law `bivector_rotation(θ).at(t) = bivector_rotation(t·θ)` is definitional (the factory
  rebuilds the rotor with `t·θ`); nothing to prove, recorded as plumbing in the coverage map.

## The open question, and how it was resolved

The task had one open question: state the theorem as (a) the student-facing `cos_between (R v R̃) v = cos θ`
plus "⊥ fixed", or (b) the vector equality with orientation. Its own recommendation was (b) as the leaf and (a)
as the corollary, because (a) alone does not fix the direction of rotation. The maintainer's instruction was
"do the 3D rotor angle theorem next" without answering the question explicitly; the recommendation was taken
(both forms delivered) and flagged in the report.

## Design (2026-10-05)

- **Coordinate leaf, not reduction to standard position.** The standard-position route (carry the plane to
  `e₁₂` with `CrossStandardPosition.reduceToPlane`, use the 2D result, transport back) needs the sandwich's
  equivariance under those rotations — more machinery than the statement is worth. Instead: unfold everything
  (with `|i|² = 1`, `i⁻¹ = ĩ`), substitute the double-angle identities for `cos θ`, `sin θ`, and each vector
  component becomes a polynomial identity modulo the two relations `cos²(θ/2) + sin²(θ/2) = 1` and
  `|i|² = 1`; the scalar/bivector/trivector components vanish identically (`ring`).
- **Cofactors computed offline, pasted in.** `linear_combination` needs the multipliers of the two relations.
  They were found with sympy's `reduced` (multivariate division) over gacalc's own 𝒢₃ product — the product
  Lean's `G3.mul` was transcribed from, so the polynomial difference is identical — and came out small
  (e.g. for `c1`: `(−p²x + prz − q²x − qry + x)·hcs + x(s − 1)(s + 1)·hpqr`). Zero remainder in sympy is the
  proof the identity holds; Lean's `ring` then checks the pasted combination. The harness is
  `tasks/adhoc/lean-rotor-3d-angle-theorem/cofactors.py`.
- **"⊥ fixed" stated on the normal itself** (`smul k (vec i.c23 (−i.c13) i.c12)`, the vector that commutes
  with `i`), the same shape as `sandwich_fixes_own_normal`; the cofactors there are by hand
  (`v_comp · hcs + v_comp · sin²(θ/2) · hpqr`, from `(c − s i) v (c + s i) = v(c² + s²|i|²)` for commuting `v`).
- **The cosine corollary** reuses the layer: `rotorSandwich_preserves_magnitude` (isometry), the leaf with
  `reject i v = 0` and `project_onto i v = v` (from `project_add_reject`), and `(v ⌋ i)·v = 0` by `ring`.

## What was done

`PlaneRotation3D.lean` (imports `Sandwich`, `Projection3D`, `Trig`, `Rotor`): `planeRotor`,
`isEvenVersor_planeRotor`, `sum_sq_of_unit_bivector`, `normSq_planeRotor`, `isRotor_planeRotor`,
**`rotorSandwich_planeRotor`**, `cos_between_rotorSandwich_planeRotor`, `rotorSandwich_planeRotor_fixes_normal`.
One build iteration: inside `namespace GacalcProofs.G3` the bare name `cos_sq_add_sin_sq` resolves to the
corpus's own angle theorem (`Trig.lean`), not Mathlib's — qualified as `Real.cos_sq_add_sin_sq`. Docs:
`proofs/README.md` (31 modules), the architecture doc (coverage row PARTIAL → HAS, remaining-threads lists), the
corpus review item 6, `unit-bivector-and-rotors.md` §7, `lean-for-gacalc.md`, `CHANGELOG`.

Not done, deliberately: relating `planeRotor θ i` to `Exp.expBivectorGeneral` (`R = exp(−(θ/2)·i)`) — a
one-line definitional unfolding away if ever wanted, not needed for the coverage claim.

## Related

- `tasks/archive/2026/10/05/lean-unit-versors-rotors-sandwich-with-reverse.md`,
  `tasks/archive/2026/10/05/lean-rotor-from-vectors-chain.md` (the layer this builds on)
- `tasks/reference/lean-proof-corpus-review-2026-10-04.md` §3 (gap #4, now closed)
