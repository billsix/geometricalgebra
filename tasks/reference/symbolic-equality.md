# gacalc — symbolic equality (`simplify(a − b) == 0`)

**Reference document** — how gacalc decides whether two multivectors are *symbolically* equal, its
limits, and where the logic lives. The **symbolic sibling** of `tasks/reference/approximate-float-equality.md`
(which covers the *numeric* `isclose`). Not a task; update in place. Created 2026-08-27
(William Emerison Six <billsix@gmail.com>) from a direct read of the generator + base class + tests
(all `file:line` verified).

## Two equality notions — don't confuse them

- **Symbolic** (this doc): `==` / `simplify(a − b) == 0`. Exact equality of symbolic coefficients, for
  values built from `sympy` symbols. Ground truth, but heuristic and slow (see Limits).
- **Numeric:** `MultiVectorBase.isclose` (`src/gacalc/base.py`) — ULP/absolute-tolerance float
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
policy — they do NOT eager-simplify** coefficients (the module header's eager/lazy note in
`src/gacalc/base.py`; `MultiVectorBase.simplified()` is the opt-in that simplifies every coefficient). So two genuinely-equal multivectors can hold
coefficients in *different forms* — `2*x` vs `x + x`, or unreduced `sqrt` expressions
(`MultiVectorBase._repr_latex_` notes a raw coefficient "may not be in lowest terms"). A bare `==` would report those unequal; the
`simplify(a − b) == 0` check is what makes equality correct.

## Gotcha: a multivector never `==` a bare Python number

`==` compares two multivectors; it does **not** lift a bare Python number. The generated
`__eq__` guards `if not isinstance(other, MultiVectorBase): return NotImplemented` (e.g.
`src/gacalc/g2.py`), and `int`/`float`/`sympy.Expr` have no reflected `__eq__` that would
accept a multivector, so Python falls back to identity and the result is **`False`** —
even when the multivector *is* that number:

```
>>> from gacalc import g2
>>> g2.Scalar.from_real(-1) == -1          # False -- NOT lifted
False
>>> g2.Scalar.from_real(-1) == g2.Scalar.from_real(-1)   # compare typed values
True
```

**This is asymmetric with arithmetic**, which *does* lift a bare number (`__add__`/`__mul__`
route it through `from_blade_dict`/`from_real`), so `scalar + 1` and `bivector * 2` work
fine — only `==` refuses. The footgun: a grade-0 *result* compared to `0`/`1` with `==` is
silently `False` even when it holds that value (`some_scalar_result == 0` misfires).

Practical rule, and the one the generated **doctests** follow: compare a multivector result
to a **correctly-typed** value — `== Scalar.from_real(-1)`, `== Vector.e_3`,
`== Versor.from_real(1)` — never to a bare number. When you want the *number*, pull it out
first (`.scalar_part()`, `.coefficient(blade)`, `.magnitude_squared()` return a plain `Real`)
and compare that: `mv.scalar_part() == 0` is fine, `mv == 0` is not.

## Limits — what `simplify(a − b) == 0` can and can't do

