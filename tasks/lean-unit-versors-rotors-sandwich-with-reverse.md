# Lean: unit-length rotors, so the sandwich can use reverse instead of inverse

**Status:** proposed — decisions made 2026-10-05, needs go-ahead to implement
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-10-03 **Updated:** 2026-10-05 (William Emerison Six <billsix@gmail.com>)

## BLUF

Add a **rotor** layer to the Lean proofs: a bare predicate `IsRotor R := IsEvenVersor R ∧ normSq R = 1`
(both grades) and the headline theorem that for a rotor the inverse sandwich `R v R⁻¹` equals the reverse
sandwich `R v R̃`. In the same task, fix the 2D names so they match the maintainer's vocabulary
(**versor = even, any magnitude; rotor = unit versor, used in the sandwich**): the half-angle sandwich
object `Rotation2D.versor θ` becomes `rotor θ`, and the full-angle one-sided operator currently named
`rotor θ` becomes `fullAngleRotor θ`. "Done" = `IsRotor` + the headline equality in 𝒢₂ and 𝒢₃,
`isRotor_*` facts for the objects already proven unit, the rename applied across Lean + docs, gate `[lean] OK`.

## Context

- Spun off from the ℝ→object sweep (`tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`,
  which absorbed the earlier statement-lift task), Open Q2. In that
  sweep we lifted the `sandwich_preserves_*` family to take an **object versor** `{R} (hR : IsEvenVersor R)
  (hr : normSq R ≠ 0)` rather than loose real components. `IsEvenVersor` is the even-grade predicate
  (`Sandwich.lean`, both grades); it does **not** constrain the magnitude.
- For a **unit** versor (`normSq R = 1`) the inverse equals the reverse (`R⁻¹ = R̃`), so the sandwich
  `R v R⁻¹` simplifies to `R v R̃` — no division, the textbook rotor form.
- **The Python side already uses this vocabulary** (checked 2026-10-05): the even-grade class is `Versor`;
  `versor_from_vectors` / `versor_rotation` (`transforms.py`) use the unnormalized `R v R⁻¹`; the
  half-angle unit object is built by `_unit_bivector_rotor_factory`'s `rotor_for`. Lean was the side out of
  step (see "The 2D naming" below).
- **Two sandwich spellings coexist today.** `Sandwich.sandwich` (both grades) is `R v R⁻¹`; the 2D
  half-angle layer uses the reverse form — `Rotation2D.sandwich_versor` is stated as
  `mul (mul (versor θ) v) (reverse (versor θ))` with `versor θ := cos(θ/2) − sin(θ/2) e₁₂`, unit by
  `versor_unit`/`versor_unit'`. `Exp.normSq_expBivectorGeneral` proves `exp` of a bivector is unit too.
  Neither is stated through a shared "unit" notion; this task supplies it.

### The 2D naming, and why it is deliberately two objects

`Rotation2D.lean` has two unit even multivectors for the angle θ, and this is **by design, for students**
(William Emerison Six <billsix@gmail.com>, 2026-10-05): in 2D there is no component perpendicular to the
plane, so a vector can be rotated by the **full** angle with a **one-sided** product,
`v * (cos θ + sin θ e₁₂)`, no sandwich needed — the intuitive first encounter. The **half-angle sandwich**
object `cos(θ/2) − sin(θ/2) e₁₂` is then introduced and *proven equal in effect*
(`sandwich_versor_eq_vec_mul_rotor`, already in the file), which is the form that carries over to 3D.
Both objects stay. Only the names move:

| today | after this task | what it is |
|---|---|---|
| `versor θ` | `rotor θ` | half-angle, unit, used in the sandwich `R v R̃` — the rotor consistent with 3D and with Python's `rotor_for` |
| `rotor θ` | `fullAngleRotor θ` | full-angle, unit, used one-sided as `v * fullAngleRotor θ` — the 2D-only teaching object (name chosen 2026-10-05 from five candidates; it is a throwaway pedagogical name) |
| `rotorFromTo α β` | `fullAngleRotorFromTo α β` | `uvec α * uvec β`, full-angle, one-sided — same family as the row above |

