# Type-precise products/sums on the generated graded types

**Status:** **DONE 2026-07-21.** The operators and named products/sums on the generated
graded types now type **precisely and soundly** (`v2 * v2 : Rotor2`, `v2 ^ v2 : Bivector2`,
`2 + 3*i2 : Rotor2`) instead of the old unsound `-> Self`. Gates green: 289 tests, `ty`
src/tests/tools clean, ruff clean, `check-regions` clean, generation deterministic.

> This doc is the durable record: the git history for this work is being squashed, so the
> **paths tried and reverted** below are preserved here on purpose.

## The problem

The generated graded types (`Vector2`/`Bivector2`/`Rotor2`/`Scalar`, and the 𝒢₃ set) declared
every product and sum method `-> typing.Self` and force-cast the real result to `Self`:

```python
class Vector2(MultiVectorBase):
    def _geometric_product(self, rhs) -> typing.Self:
        ...
        case Vector2():
            return typing.cast(typing.Self, Rotor2(...))   # a Rotor2 cast to "Vector2"
```

`Vector2 * Vector2` is a **vector × vector = scalar + bivector = Rotor2** (even). But the method
said `-> Self`, so **`v2 * v2` mistyped as `Vector2`** while returning a `Rotor2` at runtime —
an unsound cast that hid the mismatch both ways (`.coeff_e_12` was type-rejected though valid;
`.coeff_e_1` type-checked but would `AttributeError`). Root cause:
`MultiVectorBase._geometric_product -> Self` (base.py:169) types the product as grade-preserving,
which it isn't. Runtime was always correct; this was purely a **static-typing** defect. The
result type per `(lhs, rhs)` pair is *already computed* at generation time by `product_result`
(smallest registered type covering the symbolic support, else widen to `G_n`) — the cast just
threw that precision away.

## Paths tried

### Path 1 — free functions + delegation (BUILT, then REVERTED)

First implementation (committed, then reverted in the working tree):

- Emitted **per-pair free functions** `geometric_product_vector2_vector2(lhs, rhs) -> Rotor2`
  etc. (module-level, cast-free, concrete return) for the three bilinear products.
- Emitted an **overloaded free-function "front" per op** (`geometric_product`/`outer_product`/
  `inner_product`) that dispatched to the operator and carried `@overload`s for the precise type.
- Made the generic `match` **delegate** to the per-pair functions on grade-changing arms
  (same-type arms stayed inline via `type(self)` for subclass preservation), which also deduped
  the pre-`match` fast-path vs `case` formula duplication.
- Scope wrinkle found here: **`Scalar` could not be an lhs.** `scalar.py` is hand-built and
  coerces an identically-zero product (e.g. `scalar · bivector = 0`) to a `Gn`, so a
  `Scalar`-lhs front would return `Gn` while its overload promised `Scalar` — unsound. `Scalar`
  was kept as an rhs only.

