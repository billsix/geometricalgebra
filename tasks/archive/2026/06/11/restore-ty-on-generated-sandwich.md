# Restore strict ty on the generated sandwich (remove the scoped override)

**Created:** 2026-06-08 · **Completed:** 2026-06-11

## What it was

The generated rotor sandwich (`Rotor{n}.sandwich` in `g2.py`/`g3.py`, from
`tasks/archive/2026/06/08/derived-sandwich-operation.md`) had shipped with a narrow `ty.toml`
`[[overrides]]` disabling `unsupported-operator` and `invalid-method-override` for those two files. That
was a carve-out from "ty clean, keep it so", so this task made the generated code pass `ty` on its own.

## Outcome

**The `ty.toml` override was deleted; `ty check src tests` was fully clean, every rule on every file.**
207 tests passed, ruff was clean, and the regenerated output was byte-identical run to run.

1. **`unsupported-operator` was fixed by the coefficient type.** ty turns `numbers.Real` arithmetic
   into `_ComplexLike` and rejects `+`/`/`/`**` on it (the generated bilinear products passed only by
   some whole-module quirk; a standalone probe of their shape also failed). The `numbers.Real` ABC was
   replaced with a concrete alias **`Coef = int | float | sympy.Expr`** in `base.py` (`BladeCoef` became
   `dict[..., Coef]`), verified by probe before committing to it. It was threaded through `base.py`
   (every scalar-returning method: `scalar_part`, `scalar_product`, `component`, `magnitude`,
   `magnitude_squared`, `cosine`), `gn.py`, `nbplotutils.py` and the generator (field annotations, and
   `cast_real` → `cast_coef`, which skips the cast for bare or negated fields already of type `Coef`, so
   no `redundant-cast` warnings). Several hand-written casts in `base.py` (`inverse`, `cosine`,
   `from_*`) were dropped.
   - The maintainer asked for `magnitude_squared` to be widened to `Coef`, and it was. The concrete
     union was required over `numbers.Real | sympy.Expr`: the latter keeps the `numbers.Real` arm, and
     the generated arithmetic still failed (probe-confirmed).
2. **`invalid-method-override` was fixed by typing `sandwich` as its operand.** The generated
   `def sandwich(self, rhs) -> typing.Self` mismatched base's `sandwich(self, x: _OperandT) ->
   _OperandT` on the parameter name (Liskov keyword argument) and mistyped the result — a rotor's
   sandwich of a vector is a vector, so the old `cast(Self, …)` was wrong. `dispatch_method` gained
   `param_name` / `return_type` / `cast` parameters; the sandwich passes `x` / `_OperandT` /
   `cast_operand`, so it is a Liskov-compatible override typed as the operand. `_OperandT` is imported
   into the generated `g2.py`/`g3.py` headers (conditionally, n ≥ 2).

Also weighed: waiting for a newer ty to improve the numeric tower, and a generate → ty → inject
post-pass adding `# ty: ignore[...]` + `# noqa: E501` on the reported lines. The latter was rejected
again, since it couples deterministic generation to ty/ruff diagnostics.

## Side finding

`test_rotor_sandwich_equals_rotate_symbolic_2d` caught it: the maintainer's idea to compute the rotor
scalar as `product.magnitude()` is mathematically equal to `|from| * |to|`, but sympy renders it as the
nested radical `sqrt((a·b)² + (a∧b)²)` and cannot simplify it through the sandwich, breaking the
symbolic `R v R⁻¹ == rotate` identity. The two-magnitude form `from.magnitude() * to.magnitude()` was
kept, and thanks to the `Coef` widening it no longer needed its `typing.cast(sympy.Expr, …)`.

## Files

`base.py`, `gn.py`, `nbplotutils.py`, `tests/test_multivector.py` (a now-unused `# type: ignore`
dropped), `tools/gen_specialized.py`, `tools/astbuild.py`; `ty.toml` deleted; CLAUDE.md refreshed (Dev
workflow, and a new "Coefficient type" note under Architecture).
