# Lean: unit-length rotors, so the sandwich can use reverse instead of inverse

**Status:** done 2026-10-05 (gate `[lean] OK`); archived 2026-10-05
**Priority:** 6 **Difficulty:** 5
**Created:** 2026-10-03 **Completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>)
**Harvested to:** `tasks/reference/lean-ga-proof-architecture.md` (the `IsRotor` paragraph of the versor/sandwich
section, the coverage rows, the "transfer a chain" recipe) and `tasks/reference/unit-bivector-and-rotors.md`
(§6 vocabulary, §7 the rotor chain, §8 the 2D pedagogy).
**Follow-ons, all done the same day:** `lean-rot-on-g2-named-components.md`, `python-book-rotor-naming-after-lean.md`,
`lean-rotor-from-vectors-chain.md`, `python-rotor-from-vectors-lagrange.md` (this directory).

## BLUF

Added a **rotor** layer to the Lean proofs — `IsRotor R := IsEvenVersor R ∧ normSq R = 1` in both grades, with
`inverse_eq_reverse_of_isRotor` (`R⁻¹ = R̃`) and the headline `sandwich_eq_reverse_sandwich_of_isRotor`
(`sandwich R v = R v R̃`) — and aligned the 2D names to the maintainer's vocabulary (**versor** = even, any
magnitude; **rotor** = unit versor, the sandwich object): the half-angle sandwich object became `Rotation2D.rotor θ`
and the one-sided full-angle teaching operator became `fullAngleRotor θ`. No versor theorem was removed or weakened.

## Context

- Spun off from the ℝ→object sweep (`tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`, Open Q2).
  That sweep lifted the `sandwich_preserves_*` family to an object versor `{R} (hR : IsEvenVersor R) (hr : normSq R ≠ 0)`;
  `IsEvenVersor` says nothing about magnitude, so the sandwich had to stay in the inverse form `R v R⁻¹`.
- For a unit versor the inverse is the reverse, so `R v R⁻¹` becomes the textbook `R v R̃`. The Python package already
  used the vocabulary (class `Versor`; `versor_from_vectors` / `versor_rotation` un-normalized with `R v R⁻¹`;
  `rotor_for` the half-angle unit object). Lean was the side out of step.
- Before this task two sandwich spellings coexisted without a shared notion of "unit": `Sandwich.sandwich` was
  `R v R⁻¹`, while `Rotation2D` stated `R v R̃` for its half-angle object (then named `versor θ`, unit by
  `versor_unit`) and `Exp` proved `exp` of a bivector unit.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-05)

1. **Shape: a bare predicate** `IsRotor`, matching `IsVector`/`IsEvenVersor` house style. No bundled structure.
2. **Scope: the headline equality only.** No `_reverse` companion per `sandwich_preserves_*` theorem: with
   `normSq_ne_zero_of_isRotor` a rotor feeds every existing theorem unchanged, and any rotor-form statement is one
   `rw` away. (Mid-session the maintainer confirmed the goal was *both* notions side by side — "I assume the versor
   proofs for rotation and the sandwich will persist … I would like it to" — verified by a before/after diff of all
   declaration names: the ten names that disappeared were exactly the renamed ones.)
3. **`R⁻¹ = R̃` for a unit versor was cheap** (read off the corpus on 2026-10-04): `inverse a := smul (1 / normSq a)
   (reverse a)` in both grades, so it is `rw [inverse, h, div_one, one_smul]`.
4. **The 2D names, and why there are deliberately two objects.** The maintainer explained the pedagogy: in 2D nothing
   is perpendicular to the plane, so a vector rotates by the **full** angle under a **one-sided** product
   `v · (cos θ + sin θ e₁₂)` — the students' intuitive first encounter. The **half-angle sandwich** object is then
   introduced and proven equal in effect, and it is the form that carries to 3D. So the half-angle object takes the
   name `rotor` (consistent with 3D and with Python's `rotor_for`), and the full-angle one-sided operator needed a
   throwaway name. Five candidates were offered (`fullAngleRotor`, `oneSidedRotor`, `rightRotor`, `complexRotor`,
   `turn`); the maintainer chose **`fullAngleRotor`**, applied also to `rotorFromTo` → `fullAngleRotorFromTo`.
5. **Python naming was checked after the Lean work, not before** (the maintainer's ordering) — filed as
   `python-book-rotor-naming-after-lean.md`.

## What was done

1. **The rotor layer** (`Sandwich.lean`, both grades): `IsRotor`, `IsRotor.isEvenVersor`, `IsRotor.normSq_eq_one`,
   `normSq_ne_zero_of_isRotor`, `isRotor_of_mul_reverse_eq_one` (how an object proven unit as `R R̃ = 1` enters),
   `mul_reverse_self_of_isRotor`/`reverse_mul_self_of_isRotor`, `inverse_eq_reverse_of_isRotor`, and the headline
   `sandwich_eq_reverse_sandwich_of_isRotor`. Instances: `Exp.isRotor_expBivector`/`_12`/`General`,
   `Rotation2D.isRotor_rotor`, plus `Rotation2D.sandwich_rotor_eq_rot` (gacalc's inverse sandwich with the half-angle
   rotor IS the rotation — the two spellings unified). `Rotation2D` gained `import GacalcProofs.Sandwich` (no cycle).
2. **The rename.** Half-angle: `versor θ` → `rotor θ`, `versor_unit`/`'` → `rotor_unit`/`'`, `sandwich_versor` →
   `sandwich_rotor`, `versor_mul` → `rotor_mul`, `MathlibBridge.versor_sandwich_eq_rotation` →
   `rotor_sandwich_eq_rotation`. Full-angle: `rotor θ` → `fullAngleRotor θ`, `vec_mul_rotor` →
   `vec_mul_fullAngleRotor`, `rotorFromTo(_carry)` → `fullAngleRotorFromTo(_carry)`,
   `sandwich_versor_eq_vec_mul_rotor` → `sandwich_rotor_eq_vec_mul_fullAngleRotor`. Applied in `Rotation2D`,
   `MathlibBridge`, and the three files whose docstrings cite `sandwich_rotor`; the `Rotation2D` header now explains
   the two-object pedagogy. Docs: `proofs/README.md`, the architecture doc, the corpus review.
3. `CHANGELOG.md` `[Unreleased]` → Changed, a Lean-only entry.

Gate: `proofs/check.sh` nested against the host image → `[lean] OK`, the edited modules with no warnings. The
maintainer committed the layer and the rename as two commits (`d7b9727`, `9d834c5`).

## A question that became its own task

Reading `G2.vec (rot θ (x, y)).1 (rot θ (x, y)).2`, the maintainer asked what `.1`/`.2` were and why they had no
names. They were pair projections of a bare `ℝ × ℝ`, because `rot` predated the algebra. Fixed the same day in
`lean-rot-on-g2-named-components.md`.

## Related

- `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` (parent sweep)
- `tasks/reference/lean-ga-proof-architecture.md`, `tasks/reference/unit-bivector-and-rotors.md`
- `tasks/lean-rotor-3d-angle-theorem.md` (the 3D angle theorem, started 2026-10-05 from this layer)
