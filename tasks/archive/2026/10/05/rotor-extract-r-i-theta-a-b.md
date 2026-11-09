# Extract r, I, θ (and a, b, conjugate) from a versor (Macdonald p85–86)

**Created:** 2026-08-27 · **Completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>) for `r`,
`I`, `θ` and the conjugate; "a and b" was answered as not a method, and the Macdonald page citation was
left to the maintainer.

## Summary

The maintainer's idea, verbatim: *"For vectors u,v, calculate r, I and theta, Macdonald page 85, and a and
b, and provide way to get complex conjugate, also on same page. As I think about this more from page 85,
I believe the u times v creates the rotor, so it's from that rotor that we can extract r, I, and theta.
I think this can work for gn, as well as be generated on all the rotor implementation. As I think about
it more, I think I do want to be able to extract a, B and I. Because from the rotor itself, I may be
scaled by some magnitude. To calculate R, look at page 86."*

From a versor `R = u * v`, the library now reads back its magnitude `r`, unit plane `I`, angle `θ`, and the
conjugate, on `Gn` and every generated algebra. Since gacalc 0.1.0 (`tasks/archive/2026/10/04/rename-rotor-to-versor.md`)
`u * v` is an un-normalized even versor, so the scaled case `R R̃ ≠ 1` was the default, not an edge case.

Starting state (2026-08-27, re-checked 2026-10-04): the generated `Versor.plane_of_rotation()` already gave
`I` in `g2`/`g3`, but there was no angle, magnitude-as-`r` or conjugate reader. The Lean side already had
`Rotation2D.uvec_mul_uvec` (`(uvec α)(uvec β) = rotor (β − α)`, θ extraction in 2D) and the
`MathlibBridge.lean` identification of the 2D versor sandwich with `Orientation.rotation θ`. The rotor math
and the Macdonald *Survey* citations are in `tasks/reference/unit-bivector-and-rotors.md` §3 and §5.

## Decisions (the maintainer, 2026-10-05)

1. **Runtime methods**, not notebook-only formulas (the maintainer: "methods"). This overrode, for the
   library API, `tasks/reference/book-outline.md` item 25's stance that "θ is a property, not something to
   solve for"; the book may still present it that way, and item 25 was annotated.
2. **Scaled versors: yes.** The methods take any scalar + bivector versor, normalized or not; `r` is the
   magnitude and `θ` is read off the ratio, so scale is irrelevant.
3. **"a and b": not a method.** The generating vectors are not recoverable from `R`: every pair at angle `θ`
   in the plane `I` with `|u||v| = r` gives the same `R`. The even-part reading of "a and b" is already
   `R.scalar_part()` and `R.r_vector_part(2)`. Anything else would be a new ask.
4. **Citation: left with the maintainer.** The docstrings say "Macdonald" without a page, and the reference
   doc cites the *Survey*; the edition/page of p85–86 was owed by the maintainer (the same kind of gate as
   `tasks/archive/2026/10/22/finalize-exp-citation.md`).

## What was done

- **Methods** (`src/gacalc/base.py`, inherited by `Gn` and the generated algebras): `R.magnitude()` is `r`
  (it existed; now documented as such); `R.plane_of_rotation()` is `I` (new on the base class, the
  normalized bivector part; the generated `Versor` keeps its `Bivector`-typed override); `R.angle()` is
  `θ = atan2(|⟨R⟩₂|, ⟨R⟩₀) ∈ [0, π]`, the angle between the two vectors whose product `R` is (the sandwich
  rotates by `2θ`, so `rotor_from_vectors(a, b).angle()` is half the a→b angle); `R.conjugate()` is
  `r * (cos(θ) − I * sin(θ))`, equal to `reverse` for such a versor, kept as its own name for the
  complex-number reading. `angle`/`conjugate` raise `ValueError` on any other grade, so the Clifford
  conjugate / reverse distinction for odd elements never arises.
- **Tests** (`tests/test_versor_extraction.py`, 7): `u v` yields `θ = ∠(u, v)`, `r = |u||v|` and the plane;
  reconstruction `R = r * (cos(θ) + I * sin(θ))` numeric (3D) and symbolic (positive `c`, `s`); the
  half-angle rotor's `angle()` is `φ/2`; conjugate = reverse with `R R̄ = |R|²`; `Gn`; the grade guard.
- **Docs:** README, `CLAUDE.md`, a `CHANGELOG` Added entry; `book-outline.md` item 25 annotated.

Related archived work: `tasks/archive/2026/06/06/document-rotor-methods.md`,
`tasks/archive/2026/08/15/redo-exp-book-referenced.md`, `tasks/archive/2026/07/29/exp-for-rotors.md`, and
`tasks/archive/2026/10/05/lean-rotor-3d-angle-theorem.md` (the θ statement in 3D).
