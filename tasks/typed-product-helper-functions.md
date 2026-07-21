# Type-precise product helper functions for the generated types

**Status:** research — findings below, **nothing implemented** (needs a go-ahead before any
generator change). Created 2026-07-21.

**Requested by:** Bill, 2026-07-21. The generated product methods (`_geometric_product`,
inner/outer, sandwich) are large `match` statements that build a result and
`typing.cast(typing.Self, ...)` it. Two questions:

1. **Q1 — feasibility:** can we emit, somewhere on the generated types or the module, a
   *specific* product function per known type pair (e.g. `_geometric_product_scalar_times_
   rotor`) where the parameter types are the concrete operands (not always `self`) and the
   **return type is the exact concrete type it returns** — then have the `match` arms call
   those functions and do the casting?
2. **Q2 — rewiring:** if so, can we then look through Bill's code and/or the generated code
   itself and, **where the types are statically known, call the appropriate specific
   function instead of the generic `-> Self` one**, so those call sites get the true type?

## The concrete problem (verified against freshly generated `src/gacalc/g2.py`)

`_geometric_product` and `__mul__` on every generated type are declared `-> typing.Self`,
and each `match` arm force-casts its concrete result to `Self`:

```python
class Vector2(MultiVectorBase):
    def _geometric_product(self, rhs) -> typing.Self:
        if type(rhs) is Vector2:                       # perf fast-path (see note)
            return typing.cast(typing.Self, Rotor2(coeff_scalar=..., coeff_e_12=...))
        match rhs:
            case Vector2():                            # same closed form again
                return typing.cast(typing.Self, Rotor2(...))
            ...
```

`Vector2 * Vector2` is a **vector × vector = scalar + bivector = `Rotor2`** (even). But the
method is typed `-> Self`, so:

- **the cast is unsafe** — `typing.cast(typing.Self, Rotor2(...))` asserts a `Rotor2` is a
  `Vector2`, which is false. The checker believes `v1 * v2 : Vector2`; at runtime it's a
  `Rotor2`. The cast hides the mismatch **both ways** (accessing `.coeff_e_12` on the
  "`Vector2`" is a type error though valid at runtime; accessing `.coeff_e_1` type-checks but
  would `AttributeError`). This is the real motivation for Q1/Q2 — not just tidiness.
- Root cause: `MultiVectorBase._geometric_product(self, rhs) -> Self` (base.py:169) types the
  product as grade-preserving, which a geometric product is **not**. The generated overrides
  inherit that signature and paper over it with the cast.

