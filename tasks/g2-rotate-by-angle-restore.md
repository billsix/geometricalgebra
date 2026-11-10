# Restore a 𝒢₂ rotation by an angle, written as cos(θ) * v + sin(θ) * v.rotate_90_degrees()

**Status:** in progress
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

The maintainer asked for a search of gacalc's history for removed code like `rotate_90_degrees`,
and for it to be restored where that makes sense. `2081e18` (2026-06-06, "removed unneeded
procedures") deleted a planar `transforms.rotate(angle)` whose body was the book's rotation formula,
`cos(θ) * v + sin(θ) * rotate_90_degrees(v)`. Restore it the way the quarter turn came back on
2026-09-06: a generated, 𝒢₂-only method `g2.Vector.rotate(angle_in_radians)`. Done means the method
is generated with doctests, the book notebooks that hand-write the expanded rotation use the
scalar-times-vectors form, CHANGELOG `[Unreleased]` has an Added entry, and `make test` /
`make format` are green.

## Context (read first)

- `tasks/archive/2026/06/06/clarify-2d-only-transforms.md`: why the planar factories went. Applied to
  a 𝒢₃/`Gn` vector, `v * e_12` sends e₃ to a trivector, and a type checker cannot tell a 2-D `Gn` from
  a 3-D one. In 𝒢₂ the e₁e₂ plane is the whole space, so the hazard does not exist.
- `tasks/archive/2026/09/06/add-quarter-turn-to-g2.md`: the precedent (𝒢₂-only, generated, named
  for a concept the reader already knows).
- `book/docs/proof-rotate.rst`, `eq-rotate-formula`: `r(a; θ) = cos(θ) * a + sin(θ) * r(a; π/2)`.
- github.com/billsix/modelviewprojection `917fbe3f`: `Vertex.rotate` as
  `cos(θ) * self + sin(θ) * self.rotate_90_degrees()`.

## Plan

1. `tools/gen_specialized.py`: emit `Vector.rotate(angle_in_radians: Real) -> Vector` for n == 2 next
   to `rotate_90_degrees`, with a `CUSTOM_METHOD_DOCS` entry (simple examples first). Numeric
   preservation as `exp` does: a float angle uses `math.cos`/`math.sin`, anything else `sympy`.
2. Book notebooks: `book/docs/notebooks/proof-rotate-from-a-to-b.py` (`rotate`, `rotate_cs`) and
   `book/docs/notebooks/proof-projection.py` (`rotate`) use the scalar-times-vectors form.
3. CHANGELOG, `CLAUDE.md` (Operators, the quarter-turn bullet), the transform-layer reference doc.

## Decisions

- Restored as a **𝒢₂ method**, not a `transforms` factory: the angle factory for any plane already
  exists (`plane_rotation(e_1, e_2)(θ)`, a rotor), and a dimension-general coordinate rotation is the
  hazard `2081e18` removed. The agent's call under the maintainer's "put it back in if it makes
  sense" (William Emerison Six <billsix@gmail.com>, 2026-11-10).
- Not restored: `rotate_around` (it is `compose([translate(b=c), rotate, translate(b=-c)])`, and no
  caller wants it), `is_clockwise`/`is_counter_clockwise` (unused when removed; `g2.Vector.sine`
  gives the signed turn direction), `scale_non_uniform_2d` (identical to `scale_non_uniform`).
