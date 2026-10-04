# Lean: unit-length rotors, so the sandwich can use reverse instead of inverse

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 6

## BLUF

In the Lean proofs the sandwich is currently `R v R⁻¹` (`inverse`), because `R` is only known to be an
**even versor** (grades 0+2, not necessarily unit length) — gacalc/Python calls this a **versor**,
reserving **rotor** for a *unit-length* versor. Investigate whether we can introduce a **unit-rotor**
object in Lean (a versor with `normSq R = 1`, equivalently `R * reverse R = 1`) and prove the sandwich
for it as `R v R̃` (`reverse`) instead of `R v R⁻¹`. "Done" = either a working `IsRotor`/unit-versor layer
with a `sandwich_reverse`-style theorem, or a written finding that it is not worth it (with the reason).

## Context

- Spun off from the ℝ→object sweep (`tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`,
  which absorbed the earlier statement-lift task), Open Q2. In that
  sweep we lift the `sandwich_preserves_*` family to take an **object versor** `{R} (hR : IsEvenVersor R)
  (hr : normSq R ≠ 0)` rather than loose real components `(s c12 c13 c23)`. `IsEvenVersor` is the
  even-grade predicate (`R.c1 = R.c2 = R.c3 = R.c123 = 0`); it does **not** constrain the magnitude.
- For a **unit** versor (`normSq R = 1`) the inverse equals the reverse (`R⁻¹ = R̃`), so the sandwich
  `R v R⁻¹` simplifies to `R v R̃` — no division, and it's the form textbooks use for rotors. The
  maintainer's terminology (2026-10-03): **versor = even, not necessarily unit; rotor = unit versor**
  (matches the Python naming, where unit length is the distinguishing property).

## Questions to resolve

1. Shape of the unit layer: a bundled structure (versor + a `normSq = 1` proof field) vs a bare predicate
   `IsRotor R := IsEvenVersor R ∧ normSq R = 1`? The bare predicate is lighter and matches `IsEvenVersor`.
2. Which existing sandwich theorems get a unit-`reverse` companion — all of `sandwich_preserves_*`, or
   just a headline `sandwich R v = R v R̃` equality that the others can be rephrased through?
3. Is `R⁻¹ = R̃` for a unit versor already available (or cheap to prove) in the current Lean layer
   (`inverse`/`reverse`/`normSq` defs), so the reverse-form is a thin corollary of the inverse-form?

## Related

- `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` (parent sweep, archived;
  `IsEvenVersor` lives in `Sandwich.lean`).
- `tasks/reference/lean-ga-proof-architecture.md` (proof architecture; versor/sandwich section).
- `tasks/reference/unit-bivector-and-rotors.md` (the Python-side rotor/versor math).
