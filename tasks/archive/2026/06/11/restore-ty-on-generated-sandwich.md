# Restore strict ty on the generated sandwich (remove the scoped override)

Status: **COMPLETE 2026-06-11** · proposed 2026-06-08

> **Done (2026-06-11). The `ty.toml` override is DELETED; `ty check src tests` is fully clean,
> every rule on every file.** 207 tests pass, ruff clean, regen byte-identical.
>
> Both false positives traced to one root cause and one signature mismatch:
>
> 1. **`unsupported-operator` → fixed by the coefficient type.** Replaced the `numbers.Real` ABC with
>    a concrete alias **`Coef = int | float | sympy.Expr`** (in `base.py`; `BladeCoef` now
>    `dict[..., Coef]`). ty turns `numbers.Real` arithmetic into `_ComplexLike` and rejects `+`/`/`/`**`
>    on it — the concrete union types cleanly (verified by probe before committing to it). Threaded
>    through `base.py` (all scalar-returning methods: `scalar_part`/`scalar_product`/`component`/
>    `magnitude`/`magnitude_squared`/`cosine`), `gn.py`, `nbplotutils.py`, and the generator (field
>    annotations + `cast_real`→**`cast_coef`**, which now also *skips* the cast for bare/negated fields
>    that are already `Coef`, so no `redundant-cast` warnings). The widening also let several
>    hand-written casts in `base.py` (`inverse`, `cosine`, `from_*`) drop entirely.
>    - Bill's note re `magnitude_squared`: signature widened as asked (to `Coef`). The concrete
>      `int | float | sympy.Expr` was required over `numbers.Real | sympy.Expr` — the latter keeps the
>      poisonous `numbers.Real` arm, so the generated arithmetic still failed (probe-confirmed).
> 2. **`invalid-method-override` → fixed by typing `sandwich` as the operand.** The generator emitted
>    `def sandwich(self, rhs) -> typing.Self`, which mismatched base's `sandwich(self, x: _OperandT) ->
>    _OperandT` on the param name (Liskov keyword arg) *and* mistyped the result (a rotor's sandwich of
>    a vector is a vector, not the rotor — the old `cast(Self, …)` was a lie). `dispatch_method` now
>    takes `param_name`/`return_type`/`cast`; the sandwich passes `x` / `_OperandT` / `cast_operand`, so
>    it is a Liskov-compatible override **and** genuinely typed as the operand. `_OperandT` imported
>    into the generated `g2.py`/`g3.py` headers (conditionally, n≥2).
>
> **Side finding (caught by `test_rotor_sandwich_equals_rotate_symbolic_2d`):** Bill's idea to compute
> the rotor scalar as `product.magnitude()` is mathematically identical to `|from||to|` but sympy
> renders it as the nested radical `sqrt((a·b)² + (a∧b)²)` and **cannot `simplify` it through the
> sandwich**, breaking the symbolic `R v R⁻¹ == rotate` identity. Kept the two-magnitude form
> `from.magnitude() * to.magnitude()` (two simple sqrts) — which, thanks to the `Coef` widening, no
> longer needs its old `typing.cast(sympy.Expr, …)` either. So `rotor_from_vectors` got cleaner without
> changing the symbolic form the tests rely on.
>
> Files: `base.py`, `gn.py`, `nbplotutils.py`, `tests/test_multivector.py` (dropped a now-unused
> `# type: ignore`), `tools/gen_specialized.py`, `tools/astbuild.py`; `ty.toml` deleted; CLAUDE.md
> refreshed (Dev workflow + a new "Coefficient type" note under Architecture). Generated `g*.py`
> regenerated (gitignored).

---
_Original investigation plan below._

## Goal

Make the generated rotor-sandwich code (`Rotor{n}.sandwich`, in `g2.py`/`g3.py`)
pass `ty` **on its own**, so the `ty.toml` `[[overrides]]` that currently disables
`unsupported-operator` + `invalid-method-override` for those files can be
**removed** and gacalc is fully strict again everywhere.

Context: `tasks/archive/2026/06/08/derived-sandwich-operation.md` (the
implementation). The override is narrow (two rules, two files, all else strict)
but it *is* a carve-out from "ty clean, keep it so."

## The two false positives to resolve

1. **`unsupported-operator`** on the sandwich coefficients. `numbers.Real`
   arithmetic — division by `|R|²`, quadratic `self.coeff * self.coeff` sums —
   types as `_ComplexLike`, and ty then rejects `+` / `/` on it. **The mystery:**
   the generated *bilinear products* use the same `self.coeff * rhs.coeff + ...`
   shape and **pass** ty, while the sandwich's longer / `self*self` / rational
   expressions **fail**. A standalone probe of the product shape *also* failed,
   so it's some whole-module / expression-complexity behavior I couldn't pin
   down. Understanding *why the products pass* is the key that likely unlocks a
   fix for the sandwich.
2. **`invalid-method-override`** — the generated `sandwich(self, rhs) ->
   typing.Self` (the generator's blanket return convention) is an incompatible
   override of `base.AbstractMultiVector.sandwich(self, x: _OperandT) ->
   _OperandT`. The sandwich genuinely returns the *operand's* type, not `Self`.

## Avenues to investigate

- **Coefficient field type.** Fields are `numbers.Real`. Would `int | float |
  sympy.Expr` (or a dedicated `Coef` alias) make ty's `* / **` / division clean
  (sympy.Expr supports them; int/float do too)? Big but principled change — it
  would also fix the products' latent imprecision. Check it doesn't regress the
  rest of the generated code or `base.py`.
- **Why do the products pass but the sandwich doesn't?** Reduce to the minimal
  failing/passing pair *inside the real module* (not a standalone probe) and diff.
  Expression length? `self*self` vs `self*rhs`? Division? cse temps? This is the
  crux.
- **Generated `sandwich` return type.** Emit it returning the operand type (an
  `_OperandT`-style TypeVar in the generated module + cast to it per case)
  instead of `typing.Self`, so it's a *compatible* override of `base.sandwich` —
  removing the `invalid-method-override` need. (Requires parametrizing
  `dispatch_method`'s return + the per-case cast, which currently hardcode
  `typing.Self`.)
- **ty version.** Re-check on newer ty; the `numbers.Real` numeric-tower
  behavior may improve upstream, making the override unnecessary for free.
- **Inline suppression (last resort).** A generate→ty→inject post-pass that adds
  `# ty: ignore[...]` + `# noqa: E501` on exactly the reported lines. Considered
  and rejected during the implementation (couples deterministic generation to
  ty/ruff diagnostics); only revisit if the type-system avenues fail.

## Definition of done

`ty check src tests` clean with **no `ty.toml` override** (delete the file or the
`[[overrides]]` block), generated suite + `make check-generated` still green.