Theorem names follow mechanically: `versor_unit`/`versor_unit'` → `rotor_unit`/`rotor_unit'`;
`sandwich_versor` → `sandwich_rotor`; `vec_mul_rotor` → `vec_mul_fullAngleRotor`;
`sandwich_versor_eq_vec_mul_rotor` → `sandwich_rotor_eq_vec_mul_fullAngleRotor`;
`rotorFromTo_carry` → `fullAngleRotorFromTo_carry`; the `versor_mul_versor`-style composition lemmas
in the same section take the `rotor_` prefix.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-05)

1. **Shape: a bare predicate**, `IsRotor R := IsEvenVersor R ∧ normSq R = 1`, matching `IsVector` /
   `IsEvenVersor` house style. No bundled structure.
2. **Scope: the headline equality only** — for `IsRotor R`, `sandwich R v = mul (mul R v) (reverse R)`
   (one theorem per grade), plus the trivial `normSq_ne_zero_of_isRotor` so a rotor can be fed to every
   existing `sandwich_preserves_*` theorem unchanged. **No** `_reverse` companion per theorem: any
   rotor-form statement is one `rw` away from the versor-form one.
3. **`R⁻¹ = R̃` for a unit versor is cheap** (found 2026-10-04 by reading the corpus): `inverse a := smul
   (1 / normSq a) (reverse a)` in both grades, so under `normSq R = 1` the equality is
   `simp [inverse, h]` plus `smul_one`-style cleanup. No new leaf needed.
4. **Rename the 2D objects as in the table above**; `fullAngleRotor` is the full-angle one-sided name.
5. **Python naming is checked AFTER the Lean work lands, not before** (the maintainer's ordering). Expected
   to be small or nil — the package already says `Versor`/`versor_*` for the general case and `rotor_for`
   for the half-angle unit one. The place to look is the book's 2D introduction (the one-sided full-angle
   product in `book/docs/notebooks/geometric-product.py` and its prose), to decide whether it should name
   the object `full_angle_rotor` to mirror Lean. Filed as a follow-on at archive time (see below).

## Plan

1. `Sandwich.lean`, both grades: `def IsRotor`, `isRotor_evenVersor`-style discharge lemma,
   `normSq_ne_zero_of_isRotor`, `inverse_eq_reverse_of_isRotor`, `sandwich_eq_reverse_sandwich_of_isRotor`
   (the headline). Keep `normSq R` atomic per the leaf recipe in `lean-ga-proof-architecture.md`.
2. Instances: `Rotation2D.isRotor_rotor θ` (from `rotor_unit`), `Exp.isRotor_expBivector*` (from the
   `normSq_expBivector*` lemmas), `Versor2D`/`Rotation3D` `versorFromVectors` of **unit** inputs if the
   normalized form exists (otherwise note it is a versor, not a rotor).
3. The rename, as one commit of its own: `Rotation2D.lean`, then the citing files (`Versor2D`,
   `Rotation3D`, `Projection3D`, `MathlibBridge`, `ProjectionRotation2D` if it cites), then the docs
   (`tasks/reference/lean-ga-proof-architecture.md`, the coverage table rows that cite `sandwich_versor`,
   `tasks/reference/unit-bivector-and-rotors.md` if it names the Lean theorems). Re-grep for `sandwich_versor`,
   `versor_unit`, `vec_mul_rotor`, `rotorFromTo` = zero hits outside archives.
4. Gate: `proofs/check.sh` (nested: run it directly, `make lean` rebuilds the image) → `[lean] OK`;
   `make format`.
5. Archive: harvest the rotor/versor section into `lean-ga-proof-architecture.md` (the `IsRotor` layer,
   the 2D two-object pedagogy, the rename), file the Python/book naming follow-on (Decision 5), then
   `/archive-task`.

## Related

- `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` (parent sweep, archived;
  `IsEvenVersor` lives in `Sandwich.lean`).
- `tasks/reference/lean-ga-proof-architecture.md` (proof architecture; versor/sandwich section — it
  already points here for "a rotor is a unit versor").
- `tasks/reference/unit-bivector-and-rotors.md` (the Python-side rotor/versor math; §3 the half-angle
  rotor as `exp(−(θ/2)·i)`).
- `tasks/lean-rotor-3d-angle-theorem.md` (the 3D angle theorem; will want `IsRotor` once it exists).
