# Investigate why `__radd__`/`__rmul__`/`__rsub__` lack `@typing.overload`s (static + generated)

**Status:** complete (investigation — no code change warranted)
**Completed:** 2026-07-23

## Conclusion: no overloads needed

The "left operand is always a bare number" premise **holds** (verified by tracing: `__rmul__`/
`__radd__`/`__rsub__` fire only with a number left — every gacalc multivector-on-the-left is handled
by that operand's own forward op, which never returns `NotImplemented`, so a multivector never reaches
the reflected op). For that sole number-left case the current single-signature typing is **already
correct and precise** — `2 * v → Vector2`, `2.0 * i2 → Bivector2`, `2 + i2 → Rotor2`, `2 - v → G2`,
`2 * Scalar2 → Scalar2` (10 `assert_type`s pass). This is the task's outcome (2): **document, no code
change.**

The **one imprecision** is a `sympy.Expr` on the left (`t * v` → `Unknown` under `ty`), and it is a
**sympy operator-stub limitation, not a gacalc gap**: `sympy.Expr.__mul__(Vector2)` "handles" the op
in the checker's view (returns `Unknown`), so the checker never consults gacalc's `__rmul__` — meaning
**overloading the reflected ops could not fix it**. At runtime sympy returns `NotImplemented`, so
`__rmul__` fires and the result is correct (`Vector2`, confirmed).

Applies identically to the hand-built `Scalar` reflected ops and the generated graded ones.

**Deliverable:** `tests/test_operator_typing.py` gains
`test_reflected_operators_are_precise_for_numbers` (static `int`/`float` precision) and
`test_reflected_operators_runtime_including_symbolic_left` (runtime correctness incl. the symbolic
case). Finding harvested to `tasks/reference/generated-product-typing.md`. No generator change —
`git status` shows only the test file. Gates: ruff/ty src+tests+tools clean; full suite 301 pass.

## Original task


## Goal

The forward operators (`__mul__`/`__add__`/`__sub__`, `__xor__`, the products) carry per-rhs
`@typing.overload` signatures so a known-type call types precisely. The **reflected** operators
`__radd__` / `__rmul__` / `__rsub__` do **not** — in both the hand-built `Scalar`
(`generate_scalar`, `tools/gen_specialized.py:1323` `__rmul__`, `:1444` `__radd__`, `:1464`
`__rsub__`) and the generated graded types. Determine *why*, and what it would take to give them
overloads if there's a case they currently mistype.

## Current reasoning (starting point — confirm or refute)

`generate_graded_type` types `__radd__`/`__rsub__` with a **single direct return annotation**
(`radd_ann`, `tools/gen_specialized.py:1995`), not overloads. The comment (`:1989`) says: the reflected
op's **left operand is always a bare number** — Python only calls `x.__radd__(self)` when the left
operand `x` doesn't handle `self`, and a *multivector* left operand handles it via its own `__add__`.
So the only real signature is `number OP self → <resolved self±scalar type>`, i.e. one case — no
per-type overload needed. `__rmul__` likewise (`number * self → self's type`, scaling).

## Investigate

1. **Is the "left is always a number" premise actually true** for these types? Trace when
   `__rmul__`/`__radd__` fire: for `x * self` where `x` is `int`/`float`/`sympy.Expr` → yes. For `x`
   a *different* multivector representation (e.g. a bare `Gn` on the left of a `Vector2`) — does
   `Gn.__mul__(Vector2)` return `NotImplemented`, falling back to `Vector2.__rmul__(Gn)`? If so, the
   reflected op DOES see a multivector left operand and its single-signature typing is **imprecise**
   (or wrong). Test this cross-representation case.
2. **If the premise holds** (reflected ops only ever see scalars): the current single-signature typing
   is already correct/precise → the answer is "they don't need overloads," and this task documents
   that (with a test). No code change.
3. **If it doesn't hold:** determine the overload set needed (a number overload + a `MultiVectorBase`
   overload, or per-rhs like the forward ops) and what plumbing `generate_graded_type` /
   `generate_scalar` need to emit them — plus whether the runtime `__rmul__`/`__radd__` bodies handle
   the multivector-left case at all.
4. Apply the same analysis to the **`Scalar`** hand-built reflected ops.

## Verify

`ty` src/tests/tools clean; add `assert_type` guards for the reflected ops (whatever the correct types
are) to `tests/test_operator_typing.py`; suite/regions/determinism green.

## Relationships

- `tasks/reference/generated-product-typing.md` (the forward-operator overload design + the
  `__radd__`/`__rsub__` direct-typing note).
- Sibling: `tasks/scalar-product-typing-overloads.md` (the `ScalarN` forward-product overloads).
