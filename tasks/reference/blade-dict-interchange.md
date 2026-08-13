# The blade-dict interchange — `BladeCoef`

**Reference document** — the contract for `BladeCoef` (`dict[Blade, Coef]`), THE canonical
interchange format of gacalc: every representation converts to and from it, and all shared
arithmetic in `base.py` routes through it. Not a task; update in place if the contract
changes. Last updated 2026-08-13. Authoritative source: the `BladeCoef` docstring and
`_require_canonical_blades` in `src/gacalc/base.py` — this doc consolidates and explains
what lives there (and what was scattered across archived task docs). Read alongside
CLAUDE.md's "Architecture" (the interchange protocol) and `design-decisions.md`.

## What it is, and why it matters

A multivector has several *representations* — `Gn` (the general dict-of-blades reference),
the specialized `G1`/`G2`/`G3`, and the graded subtypes (`Vector2`, `Bivector3`, `Rotor2`,
`ScalarN`, ...). They all interoperate through **one** shared format:

    Blade      = tuple[int, ...]        # basis-vector indices; () is the scalar blade
    Coef       = int | float | sympy.Expr
    BladeCoef  = dict[Blade, Coef]      # e.g. {(): 3, (1, 2): -4}  ==  3 − 4·e₁e₂

Two methods are the whole protocol: `to_blade_dict()` (this value → the dict) and the
`from_blade_dict()` classmethod (the dict → this representation). Mixing two representations
(a `Vector2` and a `Gn`) works because both pass through the dict, and every
representation-independent method in `base.py` is written against it.

## The contract

### 1. Keys are canonical, or `from_blade_dict` raises

A key's basis-vector indices must be **strictly increasing**: `(1, 2)`, never `(2, 1)` or
`(1, 1)`; `()` is the scalar blade. Every representation's `from_blade_dict` runs the shared
`_require_canonical_blades` validator and **raises `ValueError`** on a bad key:

    >>> Gn.from_blade_dict({(2, 1): 1})     # ValueError
    >>> G2.from_blade_dict({(2, 1): 1})     # ValueError  (specialized classes too)
    >>> Gn.from_blade_dict({(1, 1): 1})     # ValueError  (repeated index)

`e₂e₁` is a legal algebra *element* — it just isn't a legal *key*: it equals `−e₁e₂`, so it
belongs under key `(1, 2)` with the sign folded into the coefficient (and a repeated index
contracts away, `eᵢeᵢ = 1`). The dict is **not** read as a signed permutation; it is a
canonical-key store.

**Why raise, not silently canonicalize (2026-07-29 decision).** `from_blade_dict` is an
interchange/constructor *primitive*, not user sugar, so a malformed key is a caller bug and
loud rejection fits. The raise replaced two *different* silent wrong answers that used to
depend on which representation you called: `Gn` stored the bad key raw (corrupt state), the
graded/full classes silently dropped it.

### 2. Zero coefficients are omitted; a missing blade reads as 0

`to_blade_dict` leaves out any exact-zero coefficient, and every reader treats a missing
blade as `0` (`.get(blade, 0)`). So `{(1,): 3}` and `{(1,): 3, (2,): 0}` are the same
multivector.

### 3. The eager/lazy "hidden zero" split

`Gn` **eager-simplifies** every coefficient in `__post_init__`, so a coefficient that is
*mathematically* zero but not *structurally* zero is simplified away, then pruned. The
specialized/graded classes are **lazy** — they prune only a structural `0` and keep an
un-reduced coefficient until asked:

    >>> t = sympy.Symbol("t")
    >>> Gn.from_blade_dict({(): cos(t)**2 + sin(t)**2 - 1}).to_blade_dict()
    {}                                     # eager: simplified to 0, pruned
    >>> G2.from_blade_dict({(): cos(t)**2 + sin(t)**2 - 1}).coeff_scalar
    sin(t)**2 + cos(t)**2 - 1              # lazy: kept un-reduced
    >>> _.simplified().to_blade_dict()
    {}                                     # simplify on demand

This is why `.simplified()` / `_repr_latex_` exist (show the lowest-terms form without
mutating the stored fields), and why a lazy value can compare `==` to a simpler one even
though their raw dicts differ.

### 4. A graded type keeps ONLY its own blades (the "exp() trap")

A graded subtype's `from_blade_dict` keeps only the blades that type carries; **foreign keys
are silently dropped** (they pass canonical validation — they just aren't this type's blades):

    >>> Vector2.from_blade_dict({(1,): 3, (2,): 4, (): 9, (1, 2): 5}).to_blade_dict()
    {(1,): 3, (2,): 4}                     # the scalar and e₁₂ are dropped

Consequence — the trap: a result that carries a **new grade** must be built via
**dispatching arithmetic**, never via `from_blade_dict` on the operand's own type. A
`Bivector` whose exponential is a `Rotor` (scalar + bivector) cannot be built as
`Bivector.from_blade_dict({…scalar…, …bivector…})` — the scalar part would be dropped; it
must be built with `+` / `*`, which dispatches to the type that can hold the result
(`Bivector + scalar → Rotor`). This is exactly why `MultiVectorBase.exp` builds its result
with a dispatching `+`, not `from_blade_dict` (see its docstring).

## Where it lives

- **`src/gacalc/base.py`** — the `Blade` / `Coef` / `BladeCoef` aliases and the `BladeCoef`
  docstring (the authoritative contract); `_require_canonical_blades` (the shared validator);
  the abstract `from_blade_dict` / `to_blade_dict` on `MultiVectorBase`.
- **`src/gacalc/gn.py`** — `Gn.from_blade_dict` / `to_blade_dict` (calls the validator;
  the eager `sympy.simplify` in `__post_init__`).
- **The generated modules** — `from_blade_dict_method` in `tools/gen_specialized.py` emits
  each specialized class's `from_blade_dict`, which calls `_require_canonical_blades` then
  keeps only its own blades (the silent-drop in §4).

## Sources

- `src/gacalc/base.py` (`BladeCoef` docstring + `_require_canonical_blades`) — authoritative.
- `tasks/archive/2026/07/29/validate-blade-dict-keys.md` — the raise-vs-canonicalize decision.
- `tasks/archive/2026/07/29/blade-dict-tests-and-comments.md` — the consolidated contract + tests.
- Related: `tasks/reference/design-decisions.md`, `tasks/reference/code-generator-architecture.md`.