It worked (388 tests green). **Why reverted:** it left the *operators* untouched, so `v2 * v2`
still mistyped as `Vector2`. Bill disliked that ("all those functions no longer needed… should
they be reverted?"). Everything from Path 1 — the per-pair functions, the fronts, the delegation,
and its test `tests/test_typed_products.py` — was reverted (`git checkout <pre-work> -- tools/
gen_specialized.py`, `rm tests/test_typed_products.py`). The `Scalar`-lhs exclusion is now moot.

### Path 2 — overload the operators directly (SHIPPED)

The key enabler was correcting a wrong assumption. I had believed overloading `__mul__` over a
`-> Self` base was blocked by Liskov (a `Rotor2` return isn't a subtype of `Self = Vector2`).
**Verified with `ty` experiments that this is false:** `ty` accepts subclass `@overload`s
returning non-`Self` types over a `-> Self` base — a base-typed caller gets `Base`, a
`Vector2`-typed caller gets `Rotor2`, a subclass-of-`Vector2` caller gets `Rotor2`, with no
`invalid-method-override`. And it's **sound**: the overload return equals what the impl returns
at runtime, unlike the `-> Self` cast which lied.

So the shipped design puts the overloads **on the operator/product methods themselves**:

- `__mul__` (`*`), `__xor__` (`^` — overridden; base returns `Self`), `outer_product`,
  `inner_product` each carry one `@typing.overload` per rhs type returning the resolved concrete
  type, plus a scalar-scaling overload (`__mul__`) and a `MultiVectorBase` catch-all (→ `G_n`).
- The **implementations are the original inline `match`** (runtime untouched); the overloads
  only supply precise static types.
- The full class `G_n` is **not** overloaded — its products stay `-> Self`, already correct
  (`G2 * G2 → G2`).

Result — verified by `ty reveal_type` and `typing.assert_type`:
`v2 * v2 → Rotor2`, `v2 ^ v2 → Bivector2`, `.outer_product → Bivector2`,
`.inner_product → Scalar`, `v2 * 3 → Vector2`; 𝒢₃ likewise (`u * v → Rotor3`, `u ^ v → Bivector3`).

### Path 2 extension — `+` / `-` narrow by grade too

`scalar + bivector = Rotor2` (even), so `+`/`-` narrow just like the products. Added:

- `@overload`s on `__add__`/`__sub__` (same mechanism; the number-case overload returns the
  resolved `self ± scalar` type, e.g. `Bivector2 + scalar → Rotor2`).
- `__radd__`/`__rsub__` (number-on-the-**left**, e.g. `2 + 3*i2`) typed directly to that same
  resolved type — no overloads needed since their left operand is always a bare number.

So `3*i2 + 2`, `2 + 3*i2`, `i2 - 2`, `2 - i2` all narrow to `Rotor2`, while `i2 + i2` stays
`Bivector2`. This makes `notebooks/displaygraded.py`'s `r: Rotor2 = 2 + 3*i2` correct by inference.

### Implementation-return broadening to `MultiVectorBase`

An overloaded method's *implementation* return must be a supertype of every overload's return.
The overload returns (`Rotor2`, `Bivector2`, `Scalar`, `Vector2`, `G2`) are **all siblings under
`MultiVectorBase`** — none subclasses another or the full class `G_n`. So the six overloaded
impls were retyped from `-> Self` to **`-> MultiVectorBase`** (the one common supertype). This
makes each impl honest and self-consistent with its own overloads (the old `-> Self` claimed
`Vector2` while returning a `Rotor2`).

- **`G2` was tried and rejected** for this: because the graded types don't subclass `G2`,
  `Rotor2` is not assignable to `G2`, so `impl -> G2` fails the consistency check. Verified.
- Callers are unaffected — they resolve to the precise overload types; the impl return is
  internal-only.

## Considered and rejected

- **Operator declared `-> G2`** (a single wider return instead of overloads): **dominated.**
  Runtime returns a `Rotor2` (not a `G2` subclass), so it still needs a cast, and `G2` exposes
  `.coeff_e_1` which type-checks but crashes at runtime on the real `Rotor2`. Overloads give the
  *exact* `Rotor2` and are sound.
- **Re-typing the base products off `-> Self`** (the feared "big cross-cutting change"):
  **unnecessary.** `ty` accepts the subclass overloads over the `-> Self` base as-is, so base.py
  was never touched.

## The pyright thread (why it came up, and why it's moot)

Both projects use **`ty`** as their checker — gacalc's gate is `ty`; mvp's `format.sh` gate is
`ty` too. **pyright only lingers in mvp's *emacs LSP*** (`lsp-pyright`), which is being removed
(see the mvp task below). So pyright's opinion never reaches either gate.

A one-off pyright check (installed, then uninstalled) surfaced one genuinely useful thing that
`ty` is lenient about: `reportInconsistentOverload` — the impl's `-> Self` was inconsistent with
its overloads. That is what motivated the `-> MultiVectorBase` impl broadening above (a real
honesty improvement even for `ty`). pyright would additionally flag `reportOverlappingOverload`
on the `MultiVectorBase` catch-all overlapping the specific overloads — **not chased**, since we
are `ty`-only. Bottom line: no code decision hinges on pyright.

## Consumer impact (what the precise types unlock)

Runtime was always correct, so nothing *needs* changing. What benefits:

- **mvp** reads a wedge's coefficient via the base `.coefficient(Bivector2.e_12)` reader because
  `.coeff_e_12` was type-rejected on the mis-typed `Vector2`. With precise types, those become
  direct `.coeff_e_12` reads, and `find_normal`'s `bivector = (p2-p1)^(p3-p1)` types honestly as
  `Bivector3`. Sites: `src/modelviewprojection/mathutils.py:209,309`,
  `framebuffer/softwarerendering.py:58,84`. **Gated** on a gacalc release carrying the overloads
  + bumping mvp's `gacalc==0.0.11` pin. Captured in mvp
  `tasks/precise-product-types-coefficient-cleanup.md`.
- **gacalc notebooks:** the `displaygraded.py` annotations (`i2: Bivector2 = a ^ b`, `biv`, `B`,
  `B3`, `r: Rotor2 = 2 + 3*i2`) are on reused, pedagogical locals and are now **correct by
  inference**. The teaching-notebook standard ("name + type the GA values") says to **keep**
  them — nothing to drop. gacalc has no `.coefficient()` getter-workarounds (that's mvp-only).
- **Odd-type gap is not a prerequisite.** In 𝒢₃ only the *raw full geometric product* of an
  odd-producing pair (e.g. `Rotor3*Vector3`) widens to `G3` for lack of a registered `{1,3}`
  type; the operations actually used are already precise (`Rotor3.sandwich(x) -> type(x)`,
  `Vector3.inner_product(Bivector3) -> Vector3`, `Vector3 ^ Bivector3 -> Trivector3`). Left at
  `-> G3`; see `tasks/model-odd-graded-type.md`.

## Files changed

- **`tools/gen_specialized.py`** — the generator. Adds `product_overload_stubs(...)` (emits the
  `@overload` signatures per rhs, with the number/catch-all cases), wires it onto `__mul__`,
  `__xor__` (a new overridden method delegating to `outer_product`), `outer_product`,
  `inner_product`, `__add__`, `__sub__`; sets those impls' return type to `MultiVectorBase`
  (`mvb_ann`); types `__radd__`/`__rsub__` to the resolved `self ± scalar` type. `dispatch_method`
  gained a `return_type` override use for the broadened impls (already existed for the sandwich).
- **`tools/astbuild.py`** — `_is_overload(...)` + a skip in `inject_region_markers` so `@overload`
  stubs (which share the method name) don't emit duplicate `<Class> <method> method`
  doc-regions; only the implementation carries the region. Keeps `check-regions` clean.
- **`tests/test_operator_typing.py`** (new) — guards the **static** types with
  `typing.assert_type` (a regression fails `ty check tests`) plus runtime type/value checks, for
  products and for the add/sub narrowing.
- Removed `tests/test_typed_products.py` (Path 1's test).
- The generated `g1/g2/g3.py`/`scalar.py` are gitignored — they grow (overload stubs) but don't
  appear in `git diff`. `scalar.py`/base.py untouched.

## Constraints respected

Generated code stays provably consistent with `Gn` (runtime `match` untouched); value types stay
mutable (`slots=True`, not frozen); no hand-edits to `src/gacalc/*.py` (all in `tools/`); method
docstrings still copied from base; determinism gate (`make check-generated`) green.

## Follow-ups

1. **mvp: `switch-typechecker-pyright-to-ty.md`** — make ty the only checker (gate already ty;
   remove the pyright emacs-LSP leftover). Proposed.
2. **mvp: `precise-product-types-coefficient-cleanup.md`** — the `.coefficient(...)` →
   `.coeff_e_12` + `find_normal` cleanups. Proposed, gated on a gacalc release + pin bump.
3. **`wedge` / `dot` aliases still return `-> Self`** — only `*`/`^`/`outer_product`/
   `inner_product` were overloaded. Secondary aliases; overload them too if wanted. Low priority.
4. **Bring the gacalc notebooks into the `ty` scope** now that their GA code type-checks cleanly
   — bigger (jupytext/matplotlib), separate task if wanted.
5. **`Scalar` as a product lhs** — would need `scalar.py` to adopt the resolve-and-construct
   discipline (it currently coerces zero results to `Gn`). Only relevant if a `Scalar`-lhs typed
   entry point is ever wanted; the operator overloads already handle `Scalar` as an rhs.
