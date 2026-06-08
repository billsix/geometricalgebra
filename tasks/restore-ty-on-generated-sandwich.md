# Restore strict ty on the generated sandwich (remove the scoped override)

Status: **investigation — not started** · proposed 2026-06-08

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
