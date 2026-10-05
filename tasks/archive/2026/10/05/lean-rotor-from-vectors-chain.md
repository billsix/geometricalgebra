# Lean: the rotor chain — the from-vectors versor, normalized, IS a rotor, and its reverse sandwich IS the versor/projection rotation

**Status:** done 2026-10-05 (gate `[lean] OK`, `Rotor.lean` built with no warnings); archived 2026-10-05
**Priority:** 4 **Difficulty:** 5
**Created / completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>)
**Harvested to:** `tasks/reference/lean-ga-proof-architecture.md` (the rotor paragraph, the "transfer a chain by
normalize + bridge + rw" recipe, coverage rows) and `tasks/reference/unit-bivector-and-rotors.md` §7.
**Python mirror:** `python-rotor-from-vectors-lagrange.md` (this directory).

## BLUF

The versor chain was already proven: `projRotation f t v = sandwich (versorFromVectors f t) v` (inverse sandwich),
carries `a` to `b`, isometry. The maintainer asked for **the same chain for rotors with the reverse sandwich
`R v R̃`**, and framed the two routes himself: duplicate the projection-rotation proof, or "just show that the versor
sandwich implementation, when divided by the magnitudes, is in fact the rotor sandwich implementation. You may need
to use Lagrange." Took the second route: a new module `Rotor.lean` (both grades) with
`rotorFromVectors := normalize ∘ versorFromVectors`, `IsRotor` of it, **one algebraic bridge**
`rotorSandwich (normalize R) v = sandwich R v`, the chain as one-`rw` corollaries, and the Lagrange closed form
`|versorFromVectors a b|² = 2|a||b|(|a||b| + a·b)`.

## Context

- Followed the `IsRotor` layer (`lean-unit-versors-rotors-sandwich-with-reverse.md`, this directory). What was
  missing was the link from the **from-vectors** versor to a rotor: the maintainer's question "did you prove that the
  versor sandwich, using the inverse, is the same as the rotor? like, starting from 'rotate from vector a to b',
  take the half angle, the whole thing?" — the answer then was no.
- The earlier Python-side attempt to normalize the versor symbolically had stalled: sympy cannot simplify
  `sqrt(|R|²)` from the raw polynomial. The identity that unlocks it is Lagrange's `(a·b)² + |a∧b|² = |a|²|b|²`
  (`Trig.lagrange_property`), which the maintainer did not have a name for at the time.

## Decisions and design (William Emerison Six <billsix@gmail.com>, 2026-10-05)

- **Don't duplicate the projection-rotation proof.** `(R/|R|) v (R/|R|)~ = R v R̃/|R|² = R v R⁻¹` holds for every
  `R` with no hypothesis (when `normSq R = 0` both sides are `0`), so `rotorSandwich_normalize` is stated
  unconditionally and proven by six rewrites with explicit arguments (`reverse_smul`, `smul_mul` ×2, `mul_smul`,
  `smul_smul`, the scalar identity `(1/|R|)² = 1/|R|²`, `mul_smul`) — no coordinates. The single `√` fact is
  `magnitude_sq_eq_normSq`, from `normSq_eq_sum_sq` (the scalar part of `a ã` is a sum of squares in both
  grades) and `Real.sq_sqrt`.
- **Lagrange by `ring` in coordinates** inside `normSq_versorFromVectors`, as one `linear_combination` of the two
  facts `|a|² = Σaᵢ²`, `|b|² = Σbᵢ²` (coefficients `−|b|²` and `−Σaᵢ²`), citing `lagrange_property` as the identity
  rather than threading its unfolded form through — the unfolded route was judged more fragile.
- **The 2D coda** was a stretch goal that went through: `versorFromVectors (uvec α) (uvec β) =
  2cos(θ/2) • rotor θ` (θ = β − α) via the double-angle identities, then `rotorFromVectors_uvec = rotor (β − α)`
  for `cos(θ/2) > 0` (not antiparallel) using `|k • R| = |k|` for a rotor and `Real.sqrt_sq`, and finally the
  from-vectors rotor sandwich of two unit directions is `rot (β − α) v` — "rotate from a to b, take the half
  angle, the whole thing".

## What was done

`Rotor.lean` (imports `Sandwich`, `ProjectionRotation2D/3D`, `Rotation2D`), both grades: `normSq_eq_sum_sq`,
`normSq_nonneg`, `magnitude_sq_eq_normSq`, `magnitude_ne_zero_of_normSq_ne_zero`; `normalize`, `normSq_normalize`,
`isEvenVersor_smul`, `isRotor_normalize`; `rotorSandwich`, `sandwich_eq_rotorSandwich_of_isRotor`,
**`rotorSandwich_normalize`**, `rotorSandwich_preserves_dot/normSq/magnitude`; `isEvenVersor_versorFromVectors`,
`rotorFromVectors`, `isRotor_rotorFromVectors`, `rotorSandwich_rotorFromVectors`,
`rotorSandwich_rotorFromVectors_eq_projRotation`, `rotorSandwich_rotorFromVectors_carries_from_to`;
`normSq_versorFromVectors`, `normSq_versorFromVectors_ne_zero`. 2D coda: `normSq_uvec`, `magnitude_uvec`,
`versorFromVectors_uvec`, `rotorFromVectors_uvec`, `rotorSandwich_rotorFromVectors_uvec`. Built on the first pass.
Docs: `proofs/README.md` (30 modules), the architecture doc, `unit-bivector-and-rotors.md` §6 status, `CHANGELOG`.
Committed by the maintainer in `6ab8028`.

## Related

- `tasks/reference/lean-ga-proof-architecture.md`, `tasks/reference/unit-bivector-and-rotors.md`
- `tasks/lean-rotor-3d-angle-theorem.md` (starts from `rotorFromVectors` / the `IsRotor` layer)
