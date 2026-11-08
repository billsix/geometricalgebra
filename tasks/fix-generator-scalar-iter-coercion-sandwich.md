# Fix three generator bugs: `Scalar.__iter__`, full `G` with a graded operand, inexact `sandwich`

**Status:** proposed — needs go-ahead (approved in session 2026-11-08; in progress)
**Priority:** 2
**Difficulty:** 5
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §5.1

## BLUF

Three bugs in `tools/gen_specialized.py` show up in every generated `g1`–`g3`. They are fixed
together, because they share one regenerate-and-test pass.

1. `Scalar.__iter__` yields the `Scalar` itself (and nothing when it is zero), instead of its
   coefficient.
2. The full class `G` sends a graded operand of its own algebra (`G * Vector`, `G + Vector`) to the
   slow `Gn` reference.
3. The closed-form `Versor.sandwich` turns integer input into floats.

Done means: each bug has a regression test that fails on the old generator, the suite is green, and
the generator is still deterministic.

## Context

The three bugs, as re-checked 2026-11-08 (`g2`):

```
>>> list(Scalar.from_real(3)), list(Scalar.from_real(0))
([g2.Scalar(coeff_scalar=3)], [])
>>> type(G.e_1 * Vector.e_1).__name__, type(G.e_1 + Vector.e_1).__name__
('Gn', 'Gn')
>>> (1 + 1*Versor.e_12).sandwich(1*e_1)
g2.Vector(coeff_e_1=0.0, coeff_e_2=-1.0)
```

1. **`Scalar.__iter__`.** The scalar class's `__iter__` was hand-built (`if coeff != 0: yield
   Scalar(...)`). It breaks `CLAUDE.md`'s rule that iteration yields coefficient values in blade
   order, and its own docstring ("Yields: Real"). Every other type uses `iter_method(blades)`.
2. **Full `G` with a graded operand.**
   - The full-class `bilinear` emitter (products) and the `linear` emitter (`__add__`/`__sub__`)
     guard with `if not isinstance(rhs, G): <Gn fallback>`. So a graded `Vector`/`Bivector`/…
     of the same algebra took the `Gn` path, and `cast(Self, …)` hid the type mismatch.
   - The reverse order (`Vector * G`) already widened to `G` through `_coerce`.
   - The `Gn` fallback must stay for `Gn` and other algebras;
     `tests/test_conformance.py::test_mixing_with_gn_coerces_to_gn` pins that.
3. **`sandwich` exactness.**
   - sympy's CSE gives the reciprocal `Pow(|R|², −1)`, which `sympy.sstr` writes as `1/(x0 + x1)`,
     and Python evaluates that as float division.
   - `CLAUDE.md` says int input goes through sympy for exactness, as `MultiVectorBase.inverse`
     does.
   - A survey of every `ast.Div` in the generated g1–g3 found that the only `1/expr` divisions are
     these CSE reciprocals: 1 in g2 and 4 in g3, all in `sandwich` bodies. The other division,
     `t * math.pi / 2`, is a float angle on purpose.

Read first: `CLAUDE.md` › "Code generation" (generate, read the real output, then change the
generator) and `tasks/reference/code-generator-architecture.md`.

## Plan

- [ ] Bug 1: emit the scalar's `__iter__` with `iter_method([()])`.
- [ ] Bug 2: add a `widen_same_algebra_rhs` statement (`if isinstance(rhs, (Scalar, Vector, …)): rhs =
  G.from_blade_dict(rhs.to_blade_dict())`) ahead of the `Gn` guard in `bilinear` and `linear`.
- [ ] Bug 3: add `gacalc.base._reciprocal` (int → exact `Rational`, raising `ZeroDivisionError` on
  integer 0; float and symbolic as they are, with doctests). Make `expr_to_ast` rewrite every `1 / x`
  to `_reciprocal(x)` (`ReciprocalToCall`), and add it to the generated imports.
- [ ] One regression test per bug, each confirmed to fail on the old generator.
- [ ] Gates:
  - `pytest -m "not slow"`;
  - determinism (regenerate twice, `cmp`);
  - `tools/check_doc_regions.py`;
  - `ty` on the generated modules (no new diagnostics);
  - `ruff`.
- [ ] `CHANGELOG.md` `[Unreleased]` › Fixed entries (consumer-visible behaviour).

## Open questions

None.
