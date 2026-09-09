# gacalc — symbolic equality (`simplify(a − b) == 0`)

**Reference document** — how gacalc decides whether two multivectors are *symbolically* equal, its
limits, and where the logic lives. The **symbolic sibling** of `tasks/reference/approximate-float-equality.md`
(which covers the *numeric* `isclose`). Not a task; update in place. Created 2026-08-27
(William Emerison Six <billsix@gmail.com>) from a direct read of the generator + base class + tests
(all `file:line` verified).

## Two equality notions — don't confuse them

- **Symbolic** (this doc): `==` / `simplify(a − b) == 0`. Exact equality of symbolic coefficients, for
  values built from `sympy` symbols. Ground truth, but heuristic and slow (see Limits).
- **Numeric:** `MultiVectorBase.isclose` (`src/gacalc/base.py:1207`) — ULP/absolute-tolerance float
  comparison, for concrete float coefficients. Documented separately in `approximate-float-equality.md`.

Use symbolic `==` for symbolic values; `isclose` for floats.

## How `==` is defined — the generated `__eq__`

The specialized/graded classes (`g1`/`g2`/`g3`, generated build artifacts) get a **generated
`__eq__`**, emitted as AST nodes by `tools/gen_specialized.py` (`eq_method`). Per coefficient field
it emits a call to one shared, hand-written predicate:

```
_coef_eq(self.<field>, other.<field>)
```

**`base._coef_eq` (`src/gacalc/base.py`) is where the rule lives** — the generator emits only the
call, at both of its comparison sites (the same-type field path and the cross-type blade-dict
fallback), so there is a single implementation rather than two hunks of equivalent AST. Three
steps, in order:

- a **structural fast path** — plain Python `==` — which short-circuits to `True`;
- a **numeric short-circuit**: if *neither* side is a `sympy.Basic`, return `False` immediately.
  `simplify` can never turn two unequal numbers into equal ones, so once `==` has said no, the
  answer for plain numbers is already known and the symbolic step can only burn time (2026-09-09;
  before this, a *differing* numeric comparison cost 48 µs — see Cost below);
- the **symbolic check** — `sympy.simplify(sympy.sympify(l) - sympy.sympify(r)) == 0` — reached only
  when at least one coefficient is symbolic.

**Why the simplify is needed (not just `==`):** the specialized/graded classes follow a **lazy
policy — they do NOT eager-simplify** coefficients (`base.py:393`; `.simplified()` at `base.py:391`
is the opt-in that simplifies every coefficient). So two genuinely-equal multivectors can hold
coefficients in *different forms* — `2*x` vs `x + x`, or unreduced `sqrt` expressions (`base.py:1256`
notes a raw coefficient "may not be in lowest terms"). A bare `==` would report those unequal; the
`simplify(a − b) == 0` check is what makes equality correct.

## Limits — what `simplify(a − b) == 0` can and can't do

- **No false positives:** if `simplify` reduces the difference to `0`, the values *are* equal.
- **Possible false negatives:** `sympy.simplify` is a **heuristic**, not a decision procedure — it can
  fail to prove that a genuinely-zero difference is zero (e.g. a nested radical it "cannot simplify
  through," called out at `base.py:1061`). So `==` can under-report equality on hard symbolic forms.
- **Cost:** `simplify` is expensive, and it is the reason both fast paths above exist. Measured
  2026-09-06 from a modelviewprojection profile (gacalc 0.0.19, Python 3.14): a *differing* numeric
  comparison, `g2.Vector(3.0, 4.0) == g2.Vector(1.5, -2.0)`, cost **48 µs** against 0.018 µs for the
  equivalent tuple comparison, and was 71 ms of a 173 ms game profile over 1189 calls. The numeric
  short-circuit brought that to **~0.4 µs** (~123×) with no change in results. The lesson worth
  keeping: a structural fast path guarded only on *equality* still leaves the *inequality* case
  paying full symbolic price, which is the case a game actually hits every frame.

## Test helpers that reuse the pattern (currently duplicated)

Tests compare multivectors **blade-dict-wise** with the same idiom, each rolled by hand:
- `tests/test_conformance.py:401` `_same_value(x, y)` — per-blade
  `simplify(sympify(dx[k]) − sympify(dy[k])) == 0` over `to_blade_dict()` (`:408`).
- `tests/test_graded.py:381` `simplify_equal(a, b)` — same (`:392`), used where magnitudes are `sqrt(...)`
  (`:419`), e.g. `test_rotor_sandwich_equals_rotate_*`.
- Inline one-offs: `tests/test_conformance.py:87`, `tests/test_measure.py:139-140`.

There is **no public `MultiVectorBase.symbolically_equal` method** — the `simplify(a−b)==0` logic is
re-implemented ad hoc in each test helper. That duplication is the actionable gap (see follow-on).

**What changed 2026-09-09:** the per-*coefficient* half of that logic is no longer duplicated — it is
`base._coef_eq`, one hand-written function the generated `__eq__` calls from both of its paths. The
test helpers above still roll their own, and they compare whole multivectors blade-dict-wise rather
than coefficient-wise, so the gap is unchanged in substance; but a consolidated public predicate now
has an obvious implementation to delegate to (`_coef_eq` per blade over the key union) instead of
re-deriving the rule. That is a fact for the follow-on task to use, not a decision it forecloses.

## Follow-on

`tasks/consolidate-symbolic-equality-predicate.md` — consolidate `_same_value`/`simplify_equal` into a
single public predicate and expand the symbolic tests. (Blocked on a small API decision — see that task.)

## Cross-links

- `tasks/reference/approximate-float-equality.md` — the numeric `isclose` sibling.
- `tasks/reference/code-generator-architecture.md` — how `tools/gen_specialized.py` emits classes
  (the `__eq__` here is one of its generated methods).
