# `exp()` — the exponential map, so `exp(bivector)` is a rotor

**Status:** DONE 2026-07-29 — implemented, all four gates green, archived.

## Outcome

Landed as designed: `MultiVectorBase.exp()` in `base.py` (grade-structural
dispatch, no `hint`; dispatching-add construction; numeric preservation;
doctests showing both the returned values and the equalities), generated
narrowing overrides `Bivector_n.exp() -> Rotor_n` in
`tools/gen_specialized.py`, tests in `test_conformance.py::test_exp`,
`test_graded.py::test_exp_narrows_bivector_to_rotor`, and `tests/test_exp.py`
(properties + the two plane_rotation agreement gates), plus an exp-map section
in `notebooks/displayrotations.py`.

**Bonus fix uncovered en route:** the generated full classes' `__add__` /
`__sub__` crashed on a bare number/`sympy.Expr` (`G2.from_scalar(1) + 2` →
AttributeError), violating `MultiVectorBase.__add__`'s documented contract;
the `linear` emitter now normalizes a Coef rhs via `from_coef` first.

Gates: `make test` (304 passed), `make check-generated`, `make check-regions`,
`make format` (ruff + ty clean) — all PASSED 2026-07-29.

Durable rationale harvested to `tasks/reference/design-decisions.md` › "exp()
dispatches by grade structure" and "`plane_rotation` builds its rotor by
hand-written trig ON PURPOSE". The follow-up swap investigation concluded
**against** the swap — see `tasks/archive/2026/07/29/plane-rotation-via-exp.md` (dropped).

---

*Original design record below.*

Promoted from **row 1 of the gap analysis** in
`tasks/reference/galgebra-comparison.md` ("exp / log of rotors & multivectors",
Finding 2B — "rotor = exp(bivector) is a core teaching moment; best near-term
win"). Design study: galgebra's `Mv.exp` (`galgebra/mv.py:1218` in the mounted
0.6.1rc1 checkout) plus a full read of `base.py` / `transforms.py` / the
generated `g2.py`/`g3.py` / `tools/gen_specialized.py`.

## Decisions (Bill, 2026-07-29)

1. **`exp` lands standalone; the `plane_rotation` rewrite is a separate
   follow-up** — see `tasks/archive/2026/07/29/plane-rotation-via-exp.md` (dropped). The two stay
   verified-equal by test in this task; the internals swap happens there.
2. **The generator emits typed narrowing overrides in the same change**
   (`Bivector_n.exp() -> Rotor_n`), per the repo's typing standard
   (`tasks/reference/generated-product-typing.md`).

## The design

**One method on `MultiVectorBase` in `base.py`: `exp(self) -> MultiVectorBase`.**
It builds a *value* (like `rotor_from_vectors`), so it lives on the base, not in
`transforms` (transform *factories* only). No free function.

**No `hint` parameter — Euclidean signature makes the sign structural.**
galgebra's `hint='-'/'+'` exists only because arbitrary signatures leave the
sign of a symbolic `A²` undecidable. In hardcoded-Euclidean gacalc the sign of a
homogeneous blade's square is decided by **grade**:
`A² = (−1)^(r(r−1)/2)|A|²`. Dispatch with the house `match` + mandatory
`case _`:

- **scalar** → `exp` of the coefficient (`math.exp` float / `sympy.exp`
  otherwise);
- **grade-2 blade** (and the grade-3 pseudoscalar in 𝒢₃ — also squares to
  −|A|²) → trig: `cos(θ) + sin(θ)·Â`, `θ = |A|`. For a bivector this IS the
  rotor, and it comes out **unit** (`cos²+sin²=1`) — test that property;
- **grade-1 vector** → hyperbolic: `cosh(θ) + sinh(θ)·Â`;
- **`case _`** → if `A²` is not scalar, `raise ValueError` from the code that
  discovers it (same contract as galgebra). No general fallback: mixed-grade
  scalar-square inputs are essentially nonexistent in Euclidean 𝒢₁–𝒢₃; say
  what is supported in the message.

**Numeric preservation, per the house convention** (`magnitude` /
`plane_rotation` precedent): float coefficients → `math.cos/sin/cosh/sinh/exp`,
floats out; int coefficients → sympy exact (`Bivector2.e_12.exp()` is the exact
`cos(1) + sin(1)·e₁₂`); symbolic stays symbolic.

**THE construction trap (the one way to silently corrupt the result):** build
the return through **arithmetic that routes into the generated `__add__`
dispatch** — `Â * sin_θ + cos_θ` — and *never* via `type(self).from_coef` /
`from_blade_dict`. A `Bivector3.from_blade_dict` reads only the three bivector
keys, so a scalar part handed to it is **silently dropped** (the `cos` term
would vanish with no error). The dispatching add is what widens
`Bivector3 + scalar` → `Rotor3`; `rotor_from_vectors` already threads this
needle (its `product` is Rotor-typed before the scalar is added).

**Generator overrides (decision 2):** thin cast-and-delegate narrowing
overrides in `tools/gen_specialized.py`, same pattern as the generated `dual`
override — NOT closed-form trig bodies (the cse machinery is polynomial; the
base method is already cheap). `Bivector_n.exp() -> Rotor_n`;
`Vector_n.exp()` (scalar+vector) and `Trivector3.exp()` (scalar+trivector) have
no covering graded type and honestly widen to `G_n` per the resolver's rule.
Remember the workflow: edit the generator, `make generate`, and the healthy
diff shape is `tools/` only (generated files are gitignored).

**Teaching bridge:** the rotor `plane_rotation` hand-builds is
`R = cos(θ/2) − sin(θ/2)·i = exp(−(θ/2)·i)`. A doctest showing
`exp((-θ/2) * i)` equals the `plane_rotation` rotor is the "rotor =
exp(bivector)" moment the comparison doc wanted. Add a demo cell to
`notebooks/displayrotations.py`.

## Tests

- `tests/test_conformance.py`: `test_exp` parametrized over the existing
  `CASES` (build in `Gn`, convert via interchange, compare back).
- `tests/test_graded.py`: `Bivector2.e_12.exp()` is a `Rotor2`; unit
  magnitude; ditto 𝒢₃.
- Properties: `exp(B).inverse() == exp(-B)`; `exp(zero) == one`;
  float-in-float-out (the `test_numeric_magnitude.py` genre);
  `exp((-θ/2)·î)` sandwich agrees with `plane_rotation(a, b)(θ)` for numeric
  AND symbolic θ (this equality also gates the follow-up task).
- Docstring doctests run via `--doctest-modules`.

## Docstring / citation caveat

Cite the defining power series and the trig/hyperbolic split. **No Hestenes &
Sobczyk page number was located during design — do not invent one**; find the
real citation (H&S introduce exp in their spinor/rotation material) or omit.

## Out of scope

- `log` (neither library has it; for *rotors* it's cheap later —
  `θ/2 = atan2(|⟨R⟩₂|, ⟨R⟩₀)`, `log R = (θ/2)·plane_of_rotation()` — and
  exp+log give slerp; note for a future task).
- General-multivector `exp` beyond scalar-square inputs.
- The `plane_rotation` internals swap → `tasks/archive/2026/07/29/plane-rotation-via-exp.md` (dropped).

## Gates

`make test` (conformance + graded + doctests), `make check-generated`
(determinism after the generator change), `format.sh` clean (`ruff` + `ty`),
and `make check-regions` if doc-region markers are added to the new method.
