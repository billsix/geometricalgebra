# Investigate destructuring rhs components in the `match`-on-type dispatch (static + generated)

**Completed:** 2026-07-23 (investigated; declined by William Emerison Six <billsix@gmail.com>,
2026-07-23). No code change.

## Question

Every method that dispatches on the rhs with a `match` (the geometric product, `inner_product`,
`outer_product`, the other bilinear ops) matched **on the type only** (`case Vector2():`, a class
pattern with no sub-patterns emitted by `dispatch_method` / `_match_class` in
`tools/gen_specialized.py`), then read the rhs's coefficient fields by attribute
(`self.coeff_e_1 * rhs.coeff_e_1`). The proposal was to destructure in the pattern
(`case Vector2(coeff_e_1=b1, coeff_e_2=b2):`) so the arm reads in terms of bound locals, across the
generated classes and the hand-built code (`generate_scalar`'s arms, `Gn._geometric_product`'s
`decrease_grade`).

## Finding: feasible

Keyword patterns (`case Vector2(coeff_e_1=b_e_1, …)`) bind any attribute without
`__match_args__`, so they work on the frozen+slots dataclasses. The generator change would have
been: `_match_class` emits `kwd_attrs`/`kwd_patterns` binding each rhs field to its symbol name, and
the per-arm `rename_map` maps `b_e_1 → bare local` instead of `("rhs", "coeff_e_1")`.

## Decision: declined (net-neutral-to-negative lateral rewrite)

1. **It breaks the symmetric reading.** `self.coeff_e_1 * rhs.coeff_e_1` (both operands read the
   same way) becomes the asymmetric `self.coeff_e_1 * b_e_1`.
2. **Same formula, two spellings.** The same-type early-out (`if type(rhs) is Vector2:`) is an `if`,
   not a `match` case, so it cannot destructure; the identical same-type product would appear once
   with `rhs.coeff_e_1` and once with `b_e_1` in every product method.
3. **No generator simplification.** `a_*` (self) symbols can't be pattern-bound (self isn't the
   match subject), so `SymbolToAttr`/`expr_to_ast`/`rename_map` all stay; only `b_*` would become
   bare names, while `_match_class` gets more complex.
4. **Verbose pattern headers** (up to 4 fields, e.g. `case Rotor3(coeff_scalar=…, coeff_e_12=…,
   coeff_e_13=…, coeff_e_23=…):`) for byte-identical runtime.

**Out of scope, as suspected:** `Gn._geometric_product`'s `decrease_grade` matches on **blade
tuples**, already idiomatic structural list-patterns, not component destructuring. The hand-built
`Scalar` arms had become `dispatch_method`-generated (since the scalar-product task), so no separate
static work existed. CLAUDE.md's `match` guidance counts type dispatch as legitimate, so
`case Vector2():` is fine by the house standard.

The decision was recorded in `tasks/reference/design-decisions.md` so it isn't re-proposed.

## Related

- `tasks/reference/generated-product-typing.md`, `tasks/reference/code-generator-architecture.md`
  (the dispatch/emission machinery).
