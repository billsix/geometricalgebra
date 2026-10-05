# Python: `rotor_from_vectors` (the normalized versor) + a sympy proof that uses the Lagrange closed form

**Status:** done 2026-10-05 (679 tests, format/ty, check-generated, check-regions all green); archived 2026-10-05
**Priority:** 5 **Difficulty:** 3
**Created / completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>)
**Harvested to:** `tasks/reference/symbolic-equality.md` (square roots: hand sympy the relation) and
`tasks/reference/unit-bivector-and-rotors.md` §7.

## BLUF

Mirrored `proofs/GacalcProofs/Rotor.lean` on the Python side: added `MultiVectorBase.rotor_from_vectors(from, to)`
= `versor_from_vectors(from, to).normalize()` (a true unit rotor, for the textbook reverse sandwich), typed `Versor`
on `g2`/`g3` vectors through the generator, and tests that prove **symbolically** what the Lean module proves —
including the half-angle identification where the earlier Python attempt had stalled.

## Context

- Followed `lean-rotor-from-vectors-chain.md` (this directory). The maintainer: "I know we did some proof of this
  for the python code in the past, but it had gotten stuck trying to do rotor as a unit … I didn't know the name of
  Lagrange, so we couldn't use his theorem."
- Why sympy stalls: `normalize` divides by `sqrt(|R|²)` with `|R|²` the raw polynomial `(|a||b| + a·b)² + |a∧b|²`.
  Identifying a coefficient like `(|a||b| + a·b)/sqrt(…)` with `cos(θ/2)` needs Lagrange to collapse `|R|²` to
  `2|a||b|(|a||b| + a·b)` and then the half-angle identity — relations sympy does not discover on its own.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-05)

- A named `rotor_from_vectors` rather than only a test on `.normalize()`: it is the Python twin of Lean's
  `rotorFromVectors`, additive, documented with the vocabulary, the bridge identity, and the Lagrange closed form.
- The half-angle proof parametrizes by the **half** angle, `(c, s) = (cos(θ/2), sin(θ/2))` as positive symbols, with
  `b = (2c² − 1)e₁ + 2sc·e₂`, and hands sympy the single relation `s² → 1 − c²` through the comparison helper. Then
  `|b|` collapses to 1, `|R|²` to `4c²`, `sqrt(|R|²)` to `2c`, and the normalized versor to exactly `c − s·e₁₂`.
- Typing (ty): `magnitude_squared()` is `Coef = float | Expr`, so it is wrapped in `sympy.sympify` before
  `.subs`/`simplify`; the substitution map is `Mapping[sympy.Basic | complex, sympy.Expr | complex]` (dict key
  invariance rejects `dict[Expr, Expr]`). The maintainer's reminder mid-task: every binding typed, including
  `InvertibleFunction[g2.Vector]` for a `plane_rotation(...)(θ)` result.

## What was done

- `base.py`: `rotor_from_vectors` classmethod; `tools/gen_specialized.py`: the `Vector`-typed narrowing override
  (`-> Versor`) via `inherited_classmethod_narrowing`, plus a `vector|rotor_from_vectors` docstring.
- `tests/test_rotor_from_vectors.py` (7 tests): the Lagrange closed form of `|R|²` (2D + 3D, fully symbolic); the
  rotor is unit and typed `Versor`; `R̂ v R̂~ = R v R⁻¹ = R̂.sandwich(v) = projection_rotation(v)` (2D symbolic over
  general vectors, 3D concrete) and carries `a` to `b`; the half-angle identification; a numeric check against
  `plane_rotation`'s half-angle rotor at sample angles.
- README, `CLAUDE.md` rotation bullet, `CHANGELOG` `[Unreleased]` → Added.

Gates nested against the existing image: 679 tests, ruff + ty clean, generator deterministic, doc-region markers OK.
Committed by the maintainer in `b27345d`.

## Related

- `lean-rotor-from-vectors-chain.md` (this directory), `proofs/GacalcProofs/Rotor.lean`
- `tasks/reference/unit-bivector-and-rotors.md`, `tasks/reference/symbolic-equality.md`
