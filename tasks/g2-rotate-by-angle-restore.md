# Restore a 𝒢₂ rotation by an angle, written as cos(θ) * v + sin(θ) * v.rotate_90_degrees()

**Created:** 2026-11-10 · **Completed:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)

## Summary

The maintainer asked for a search of gacalc's history for removed code like `rotate_90_degrees`,
and for it to be restored where that made sense. The removed code that matched was in
`2081e18766cfaddd222026c2c119fa4a9a85524a` (2026-06-06, "removed unneeded procedures"). That commit
deleted a planar `transforms.rotate(angle)` whose body was the book's rotation formula,
`cos(θ) * v + sin(θ) * rotate_90_degrees(v)`. It came back the way the quarter turn did on
2026-09-06: as a generated, 𝒢₂-only method, `g2.Vector.rotate(angle_in_radians)`.

## What changed

- `tools/gen_specialized.py`: for n == 2 the generator emits `Vector.rotate(angle_in_radians: Real)
  -> Vector` next to `rotate_90_degrees`. Its body is
  `Scalar(cos_angle) * self + Scalar(sin_angle) * self.rotate_90_degrees()`. The `Scalar(...)`
  wrapper follows the maintainer's pyright spelling choice (option 1 of
  `tasks/reference/pyright-sympy-coefficient-typing.md`), so pyright types the result as a `Vector`.
  A float angle uses `math.cos`/`math.sin`; an int or `sympy` angle goes through `sympy`, the same
  split `MultiVectorBase.exp` makes. The `CUSTOM_METHOD_DOCS` entry `vector|rotate` gives the
  doctests, simplest first: 0, π/2, π, agreement with `rotate_90_degrees`, then the symbolic
  `(x, y)` form.
- `book/docs/notebooks/proof-rotate-from-a-to-b.py`: `rotate(v, theta)` calls `v.rotate(theta)`, and
  `rotate_cs` is `cos * v + sin * v.rotate_90_degrees()`. `book/docs/notebooks/proof-projection.py`:
  its local `rotate` uses the same blend. The expanded per-coordinate formulas are gone from both.
- CHANGELOG `[0.1.0]` Added entry (0.1.0 had not been tagged yet); `CLAUDE.md` (the quarter-turn
  bullet and Operators); `tasks/reference/transform-and-composable-function-layer.md`.

## Decisions

- Restored as a **𝒢₂ method**, not as a `transforms` factory. Two reasons:
  - The composable angle rotation for any plane already exists: `plane_rotation(e_1, e_2)(θ)`, a rotor.
  - A dimension-general coordinate `rotate` is the hazard that
    `tasks/archive/2026/06/06/clarify-2d-only-transforms.md` removed: on a vector with an e₃ part it
    produced a trivector.

  The agent made this call under the maintainer's "put it back in if it makes sense" (William
  Emerison Six <billsix@gmail.com>, 2026-11-10).
- Not restored:
  - `rotate_around`: it is `compose([translate(b=c), rotate, translate(b=-c)])`, and no caller wants it.
  - `is_clockwise`/`is_counter_clockwise`: they were unused when removed, and `g2.Vector.sine` gives
    the signed turn direction.
  - `scale_non_uniform_2d`: it is identical to `scale_non_uniform`.
- `book/docs/notebooks/proof-cross.py` (3-D `rotate_xy`/`rotate_xz`/`rotate_yz`) was left for
  `tasks/standard-position-e3-axis-and-vector-rotations.md`, which rewrites the 3-D plane rotations the
  same way.

## Verification

- `entrypoint/format.sh` in the image: ruff, ty and the changelog check were clean.
- `check_doc_regions.py` reported OK, and the suite passed: 1185 passed, 2 skipped (one more than
  before, the new doctest).
- `pyright notebooks/` reported 0 errors.
- The generator was deterministic: two runs produced byte-identical `g2.py`.
- Both book notebooks ran with every `# -> True` / `# -> [0, 0]` claim checked as an assertion.
- A scratch pyright check typed `(3 * e_1 + 4 * e_2).rotate(theta)` as `Vector`.
