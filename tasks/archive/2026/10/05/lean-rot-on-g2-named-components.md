# Lean: define 2D rotation on 𝒢₂ vectors (named components), not on bare `ℝ × ℝ` pairs

**Status:** done 2026-10-05 (gate `[lean] OK`); archived 2026-10-05
**Priority:** 5 **Difficulty:** 3
**Created / completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>)
**Harvested to:** `tasks/reference/lean-ga-proof-architecture.md` ("state on the algebra, not on bare tuples").

## BLUF

`Rotation2D.rot θ` had been defined on a bare coordinate pair `ℝ × ℝ`, so every 2D theorem that landed in the
algebra read `G2.vec (rot θ (x, y)).1 (rot θ (x, y)).2` — anonymous pair projections the maintainer could not read
("what is `.1` and `.2`? couldn't they have names?"). Redefined `rot θ` as a map `G2 → G2` on the **named
components** `c1`/`c2`, restated the 2D theorems on 𝒢₂ vectors, and pointed the Mathlib bridge's `toC` at a 𝒢₂
vector. No `ℝ × ℝ` and no `.1`/`.2` remain in `Rotation2D.lean` or `MathlibBridge.lean`.

## Context

- Spun out of `lean-unit-versors-rotors-sandwich-with-reverse.md` (this directory) from the maintainer's mid-session
  question. The "from scratch" spine was unaffected: `rot` is still defined from sin/cos on two real coordinates —
  they are the named fields of a `G2` vector instead of a tuple. `G2` is a coordinate struct, so this cost nothing
  and removed the pair type from the 2D story entirely.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-05)

1. `rot θ : G2 → G2`, through `G2.vec` on `v.c1`/`v.c2` (returns a vector; a non-vector input's other parts are
   dropped, so the theorems take `IsVector v`).
2. `polar r φ : G2 := vec (r cos φ) (r sin φ)`; the hand-rolled pair `scale` was deleted in favour of `G2.smul`.
3. Object form wherever a vector is involved: `vec_mul_fullAngleRotor`, `sandwich_rotor`,
   `sandwich_rotor_eq_vec_mul_fullAngleRotor`, `sandwich_rotor_eq_rot`, `rot_normSq` take `(θ) {v} (hv : IsVector v)`;
   `rot_add`, `toC_rot`, `toC_rot_rot` hold for every `v` (both sides read only `c1`/`c2`) and stayed unconditional.
   `rot_cossin` became `rot_uvec : rot θ (uvec α) = uvec (α + θ)`, with `isVector_uvec`; a definitional `rot_vec`
   bridges to the two coordinates.
4. `toC (v : G2) : ℂ := ⟨v.c1, v.c2⟩`, so `rotor_sandwich_eq_rotation` is stated directly on the sandwich.

## What was done

Rewrote `Rotation2D.lean` and the rotation section of `MathlibBridge.lean` as above. One proof needed a change
after the retype: `rot_from_to` on components is `ext <;> field_simp <;> ring` (the pair version had been
`constructor <;> field_simp`). Gate `[lean] OK`, both modules with no warnings. `CHANGELOG` Lean entry extended.
Committed by the maintainer in `9d834c5`.

## Related

- `lean-unit-versors-rotors-sandwich-with-reverse.md` (this directory)
- `tasks/reference/lean-ga-proof-architecture.md` ("geometric objects in, scalars in the body")