**Two observations for the same-type case** (`if type(rhs) is Vector2` *and* `case
Vector2()`): the pre-`match` `if` is an intentional perf fast-path (the "added performance
improvements in generated code" commit; comment at `gen_specialized.py:1020`) for the
dominant same-type operand; the `case Vector2()` is then reached only by a *subclass* of
Vector2 (none exist today), so it's near-dead but kept for completeness. Both emit the
**same** closed form — a natural first customer for a shared typed helper (dedupes them).

## Q1 — feasibility: YES, and the generator already has everything needed

At generation time `dispatch_method` (gen_specialized.py:929) already computes, per
`(self_spec, rhs_spec)` pair:
`result_spec, out_exprs = product_result(self_spec, rhs_spec, gn_product, n, full_name)`
— i.e. **the concrete result type and its closed-form coefficient expressions are known
before any cast.** `result_block_stmts` (gen_specialized.py:866) already renders exactly
`cse temps + return RType(field=…, …)`. Extracting a typed helper is near-mechanical:

```python
# module-level in g2.py — concrete param + concrete return, NO cast:
def _geometric_product_vector2_vector2(lhs: Vector2, rhs: Vector2) -> Rotor2:
    return Rotor2(
        coeff_scalar=lhs.coeff_e_1 * rhs.coeff_e_1 + lhs.coeff_e_2 * rhs.coeff_e_2,
        coeff_e_12=lhs.coeff_e_1 * rhs.coeff_e_2 - lhs.coeff_e_2 * rhs.coeff_e_1,
    )
```

and the `match`/fast-path arms become one line each:

```python
        if type(rhs) is Vector2:
            return typing.cast(typing.Self, _geometric_product_vector2_vector2(self, rhs))
        match rhs:
            case Vector2():
                return typing.cast(typing.Self, _geometric_product_vector2_vector2(self, rhs))
```

**Important scope-setting:** extraction **does not remove the cast inside
`_geometric_product`** — that method is still declared `-> Self` (a Liskov override of the
ABC), so its arms must still cast the concrete helper result to `Self`. What extraction buys:
(a) the concrete result type now lives in one honest, cast-free place (the helper), and (b)
**known-type call sites can bypass the `-> Self` method entirely** and get the true type
(that's Q2). The generic method stays for the polymorphic path (`MultiVectorBase * MultiVectorBase`).

**Design decisions to settle (my recommendations in bold):**
- **Where:** **module-level free functions** in each `g*.py` (and `scalar.py`). Concrete types
  are all in scope there; no `Self` involved; no import-cycle risk. (A `@staticmethod` on the
  class works too but buys nothing and reads worse.)
- **Naming:** Bill's `_geometric_product_scalar_times_rotor` shape → **`_<op>_<lhs>_<rhs>`**,
  e.g. `_geometric_product_vector2_vector2`, `_inner_product_rotor2_vector2`,
  `_outer_product_bivector2_vector2`, `_sandwich_rotor2_vector2`. Lowercased type names, so
  unique and prefix-free. (Underscore-private: they're an implementation surface, exposed for
  typed call sites but not part of the teaching API.)
- **Which operations:** the four that go through `dispatch_method` — geometric, inner, outer,
  and the rotor sandwich. `__add__`/`__sub__` are already same-type (linear), so they don't
  need this. `__mul__`/`__xor__` are thin wrappers that delegate to the primitives.
- **Cost:** combinatorial. Per class, one helper per rhs in the registry (Scalar + graded +
  full Gₙ). Ballpark: **g2 ≈ 60–90 helpers, g3 substantially more**; file sizes grow. Options
  to bound it (decide later): emit helpers only for pairs where `result != lhs` (the ones the
  `-> Self` cast actually mistypes), or only for pairs consumers use. My lean: **emit them
  uniformly** — uniformity is the generator's whole value, and dead helpers cost only bytes.

## Q1 alternative worth weighing: `@typing.overload` on the operators

A more *ergonomic* way to give known-type call sites the true type is to overload the
operator itself, so `a * b` keeps its syntax but gets a precise return type:
```python
    @typing.overload
    def __mul__(self, rhs: Vector2) -> Rotor2: ...
    @typing.overload
    def __mul__(self, rhs: Scalar) -> Vector2: ...
```
**But there's a real blocker:** the base declares `__mul__(...) -> Self`, and `Rotor2` is
**not** a subtype of `Vector2` (= `Self`), so an overload returning `Rotor2` is **not a
covariant-return override** — ty/pyright will likely reject it as an incompatible override.
The **named-helper route avoids this entirely** because a helper is a *new function*, not an
override of a `-> Self` method — which is a genuine point in favor of Bill's original idea
over operator overloads. (Overloads could still work if the products were re-typed off
`Self`, a much larger change.) **Recommendation:** go with named helpers; note overloads as a
possible later ergonomic layer if the `-> Self` base signature is ever revisited.

## Q2 — rewiring known-type call sites

Two populations:
- **Inside the generated code** — trivial and generator-driven: the fast-path `if` and each
  `match` arm call the helper (shown above). This also dedupes the fast-path/case pair.
  Whether any *other* generated method (e.g. a product used inside another closed form) has a
  statically-known pair to rewire: TBD from the generated source.
- **In Bill's / consumer code** (mvp, notebooks, tests) — where two concrete types are
  multiplied and the result type differs from the lhs, calling the helper yields the correct
  static type instead of the current mistype. **Scope + value being measured by a consumer
  scan — see "Consumer sites" below.**

## Prior design context (from archived task docs — don't relitigate these)

- **The result-type resolution already exists and is exact.** `resolve` (smallest registered
  type whose blades ⊇ the symbolic support, else widen to full `Gₙ`) + `product_result`
  derive each pair's type and closed form *symbolically from `Gn`*, at generation time — never
  from runtime floats (`graded-blade-subtypes.md`). So a helper's concrete return type is
  already computed; we're only relocating it.
- **`Vector*Vector → Rotor` is the *correct* type, not a bug.** The mis-typings that were
  found+fixed were the opposite (products typed *too wide*): the rotor `sandwich` (was
  falsely `Self`, fixed to `_OperandT` via `cast_operand` — `restore-ty-on-generated-
  sandwich.md`) and `project` (widened a grade-preserving result to `G3`, narrowed back —
  `project-grade-preserving-narrowing.md`). Typed helpers are the same *spirit* (give the
  honest concrete type) applied to the general products.
- **⚠ Pedagogical tension to weigh (this is the main judgment call).** The `match`-on-rhs
  ladder was a *deliberate* design so each product "reads as the grade product table made
  visible" (`graded-blade-subtypes.md`). Extracting the closed forms into named helpers moves
  the actual formulas *out* of the `match`. Two readings: it could **help** (the `match`
  becomes a clean dispatch table — `case Vector2(): return _geometric_product_vector2_vector2(
  self, rhs)` — and each helper's name+signature *documents* the type relationship `Vector2 ×
  Vector2 → Rotor2`), or **hurt** (a reader now jumps to another function to see the algebra).
  My lean: it **helps** — the named signatures make the product table's *type* structure
  explicit where today it's buried under a cast — but Bill should decide, since the "table
  made visible" goal was explicit.
- **No `_OperandT`/`Self` issue for helpers.** Helpers are free functions with concrete types,
  so none of the Liskov/`Self` machinery applies to them (that stays on the polymorphic
  methods).
- **Interaction with the odd-type gap (`model-odd-graded-type.md`, not started).** In 𝒢₃,
  `Rotor3*Vector3`, `Vector3*Bivector3`, `Rotor3*Trivector3` currently widen to `G3` because
  there's no registered odd `{1,3}` type. A helper for those pairs would have to return `G3`
  too — so typed helpers **don't** fix that gap, but they'd make each such widening explicit
  and would automatically become type-precise if/when an `Odd3` type is modeled. Worth doing
  that task first *or* accepting `-> G3` helpers for those pairs now.

### Two mechanical wrinkles the implementation must handle

- **Docstrings:** generated *methods* copy their docstring from the matching `MultiVectorBase`
  method (`inspect.getdoc`). A per-pair helper has **no** base method to copy from — so decide
  a helper docstring policy (my suggestion: a one-line generated doc like
  `"Geometric product  Vector2 × Vector2 → Rotor2."`, or none since they're private).
- **Doc-region markers:** `astbuild.inject_region_markers` wraps each generated class/method;
  new module-level helper functions need marker handling that stays collision-free
  (`make check-regions` gate), or an explicit decision to leave free functions unmarked.

### Consumer sites measured (mvp src, gacalc notebooks + tests)

Every concrete-type product site classified **(a)** result == lhs (Self is right — helper adds
precision only) or **(b)** result != lhs (Self is a *mistype* a helper would correct):

- **mvp (the real app): 5 sites, ALL outer products (`^`), ALL class (b), and ZERO raw
  geometric products / inner / sandwich between concrete types.** Rotations already route
  through precisely-typed `plane_rotation(...)` / `sandwich`. So a *geometric-product* helper
  doesn't touch mvp at all — only the *outer-product* helper is relevant, at 5 wedge sites
  (`mathutils.py:209,272,309`; `framebuffer/softwarerendering.py:58,84`). All already use
  `.coefficient(Bivector2.e_12)` (a base reader) because `.coeff_e_12` would be **ty-rejected**
  on a `Vector2`-typed value — the mistype *forces* the verbose form.
- **gacalc notebooks: ~26 concrete (b) sites — the main beneficiary.** Several **corrective
  hand-annotations** exist *solely* to relabel an operator result the type system calls `Self`:
  `displaygraded.py` `i2: Bivector2 = a ^ b`, `biv: Bivector3 = u ^ v`, `B: Bivector3 = …`,
  `B3: Bivector3 = …`. These are technically `Vector→Bivector` assignment errors, tolerated
  only because notebooks are outside the ty/test scope. **This cluster is the strongest
  concrete evidence for the helpers.**
- **gacalc tests: ~15 (b) sites** asserting `type(a ^ b) is Bivector2` etc. — the library
  verifying its own runtime grade resolution; some could become static.
- **No runtime bug anywhere.** The internal cast keeps runtime correct; every consumer already
  sidesteps the *static* mistype with base readers / explicit annotations / `MultiVectorBase`.
  This is a **static-precision** improvement, not a correctness fix.
- **Value concentrates in the OUTER product (→ bivector), not the geometric product** — mvp
  uses no raw `*` between concretes; notebooks' `*` sites are few next to `^`.

### The decisive design fact, and the real fork

**All base products are `-> typing.Self`** (`_geometric_product`, `__mul__`, `inner_product`,
`outer_product`, `wedge`, `__xor__`; only `sandwich -> _OperandT` and `scalar_product -> Coef`
differ). That single fact drives everything:

- **Bill's named-helper idea works precisely *because* it sidesteps `-> Self`** — a free
  function is not an override, so no Liskov constraint binds it. Good.
- **But the *ergonomic* ideal — keep writing `a ^ b` and have it type as `Bivector2` via an
  `@overload` on `__xor__` — is BLOCKED** by `-> Self`: `Bivector2` is not a subtype of
  `Self (= Vector2)`, so the overload is not a covariant-return override and ty/pyright reject
  it. Overloads become viable only if the base products are re-typed off `Self` (e.g.
  `-> MultiVectorBase`), a bigger cross-cutting change.
- **So Q2 carries an ergonomics tension:** calling `_outer_product_vector2_vector2(a, b)`
  instead of `a ^ b` gives the precise type but **uglifies exactly the pedagogical notebook
  code that benefits.** You get operator ergonomics *or* named-helper precision — not both —
  unless you re-type off `Self`.

Three coherent implementations follow:

- **Option A — named helpers + rewire call sites (Bill's literal ask).** Emit helpers; at the
  ~30 known-type sites call the helper instead of `*`/`^`. Precise, cast-free at those sites.
  Cost: replaces operator syntax with function calls in teaching code — I'd advise **not**
  applying this to the notebooks specifically, since it fights their whole purpose.
- **Option B — named helpers as the internal cast-free home only.** Emit helpers; the
  generated `match`/fast-path call them (this **dedupes** the fast-path `if` + `case` pair and
  gives each closed form one honest, cast-free home); **don't** touch consumer sites. Low-risk
  internal cleanup; does *not* deliver consumer type-precision.
- **Option C — re-type products off `Self` + emit `@overload`s (the "real" fix).** `a ^ b`
  types as `Bivector2` with **zero consumer changes**, and the corrective notebook annotations
  become unnecessary. Biggest change (touches base.py's product contract *and* every generated
  operator; must re-verify `Gn` precision and Liskov). The named helpers can be the cast-free
  bodies the overloads delegate to.

### Recommendation

The underlying want is "`a ^ b` should type honestly," and the beneficiaries *read operators* —
so **Option C is the only one that delivers the value without degrading the teaching code**,
but it's the largest and reopens the base `-> Self` product contract. If that's too big now,
**Option B is a safe, honest internal cleanup and a stepping stone to C** (it builds the exact
helpers C would delegate to). **Option A as literally described I'd not apply to notebook /
consumer sites** (ergonomics) — though the helpers it builds are the same ones B and C use.
Net: **do B now, hold C as the follow-up that actually lands consumer precision, skip A's
consumer rewiring.** And since mvp uses no raw `*`, if scoping tighter, the **outer-product**
helper carries almost all the consumer value.

## Constraints this task must respect (from CLAUDE.md + prior tasks)

- Generated code stays **provably consistent with `Gn`** — helpers reuse the *same*
  `product_result` closed form, so consistency is preserved by construction.
- Generated value types are **mutable (`slots=True`, not `frozen`)** — helpers take/return
  values, don't change this.
- **Never hand-edit generated `.py`** — all changes go in `tools/gen_specialized.py` /
  `tools/astbuild.py`; a correct change shows up as a `tools/` diff with nothing under
  `src/gacalc/`.
- Docstring-copied-from-base and doc-region-marker conventions still apply to emitted code.
- Don't churn the generator gratuitously; the `dispatch_method` change is localized.

## Open questions for Bill

1. **Which option** — A (rewire call sites to named helpers), **B (helpers as the internal
   cast-free home only, no consumer changes — my recommendation for now)**, or C (re-type
   products off `Self` + `@overload`s so `a ^ b` types precisely with zero consumer changes —
   the real fix, but the largest, and it reopens base.py's `-> Self` product contract)?
2. **Scope of operations** — all bilinear products (geometric + inner + outer), or **outer
   product first** (since mvp uses no raw `*` between concrete types, nearly all consumer
   value is in `^ → bivector`)?
3. **Ordering vs the odd-type gap** — decide `model-odd-graded-type.md` (the `{1,3}` odd type)
   *first*, so 𝒢₃ helpers for `Rotor3*Vector3` / `Vector3*Bivector3` can return a precise odd
   type instead of `-> G3`? Or accept `-> G3` helpers for those pairs now?