- **No false positives:** if `simplify` reduces the difference to `0`, the values *are* equal.
- **Possible false negatives:** `sympy.simplify` is a **heuristic**, not a decision procedure — it can
  fail to prove that a genuinely-zero difference is zero (e.g. a nested radical it "cannot simplify
  through," called out in `MultiVectorBase.versor_from_vectors`). So `==` can under-report equality on hard symbolic forms.
- **Cost:** `simplify` is expensive, and it is the reason both fast paths above exist. Measured
  2026-09-06 from a modelviewprojection profile (gacalc 0.0.19, Python 3.14): a *differing* numeric
  comparison, `g2.Vector(3.0, 4.0) == g2.Vector(1.5, -2.0)`, cost **48 µs** against 0.018 µs for the
  equivalent tuple comparison, and was 71 ms of a 173 ms game profile over 1189 calls. The numeric
  short-circuit brought that to **~0.4 µs** (~123×) with no change in results. The lesson worth
  keeping: a structural fast path guarded only on *equality* still leaves the *inequality* case
  paying full symbolic price, which is the case a game actually hits every frame.

## The public predicate: `MultiVectorBase.symbolically_equal` (2026-10-05)

The `simplify(a − b) == 0` idiom has one home: `a.symbolically_equal(b, subs=None)` in `src/gacalc/base.py`
(`tasks/archive/2026/10/05/consolidate-symbolic-equality-predicate.md`). Blade-dict-wise over the union of
present blades, so it is representation-agnostic (`Gn` vs `g2`/`g3`); per blade it delegates to `_coef_eq`
(the same rule the generated `__eq__` uses: exact for plain numbers, `simplify`-backed only when a side is
symbolic), and with `subs` it applies the substitution to each blade's *difference* before `simplify` (the
"Square roots" recipe below). It returns a plain `bool` and is **conservative**: `False` means "not proven
equal" (decided 2026-10-05: public method, plain `bool` — no separate "undecided" signal). Tests use it
directly; the former hand-rolled copies (`_same_value` in `test_conformance.py`, `simplify_equal` in
`test_graded.py`, `_simplify_equal` in `test_rotor_from_vectors.py`) are gone. Scalar-level one-offs
(`scalar_eq` in `test_conformance.py`, the `content` assertions in `test_measure.py`) compare `Real`s, not
multivectors, and stay as `simplify(...) == 0`. Pinned by `tests/test_symbolic_equality.py`.

## Square roots: hand sympy the relation it cannot find (Lagrange / Pythagoras) (2026-10-05)

`simplify(a − b) == 0` stalls when the two sides hide the same square root in different shapes.
`versor_from_vectors(a, b).normalize()` divides by `sqrt(|R|²)` with `|R|²` the raw polynomial
`(|a||b| + a·b)² + |a∧b|²`; proving the result is the half-angle rotor `cos(θ/2) − sin(θ/2)·i` needs two
relations sympy does not discover: Lagrange's (<https://en.wikipedia.org/wiki/Lagrange%27s_identity>) `(a·b)² + |a∧b|² = |a|²|b|²` (collapsing `|R|²` to
`2|a||b|(|a||b| + a·b)`) and the half-angle identity. The pattern that works, from
`tests/test_rotor_from_vectors.py`:

- **Parametrize so the relation is a single substitution.** Use the half angle itself: `(c, s) =
  (cos(θ/2), sin(θ/2))` as `positive=True` symbols, `b = (2c² − 1)·e₁ + 2sc·e₂`, and the one relation
  `s² → 1 − c²`. Then `|b| → 1`, `|R|² → 4c²`, `sqrt(4c²) → 2c` (positivity lets sympy take the root), and the
  rotor simplifies to exactly `c − s·e₁₂`.
- **Substitute before simplifying, blade-wise.** The comparison helper takes an optional substitution and
  applies it to each blade's *difference* before `simplify` (`_simplify_equal(a, b, subs=…)`). Substituting
  `s**2` hits it inside the `sqrt` argument too.
- **Prove the closed form itself as its own assertion** (`simplify(R.magnitude_squared() − 2|a||b|(|a||b| +
  a·b)) == 0`, fully symbolic in 2D and 3D) — it is a plain polynomial identity once `sqrt(x)**2 → x`.
- **Typing (ty):** `magnitude_squared()` is `Real = float | Expr`, so wrap it in `sympy.sympify` before
  `.subs`/`simplify`; a substitution map is `Mapping[sympy.Basic | complex, sympy.Expr | complex]` (dict keys
  are invariant, so `dict[Expr, Expr]` is rejected by sympy's `subs` overloads).

The Lean twin needs none of this: `Rotor.lean` proves the same chain structurally and gets Lagrange by `ring`
(`tasks/reference/unit-bivector-and-rotors.md` §7).

## Follow-on

`tasks/archive/2026/10/05/consolidate-symbolic-equality-predicate.md` (done 2026-10-05) — consolidate `_same_value`/`simplify_equal` into a
single public predicate and expand the symbolic tests. (Blocked on a small API decision — see that task.)

## Cross-links

- `tasks/reference/approximate-float-equality.md` — the numeric `isclose` sibling.
- `tasks/reference/code-generator-architecture.md` — how `tools/gen_specialized.py` emits classes
  (the `__eq__` here is one of its generated methods).
