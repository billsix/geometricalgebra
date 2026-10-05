# Lean: the 3D half-angle rotor rotates by its angle (`bivector_rotation` / `plane_rotation`)

**Status:** proposed — needs go-ahead; the statement form is undecided (open question 1).
**Priority:** 6. **Difficulty:** 6.
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>), spun out of
`tasks/archive/2026/10/04/lean-coverage-extend-transforms-frame-gn.md` at the maintainer's request ("not sure, I don't have
time to think about this now, spin that into its own task"). **Owner:** William Emerison Six
<billsix@gmail.com>.
**See also:** `tasks/reference/lean-proof-corpus-review-2026-10-04.md` §3 (gap #4),
`tasks/reference/lean-ga-proof-architecture.md`, `tasks/reference/unit-bivector-and-rotors.md`,
`tasks/archive/2026/10/05/lean-unit-versors-rotors-sandwich-with-reverse.md` (the unit-rotor layer this builds on — `Sandwich.IsRotor`, landed 2026-10-05; the from-vectors rotor
`Rotor.rotorFromVectors` + the 2D half-angle identification `rotorFromVectors_uvec`:
`tasks/archive/2026/10/05/lean-rotor-from-vectors-chain.md`).

## BLUF

Python's `transforms.bivector_rotation(B, θ)` and `plane_rotation(a, b, θ)` build the half-angle rotor
`R = cos(θ/2) − sin(θ/2)·i` for a unit bivector `i` and apply it as `R v R̃`. Lean proves this rotates by
`θ` only in 𝒢₂ for the `e₁₂` plane (`Rotation2D.sandwich_versor`); in 𝒢₃ it proves the rotor is unit
(`Exp.normSq_expBivectorGeneral`) and that any even versor fixes its own plane and normal
(`Sandwich.sandwich_fixes_own_bivector`/`_normal`), but no theorem connects the **angle** to the sandwich
for a general plane. This is the gap with the most Python resting on it. "Done" = a 𝒢₃ theorem that, for a
unit bivector `i` and `R = cos(θ/2) − sin(θ/2)·i`, the sandwich rotates the in-plane part of `v` by `θ` and
fixes the perpendicular part; `make lean` green; coverage table row updated.

## Context — how to read this cold

- Lean's `G3` is a coordinate struct; proofs are "objects in, scalars in the body, objects out"
  (`CLAUDE.md` "Coordinates only when needed"). Rotors are not a subtype: `IsEvenVersor R` is a predicate,
  unit-ness is `normSq R = 1` (`Sandwich.IsRotor`, landed 2026-10-05).
- The natural route is **reduce to standard position**: `CrossStandardPosition.reduceToPlane` carries any
  plane into `e₁₂` by three elementary rotations that preserve dot and are equivariant for proj/reject/cross;
  in the `e₁₂` plane `Rotation2D.sandwich_versor` (𝒢₂) or `Sandwich.sandwich_fixes_orthogonal`/
  `sandwich_plane_invariant` (𝒢₃, `e₁₂`-plane versor, still coordinate-literal) do the rest. The missing
  piece is the 𝒢₃ angle statement in the `e₁₂` plane plus the transport.
- The interpolation law `bivector_rotation(θ).at(t) = bivector_rotation(t·θ)` is **definitional** — the
  factory rebuilds the rotor with `t·θ` (`transforms.py` docstrings: "`rotation(theta).at(t)` is
  `rotation(t * theta)`"), recorded as "plumbing — no theorem" in the architecture doc's coverage map.
  Nothing to prove here.
- Build nested with the direct `check.sh` recipe in `lean-ga-proof-architecture.md` "Build discipline".

## Open questions

1. State the theorem as (a) a student-facing `cos_between (R v R̃) v = cos θ` for in-plane `v`, plus "the
   ⊥ part is fixed" — matching what `plane_rotation`'s docstring promises and the `StudentTrigForms`
   style; or (b) the stronger coordinate statement that the in-plane part is rotated by `θ` (an equality
   of vectors, orientation included)? Recommendation: (b) as the leaf, (a) as the corollary, since (a)
   alone does not fix the direction of rotation.
