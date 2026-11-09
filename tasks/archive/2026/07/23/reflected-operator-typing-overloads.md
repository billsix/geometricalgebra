# Investigate why `__radd__`/`__rmul__`/`__rsub__` lack `@typing.overload`s (static + generated)

**Completed:** 2026-07-23 (investigation; no code change warranted)

## Question

The forward operators (`__mul__`/`__add__`/`__sub__`, `__xor__`, the products) carry per-rhs
`@typing.overload`s; the reflected `__radd__` / `__rmul__` / `__rsub__` did not, in either the
hand-built `Scalar` (`generate_scalar`) or the generated graded types, where `generate_graded_type`
types `__radd__`/`__rsub__` with a single direct annotation (`radd_ann`). The generator's comment
reasoned that the reflected op's left operand is always a bare number, because a multivector left
operand handles the op via its own forward method. The task was to confirm or refute that, testing
the cross-representation case (e.g. a bare `Gn` on the left of a `Vector2`).

## Conclusion: no overloads needed

**The premise holds**, verified by tracing: `__rmul__`/`__radd__`/`__rsub__` fire only with a number
on the left. Every gacalc multivector-on-the-left is handled by that operand's own forward op, which
never returns `NotImplemented`, so a multivector never reaches the reflected op. For the number-left
case the single-signature typing was already correct and precise: `2 * v → Vector2`,
`2.0 * i2 → Bivector2`, `2 + i2 → Rotor2`, `2 - v → G2`, `2 * Scalar2 → Scalar2` (10 `assert_type`s
pass). The same applies to the hand-built `Scalar` reflected ops and the generated graded ones.

**The one imprecision is a `sympy.Expr` on the left** (`t * v` → `Unknown` under `ty`), and it is a
sympy operator-stub limitation, not a gacalc gap: `sympy.Expr.__mul__(Vector2)` "handles" the op in
the checker's view (returns `Unknown`), so the checker never consults gacalc's `__rmul__`, and
overloading the reflected ops could not fix it. At runtime sympy returns `NotImplemented`, so
`__rmul__` fires and the result is correct (`Vector2`, confirmed).

## Deliverable

`tests/test_operator_typing.py` gained `test_reflected_operators_are_precise_for_numbers` (static
`int`/`float` precision) and `test_reflected_operators_runtime_including_symbolic_left` (runtime
correctness incl. the symbolic case). The finding was harvested to
`tasks/reference/generated-product-typing.md`. No generator change; only the test file changed.
Gates: ruff/ty src+tests+tools clean; full suite 301 pass.

## Related

- `tasks/reference/generated-product-typing.md` (the forward-operator overload design + the
  `__radd__`/`__rsub__` direct-typing note).
- Sibling: `tasks/archive/2026/07/23/scalar-product-typing-overloads.md` (the `ScalarN`
  forward-product overloads).
