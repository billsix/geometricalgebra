# Investigate destructuring rhs components in the `match`-on-type dispatch (static + generated)

**Status:** investigated — **declined** (Bill, 2026-07-23). Feasible, but a net-neutral-to-negative
lateral rewrite; leave the dispatch matching on type only.

## Investigation & decision

**Feasible:** keyword patterns (`case Vector2(coeff_e_1=b_e_1, …)`) bind any attribute without
`__match_args__`, so they work on the frozen+slots dataclasses. The generator change would be:
`_match_class` emits `kwd_attrs`/`kwd_patterns` binding each rhs field to its symbol name, and the
per-arm `rename_map` maps `b_e_1 → bare local` instead of `("rhs", "coeff_e_1")`.

**Declined because it doesn't improve anything and regresses a few things:**
1. **Breaks the symmetric reading.** `self.coeff_e_1 * rhs.coeff_e_1` (both operands read the same
   way) becomes the asymmetric `self.coeff_e_1 * b_e_1`.
2. **Same formula, two spellings.** The `#1` same-type early-out (`if type(rhs) is Vector2:`) is an
   `if`, not a `match` case, so it **cannot** destructure — the identical same-type product would then
   appear once with `rhs.coeff_e_1` (early-out) and once with `b_e_1` (case arm), in every product
   method.
3. **No generator simplification.** `a_*` (self) symbols can't be pattern-bound (self isn't the match
   subject), so `SymbolToAttr`/`expr_to_ast`/`rename_map` all stay; only `b_*` becomes bare names,
   while `_match_class` gets *more* complex. Complexity moves sideways.
4. **Verbose pattern headers** (up to 4 fields, e.g. `case Rotor3(coeff_scalar=…, coeff_e_12=…,
   coeff_e_13=…, coeff_e_23=…):`) for byte-identical runtime.

**Out of scope (as suspected):** `Gn._geometric_product`'s `decrease_grade` matches on **blade
tuples** — already idiomatic *structural* list-patterns, not component destructuring. The hand-built
`Scalar` arms are now `dispatch_method`-generated (since the scalar-product task), so no separate
static work exists. CLAUDE.md's `match` guidance counts **type dispatch** as legitimate use, so the
current `case Vector2():` is fine by the house standard.

Recorded in `tasks/reference/design-decisions.md` so it isn't re-proposed. No code change.

## Original task


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
