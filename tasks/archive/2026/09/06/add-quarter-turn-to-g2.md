# Add a g2 `rotate_90_degrees` — a 90° turn in the e₁e₂ plane (= × pseudoscalar)

**Status:** done — implemented 2026-09-06 (Fable session), gates green, awaiting the maintainer's
release (the next version is a MINOR bump; the entry sits in `CHANGELOG.md` `[Unreleased]`).
**Priority:** 7
**Difficulty:** 3

## BLUF

𝒢₂ now has a named quarter turn in two forms that share one generated closed form: the method
`g2.Vector.rotate_90_degrees()` and the module-level factory `g2.rotate_90_degrees()` returning an
`InvertibleFunction[Vector]`. Both ARE `v * e_12` — multiplication by the unit pseudoscalar,
`(x, y) -> (-y, x)` — so the turn is exact (ints stay ints, symbols stay symbolic; no `cos`/`sin`),
composes (four turns are the identity), inverts (the −90° turn, `v * -e_12`), and interpolates
(`at(t)` runs `plane_rotation(e_1, e_2)(t·π/2)`, the exact turn at `t >= 1`). 𝒢₂ only.

## Context

- Researched 2026-09-04 as a standalone design question: does the library want a named convenience
  over the raw `v * e_12`? The pedagogical value is that the name is a labelled doorway to a
  foundational 2-D GA identity, and the `InvertibleFunction` form composes/inverts.
- **Why 𝒢₂-only.** gacalc once had a general planar `rotate_90_degrees` and removed it because it
  acted only in the e₁e₂ plane and silently mis-transformed a vector with an e₃+ component
  (`transforms.py` module docstring) — `× e_12` sends `e_3` to a trivector in 3-D. In 2-D the e₁e₂
  plane is the whole space, so the footgun does not exist.
- **Precedent.** 𝒢₃'s generated `Vector.cross` — dimension-specific, closed-form, type-precise
  (`tasks/archive/2026/08/31/generated-vector-cross.md`). The quarter turn is its 2-D analogue.
- **Why not `plane_rotation(e_1, e_2)(π/2)`.** That is the general-angle rotor from `cos`/`sin`; a
  float π/2 gives round-off. A quarter turn is the pseudoscalar product, exact and angle-free.
- **Direction.** `v * e_12 = (-y, x)` is +90° (e₁ toward e₂), the same positive sense as
  `plane_rotation` (gated in the tests).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-09-06)

1. **Wanted:** "named functions for a concept that they should know already are good."
2. **Form: both** — the `InvertibleFunction` factory and the `Vector` method.
3. **Name: `rotate_90_degrees`** — "if it were to be negative, that would be in the name, and we can
   assume 90 is positive." So no `_ccw` suffix.
4. **𝒢₂ only, confirmed.**

Implementation choices made by the agent within those decisions:

- **Guard raises `TypeError`, not the `ValueError` this doc first sketched** — it matches
  `plane_rotation`'s grade check (`TypeError` for a wrong-grade operand; `ValueError` there is
  reserved for a zero bivector). The guard is `type(vector) is not Vector` (the classes are
  `@typing.final`), so a 𝒢₃ vector, a scalar, or a bivector all raise.
- **Both closed forms are derived, not hand-written:** the method via `unary_result` over
  `v * e_12` and the factory's inverse via `unary_result` over `v * -e_12`, so the two cannot drift.
- **The factory's `interpolate` uses `plane_rotation`** (the sanctioned rotor), which is why `g2.py`
  now imports `gacalc.transforms` — acyclic (`transforms` imports only `base`/`functions`).
- **Doc-region markers** `rotate_90_degrees factory` / `rotate_90_degrees body` wrap the factory
  (the auto `Vector rotate_90_degrees method` region wraps the method) for a book to include.

## What shipped

- `tools/gen_specialized.py`: `ROTATE_90_METHOD_DOC` / `ROTATE_90_FACTORY_DOC`; an `n == 2` arm in
  `vector_extras` (beside the `n == 3` `cross` arm); `generate_quarter_turn(name)`; the n == 2
  header imports (`Linearity`, `plane_rotation`); `rotate_90_degrees` in `g2.__all__`.
- `tests/test_rotate_90_degrees.py` (11 tests): pseudoscalar identity, exactness on ints and
  symbols, direction vs `plane_rotation(π/2)`, factory ≡ method ≡ product, inverse, composition,
  `at(t)` endpoints and midpoint, metadata, the guard, and 𝒢₁/𝒢₃ absence.
- `CHANGELOG.md` `[Unreleased]` › Added; `CLAUDE.md` (module layout, operators list, rotation
  convention); `README.md` quarter-turn paragraph;
  `tasks/reference/transform-and-composable-function-layer.md` rotation-factories bullet.
- Gates (run in the modelviewprojection image, 2026-09-06): ruff check + format clean, ty clean,
  427 tests pass, regeneration byte-stable across two runs, doc-region markers unique/prefix-free.

## Consumer

modelviewprojection's `tasks/swap-myriapod-rotate90-to-gacalc.md` (github.com/billsix/modelviewprojection)
stays blocked on a *release* containing this; once cut and the pin bumped there, myriapod deletes
its local copy and imports `gacalc.g2.rotate_90_degrees`.
