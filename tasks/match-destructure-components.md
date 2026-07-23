# Investigate destructuring rhs components in the `match`-on-type dispatch (static + generated)

**Status:** proposed — needs go-ahead. Created 2026-07-23 (Bill).

## Goal

Every method that dispatches on the rhs with a `match` — the geometric product, `inner_product`,
`outer_product`, and the other bilinear ops — currently matches **on the type only**, then reads the
rhs's coefficient fields by attribute in the arm body:

```python
match rhs:
    case Vector2():
        return Rotor2(coeff_scalar=self.coeff_e_1 * rhs.coeff_e_1 + self.coeff_e_2 * rhs.coeff_e_2,
                      coeff_e_12=self.coeff_e_1 * rhs.coeff_e_2 - self.coeff_e_2 * rhs.coeff_e_1)
```

(The generator builds these via `dispatch_method` / `_match_class`, which emits a **class pattern with
no sub-patterns** — `tools/gen_specialized.py:1012-1016`, `:1075`.) Investigate rewriting them to
**destructure the rhs's components in the match pattern**, binding each coeff field to a fresh local:

```python
match rhs:
    case Vector2(coeff_e_1=b1, coeff_e_2=b2):
        return Rotor2(coeff_scalar=self.coeff_e_1 * b1 + self.coeff_e_2 * b2,
                      coeff_e_12=self.coeff_e_1 * b2 - self.coeff_e_2 * b1)
```

so the arm reads in terms of `b1`/`b2` instead of `rhs.coeff_e_1`/`rhs.coeff_e_2`.

## Scope

**Both** kinds:
- the **generated** classes (`g1`/`g2`/`g3`) — `dispatch_method` and the inline `__mul__`/`__xor__`
  and `_geometric_product`; and
- the **statically/hand-built** code — the hand-built `Scalar` `match`/`isinstance` arms in
  `generate_scalar`, and `Gn._geometric_product`'s `decrease_grade` `match` in `gn.py` (already a
  structural `match`, but on blade tuples, not components — assess if it's in scope).

## Investigate

1. **Feasibility:** keyword patterns (`case Vector2(coeff_e_1=b1, …)`) work on any attribute (they
   don't need `__match_args__`), so binding the `coeff_*` fields is possible on the `slots=True`
   dataclasses. Confirm with a spike.
2. **Naming:** the generator already has a rename map (`a_e_1 -> self.coeff_e_1`, `b_e_1 -> rhs.…`);
   destructuring would bind the `b_*` names as locals in the pattern instead of rewriting to
   attribute access — potentially *simplifying* `expr_to_ast`/`SymbolToAttr` (the symbols map straight
   to the bound locals). Assess whether the emitted code gets simpler or just different.
3. **Readability / checker:** does the destructured form read better, and does `ty` narrow the same?
4. **Cost:** any perf difference (binding N locals vs N attribute reads — negligible, but confirm).

## Verify

Regenerate; byte-diff review; `ty`/ruff/suite/regions/**determinism** green; runtime unchanged
(the products are value-identical).

## Relationships

- `tasks/reference/generated-product-typing.md` and `tasks/reference/code-generator-architecture.md`
  (the dispatch/emission machinery).
- CLAUDE.md "Prefer `match` + `case _`" / "Use modern Python" (the idiom this leans into).
