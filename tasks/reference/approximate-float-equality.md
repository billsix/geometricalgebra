# Approximate floating-point equality — the landscape, and gacalc's choice

**Reference document** — why `MultiVectorBase.isclose` works the way
it does, and the standard practice it follows. Not a task; update in place if the
method changes. Created 2026-08-02 (from the research behind renaming/reworking the
old `is_close`; work record in `tasks/archive/.../is-numerically-close-*.md`).

## The problem

Exact `==` is wrong for computed floats — geometric products, rotor sandwiches,
and inverses never land on the exact expected value, they land ~1 ULP away. Every
numerics library ships an "are these close enough?" predicate for this. gacalc's is
`isclose`.

## What the standard libraries do (researched 2026-08-02)

The universal idea: **combine a relative tolerance with an absolute tolerance** —
close if the difference is within `rel_tol` scaled by magnitude, *or* within a small
`abs_tol` (which rescues comparisons near zero, where relative tolerance collapses to
nothing). Common names: `isclose` (Python `math`, NumPy), `allclose` /
`assert_allclose` (NumPy, whole-array), `assertAlmostEqual` (unittest), `approx`
(pytest), `EXPECT_NEAR`/`FLOAT_EQ` (GoogleTest), `WithinRel`/`WithinAbs`/`WithinULP`
(Catch2). Two mainstream spellings differ only in how they combine the two allowances:

- **`math.isclose` (PEP 485)** — **symmetric**, uses `max`:
  `abs(a-b) <= max(rel_tol * max(|a|,|b|), abs_tol)`.
  Defaults `rel_tol=1e-9`, `abs_tol=0.0`. `isclose(a,b) == isclose(b,a)`.
- **`numpy.isclose`** — **asymmetric**, uses `sum`, treats the **second** arg as the
  reference: `abs(a-b) <= atol + rtol*|b|`. Defaults `rtol=1e-5`, `atol=1e-8`.

(A stricter third school — **ULP** comparison, counting representable floats between
the two — is used by GoogleTest/Boost. More rigorous, less common for a library-level
"close" check; rel+abs is the mainstream, and it's what we use.)

Both mainstream forms warn that **`abs_tol` defaults are dangerous near zero**: NumPy
notes its `1e-8` atol is too tight for values ≪ 1; PEP 485 defaults `abs_tol=0.0` *on
purpose* and tells callers to set it explicitly for zero comparisons, to avoid
"spurious passing tests."

## gacalc's choice — and why

`MultiVectorBase.isclose(self, other, rel_tol=0.0, abs_tol=0.0)`
compares **blade by blade** over the union of present blades (an absent blade counts
as `0`), each pair via **`math.isclose`** (the symmetric PEP-485 form). Aggregated
with `all(...)`, this is exactly "`numpy.allclose` but symmetric."

- **Symmetric (`math.isclose`), not `numpy.isclose`** — an equality-ish predicate
  should be order-independent; `a.isclose(b)` must equal
  `b.isclose(a)`. NumPy's asymmetry (b-as-reference) is a wart we don't
  want in a `==`-adjacent method. (This replaced the original `np.isclose`-per-blade
  implementation.)
- **Per-blade `math.isclose`, not a hand-rolled max formula** — the stdlib function
  *is* the symmetric formula, self-documenting and impossible to get subtly wrong; it
  also drops NumPy from this path (`np` is no longer imported by the generated
  modules).
- **Both tolerances default to `0.0`**, and **all ~72 in-tree callers pass
  `rel_tol=1e-5, abs_tol=1e-5`** explicitly. Rationale (Bill): the defaults should be
  the honest ones — no silent tolerance at all, so a bare `a.isclose(b)` is *exact*
  equality — and each call site declares the tolerance it actually relies on. GA
  results are full of exact/near-zero blades (a rotated basis vector's off-axis parts,
  `scalar·vector = 0`, cancelling products), so those comparisons genuinely need
  `abs_tol`; now that (and the `1e-5` relative level that used to be the hidden
  default) is visible at the call site. `1e-5` is looser than `math.isclose`'s stdlib
  defaults, chosen to absorb the float error the geometric operations accumulate.
- **Floating-point only — symbolic coefficients raise.** gacalc runs symbolically too,
  but "approximately equal" is meaningless for a free symbol. A coefficient carrying
  free symbols raises a clear `TypeError` (via the `_require_float` helper in
  `base.py`) that names the value and points to `==`, instead of the opaque
  `TypeError` a bare `float(expr)` used to throw. Pure-*number* sympy (`Rational`,
  `sqrt(4)→2`) is float-able and passes through. **Use `==` for exact/symbolic
  equality.**

## Where it lives (keep consistent)

Defined on `MultiVectorBase` (`base.py`, the reference) and **overridden in the
generated classes** (`tools/gen_specialized.py`: `is_close_method` for the full
class + graded types, and a hand-built one in `generate_scalar`) with a field-wise
`math.isclose` fast path that defers to `super()` for a foreign type. A change to the
predicate touches **all three** sites plus the shared `_require_float` helper. Guarded
by `tests/test_isclose.py` (symmetry, near-zero opt-in, symbolic raise,
Gn-vs-specialized agreement).
