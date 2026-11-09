# `exp()`: the exponential map, so `exp(bivector)` is a rotor

**Completed:** 2026-07-29

Promoted from row 1 of the gap analysis in `tasks/reference/galgebra-comparison.md` ("exp / log of
rotors & multivectors", Finding 2B: "rotor = exp(bivector) is a core teaching moment; best
near-term win"). Design study: galgebra's `Mv.exp` (github.com/pygae/galgebra `galgebra/mv.py`,
0.6.1rc1) plus a full read of `base.py` / `transforms.py` / the generated `g2.py`/`g3.py` /
`tools/gen_specialized.py`.

> **Later superseded in part:** the hyperbolic branch for a grade-1 vector described below was
> later removed as meaningless in this Euclidean library; `exp` of a vector now raises
> `ValueError` (see `CLAUDE.md` › Operators and `tasks/reference/design-decisions.md`).

## Outcome

`MultiVectorBase.exp()` in `base.py` (grade-structural dispatch, no `hint`; dispatching-add
construction; numeric preservation; doctests showing both the returned values and the equalities),
generated narrowing overrides `Bivector_n.exp() -> Rotor_n` in `tools/gen_specialized.py`, tests in
`test_conformance.py::test_exp`, `test_graded.py::test_exp_narrows_bivector_to_rotor`, and
`tests/test_exp.py` (properties + the two `plane_rotation` agreement gates), plus an exp-map section
in `notebooks/displayrotations.py`.

**Bonus fix found en route:** the generated full classes' `__add__` / `__sub__` crashed on a bare
number/`sympy.Expr` (`G2.from_scalar(1) + 2` → AttributeError), violating
`MultiVectorBase.__add__`'s documented contract; the `linear` emitter now normalizes a Coef rhs via
`from_coef` first.

Gates: `make test` (304 passed), `make check-generated`, `make check-regions`, `make format` (ruff +
ty clean), all passed 2026-07-29. Durable rationale was harvested to
`tasks/reference/design-decisions.md` › "exp() dispatches by grade structure" and "`plane_rotation`
builds its rotor by hand-written trig ON PURPOSE". The follow-up swap investigation concluded
**against** the swap: `tasks/archive/2026/07/29/plane-rotation-via-exp.md` (dropped).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-07-29)

1. **`exp` landed standalone; the `plane_rotation` rewrite was a separate follow-up**
   (`tasks/archive/2026/07/29/plane-rotation-via-exp.md`). The two were kept verified-equal by test
   in this task.
2. **The generator emits typed narrowing overrides in the same change** (`Bivector_n.exp() ->
   Rotor_n`), per `tasks/reference/generated-product-typing.md`.

## The design

- **One method on `MultiVectorBase`: `exp(self) -> MultiVectorBase`.** It builds a *value* (like
  `rotor_from_vectors`), so it lives on the base, not in `transforms` (transform factories only). No
  free function.
- **No `hint` parameter: Euclidean signature makes the sign structural.** galgebra's `hint='-'/'+'`
  exists because arbitrary signatures leave the sign of a symbolic `A²` undecidable. In
  hardcoded-Euclidean gacalc a homogeneous blade's square is `A² = (−1)^(r(r−1)/2)|A|²`, decided by
  grade. Dispatch is a `match` with a mandatory `case _`: **scalar** → `exp` of the coefficient;
  **grade-2 blade** (and the 𝒢₃ grade-3 pseudoscalar, which also squares to −|A|²) →
  `cos(θ) + sin(θ)·Â`, `θ = |A|` (for a bivector this is the rotor, and it comes out unit); **grade-1
  vector** → hyperbolic `cosh(θ) + sinh(θ)·Â` (later removed, see the note above); **`case _`** →
  `ValueError` raised where it is discovered, saying what is supported. There is no general
  fallback: mixed-grade scalar-square inputs are essentially nonexistent in Euclidean 𝒢₁–𝒢₃.
- **Numeric preservation**, per the `magnitude` / `plane_rotation` precedent: float coefficients →
  `math` functions, floats out; int coefficients → sympy exact (`Bivector2.e_12.exp()` is the exact
  `cos(1) + sin(1)·e₁₂`); symbolic stays symbolic.
- **The construction trap:** the return is built through arithmetic that routes into the generated
  `__add__` dispatch (`Â * sin_θ + cos_θ`), never via `type(self).from_coef` / `from_blade_dict`. A
  `Bivector3.from_blade_dict` reads only the three bivector keys, so a scalar part handed to it is
  silently dropped (the `cos` term would vanish with no error). The dispatching add is what widens
  `Bivector3 + scalar` → `Rotor3`; `rotor_from_vectors` already threads this needle.
- **Generator overrides** are thin cast-and-delegate narrowing overrides, the same pattern as the
  generated `dual` override, NOT closed-form trig bodies (the cse machinery is polynomial; the base
  method is already cheap). `Vector_n.exp()` (scalar+vector) and `Trivector3.exp()`
  (scalar+trivector) have no covering graded type and honestly widen to `G_n`.
- **Teaching bridge:** the rotor `plane_rotation` hand-builds is
  `R = cos(θ/2) − sin(θ/2)·i = exp(−(θ/2)·i)`; a doctest shows `exp((-θ/2) * i)` equals the
  `plane_rotation` rotor, and `notebooks/displayrotations.py` got a demo cell.
- **Citation:** the docstring cites the defining power series and the trig/hyperbolic split. No
  Hestenes & Sobczyk page number was located during design, so none was invented.

## Tests

- `tests/test_conformance.py`: `test_exp` parametrized over the existing `CASES` (build in `Gn`,
  convert via interchange, compare back).
- `tests/test_graded.py`: `Bivector2.e_12.exp()` is a `Rotor2` of unit magnitude; ditto 𝒢₃.
- Properties: `exp(B).inverse() == exp(-B)`; `exp(zero) == one`; float-in-float-out; the
  `exp((-θ/2)·î)` sandwich agrees with `plane_rotation(a, b)(θ)` for numeric AND symbolic θ.
- Docstring doctests run via `--doctest-modules`.

## Out of scope

- `log` (neither library has it). For rotors it would be cheap
  (`θ/2 = atan2(|⟨R⟩₂|, ⟨R⟩₀)`, `log R = (θ/2)·plane_of_rotation()`), and exp+log give slerp; noted
  for a possible future task.
- General-multivector `exp` beyond scalar-square inputs.
- The `plane_rotation` internals swap (`tasks/archive/2026/07/29/plane-rotation-via-exp.md`).
