# `Real` vs `Scalar` — what each word names in gacalc, and why (decision record)

**Reference document** — the naming decision for the grade-0 / real-number boundary, decided
2026-10-05 (William Emerison Six <billsix@gmail.com>) on the analysis in
`tasks/archive/2026/10/05/consider-renaming-scalar-to-real.md`. The rename landed 2026-10-05 (`tasks/archive/2026/10/05/consider-renaming-scalar-to-real.md`). Update in place.

## The rule in one line

**`Real` is a Python real number — `int | float | sympy.Expr`, the thing you put into the algebra and
read back out. `Scalar` is the grade-0 *element of the algebra* — a multivector.** They denote the same
mathematical object and are different Python types on purpose.

## Why the distinction exists (a deliberate deviation from Hestenes)

On paper Hestenes treats the real number `5` and the grade-0 multivector `5` as one object; nothing in
the notation needs a boundary. In Python there is one: `5` is an `int`, `5 * one` is a `Scalar`, and by
the symbolic-equality contract a multivector is never `==` a bare number
(`tasks/reference/symbolic-equality.md`). Naming the *number* `Real` and the *element* `Scalar` tells
the reader which side of that type boundary a value is on. This is not a disagreement with the math;
it is a consequence of Python's type system drawing a line the paper did not need.

**Reals cross the boundary; algebra elements stay inside.** A real goes *in* through the one
constructor `from_real`, and comes *out* only through a named extraction — `scalar_part()`,
`coefficient(blade)`, `magnitude()` / `magnitude_squared()` / `abs()`, `scalar_product()`,
`cosine()`, iteration — all of which return a `Real`, because `mag < 1.0`, `math.sqrt`, numpy and
`scalar_part() == 0` must keep working on a plain number. Algebra operations that happen to land in
grade 0 (`A * B`, projections, `exp`) return the typed element `Scalar`. That asymmetry
(`scalar_product` returns a real, `A * B` a `Scalar`) is the boundary working, not an inconsistency.

## The map — what is renamed, what is kept

| name | sense | decision |
|---|---|---|
| `Coef` (type alias `int \| float \| sympy.Expr`) | the Python real, in and out | **→ `Real`** |
| `BladeCoef` (blade → coefficient dict) | the interchange of reals | **→ `BladeReal`** |
| `MultiVectorBase.from_scalar(scalar)` | lift a number into the algebra | **→ `from_real(real: Real)`** |
| `MultiVectorBase.from_coef(expr)` | the symbolic sibling of the above | **folded into `from_real`** (removed) |
| `Scalar` / `Scalar_n` (generated grade-0 class) | the algebra element | **keep** |
| `coeff_scalar` (generated grade-0 field) | the element's coordinate | **keep** |
| `scalar_part()`, `scalar_product()` | GA literature terms (⟨A⟩₀, ⟨A B⟩) | **keep** |
| `is_scalar()` | the `is_<grade>` predicate family | **keep** |
| `pseudoscalar`, `unit_pseudoscalar*`, `pseudoscalar_squared_sign` | one GA word, not "pseudo" + our scalar | **keep** |
| generator internals (`scalar_spec`, `generate_scalar`, …) | mirror the kept class name | **keep** |

So after the rename the API reads: `Scalar.from_real(3)` lifts the real `3` into the grade-0 element;
`(3 * one).scalar_part()` is the real `3` back; `v.magnitude()` is a `Real`. The constructor is named
for what goes in; the part/product methods keep the literature's word for the grade-0 *element*.

## Compatibility

A hard break (no deprecation alias): `CHANGELOG` BREAKING entry and a version bump, the same mechanism as
rotor → versor in 0.1.0 (`tasks/archive/2026/10/04/rename-rotor-to-versor.md`). Checked 2026-10-05: no
in-house consumer calls `from_scalar`/`from_coef` or imports `Coef`/`BladeCoef` (mvp has zero hits).

## Related

- `tasks/archive/2026/10/05/consider-renaming-scalar-to-real.md` — the analysis, the three-senses inventory, the work record
- `tasks/reference/symbolic-equality.md` — why a multivector is never `==` a bare number
- `tasks/reference/graded-subspaces-vs-subalgebras.md` — the grade-pure types the `Scalar` class belongs to
