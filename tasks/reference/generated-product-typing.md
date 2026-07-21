# How the generated graded types type their products & sums

**Reference document** — the design and *rationale* for the precise `@typing.overload` typing on
the generated graded types' products/sums (so `v2 * v2 : Rotor2`, not `Vector2`). Not a task;
update in place if the generator's product typing changes. Last updated 2026-07-21. Origin: the
type-precise products/sums work — `tasks/archive/2026/07/21/typed-product-helper-functions.md`.

## The design

Each generated graded type (`Vector2`/`Bivector2`/`Rotor2`/`Scalar`, and the 𝒢₃ set) carries
`@typing.overload` signatures on its product/sum methods, so a known-type call site gets the
**exact** result type:

- `__mul__` (`*`), `__xor__` (`^`), `outer_product`, `inner_product`, `__add__`, `__sub__` — one
  `@overload` per rhs type returning the **resolved concrete type** (e.g. `Vector2 * Vector2 ->
  Rotor2`, `Vector2 ^ Vector2 -> Bivector2`, `Bivector2 + scalar -> Rotor2`), plus a scalar/number
  overload and a `MultiVectorBase` catch-all (→ the full class `G_n`).
- `__radd__` / `__rsub__` (number on the **left**, `2 + 3*i2`) are typed directly to the resolved
  `self ± scalar` type — no overloads, since their left operand is always a bare number.
- The **implementations are the original inline `match`** — runtime is unchanged; the overloads
  only supply static types.
- Each overloaded impl returns **`-> MultiVectorBase`** (not `-> Self`).
- The full class `G_n` is **not** overloaded — its products stay `-> Self`, already correct
  (`G2 * G2 → G2`).

Precision (guarded by `typing.assert_type` in `tests/test_operator_typing.py`, so a regression
fails `ty check tests`): `v2 * v2 → Rotor2`, `v2 ^ v2 → Bivector2`, `.inner_product → Scalar`,
`v2 * 3 → Vector2`, `2 + 3*i2 → Rotor2`; 𝒢₃ likewise. Runtime was always correct — this was a
static-typing fix, replacing an unsound `typing.cast(typing.Self, Rotor2(...))`.

## Why this design (decisions & rejected alternatives)

- **Overloads on the methods, not free functions.** An earlier version used per-pair free
  functions + a front per op + generic-`match` delegation, leaving the operators untouched — so
  `v2 * v2` still mistyped as `Vector2`. Overloading the methods fixes the operator itself; the
  free-function approach was reverted.
- **No base.py change is needed.** `MultiVectorBase._geometric_product` etc. are `-> Self`. It's a
  natural assumption (I held it, wrongly) that overloading a subclass method to return a
  non-`Self` type is a Liskov violation the checker rejects. **`ty` accepts it** — a base-typed
  caller gets the base type, a concrete-typed caller gets the precise overload type, subclasses
  inherit the overloads — and it is **sound**: the overload return equals what the impl returns at
  runtime (unlike the old `-> Self` cast, which lied). So base.py stayed untouched.
- **Impl return is `MultiVectorBase`, not `Self` or `G_n`.** An overloaded impl's return must be a
  supertype of *every* overload return. The overload returns (`Rotor2`, `Bivector2`, `Scalar`,
  `Vector2`, `G2`) are **all siblings under `MultiVectorBase`** — none subclasses another or the
  full class `G_n`. So `MultiVectorBase` is the only common supertype. `-> G2` was tried and
  fails (a `Rotor2` is not a `G2`). The old `-> Self` was internally inconsistent with its own
  overloads (claimed `Vector2` while an overload said `Rotor2`).
- **Not declaring the operator `-> G_n`** (a single wide return instead of overloads):
  **dominated.** Runtime returns a `Rotor2` (not a `G_n` subclass), so it still needs a cast, and
  `G_n` exposes coefficients the real `Rotor2` lacks (type-checks, crashes at runtime). Overloads
  give the *exact* type, soundly.

## Mechanism (in the generator)

- `tools/gen_specialized.py` `product_overload_stubs(...)` emits the `@overload` signatures per
  rhs (including the number-case and the `MultiVectorBase` catch-all), using the same
  `product_result` resolution the runtime `match` uses — so the overload types can't drift from
  the runtime results.
- The impls' return type is `MultiVectorBase` (`mvb_ann`); `dispatch_method`'s `return_type`
  parameter carries it for the four dispatched methods, and the inline `__mul__`/`__xor__` set it
  directly.
- `tools/astbuild.py` `_is_overload(...)` makes `inject_region_markers` **skip `@overload`
  stubs** — they share the method name, so marking them would emit duplicate `<Class> <method>
  method` doc-regions. Only the implementation carries the region; `make check-regions` stays
  clean.

## Related facts

- **Checker: `ty` for both gacalc and mvp.** gacalc's gate is `ty`; mvp's `format.sh` gate is
  `ty` too. **pyright** only appears in mvp's emacs LSP (being removed — mvp
  `tasks/switch-typechecker-pyright-to-ty.md`), so it never reaches either gate. A one-off pyright
  check surfaced `reportInconsistentOverload` (the impl's `-> Self` inconsistent with its
  overloads) — that is what motivated the `-> MultiVectorBase` broadening (an honesty improvement
  even for `ty`, which is lenient about it). pyright would also flag `reportOverlappingOverload`
  on the catch-all overlapping the specific overloads; **not chased**, since we are `ty`-only.
- **What precise types unlock for consumers:** direct `.coeff_e_12` field access instead of the
  base `.coefficient(blade)` reader — the reader was the workaround forced by the old mistype
  (`.coeff_e_12` was type-rejected on a mis-typed `Vector2`). See mvp
  `tasks/precise-product-types-coefficient-cleanup.md`.
- **The odd-type gap is not a prerequisite.** In 𝒢₃ only the *raw full geometric product* of an
  odd-producing pair (e.g. `Rotor3 * Vector3`, `Vector3 * Bivector3`) widens to `G3` for lack of a
  registered `{1,3}` type; the operations actually reached for are already precise
  (`Rotor3.sandwich(x) -> type(x)`, `Vector3.inner_product(Bivector3) -> Vector3`,
  `Vector3 ^ Bivector3 -> Trivector3`). Left at `-> G3`; see `tasks/model-odd-graded-type.md`.

## Not yet done (see the archived task's follow-ups)

- `wedge` / `dot` **aliases** still return `-> Self` — only `*`/`^`/`outer_product`/
  `inner_product` were overloaded. Secondary; overload them the same way if wanted.
- `Scalar` as a product **lhs** needs `scalar.py` to adopt the resolve-and-construct discipline
  (it coerces identically-zero results to `Gn`). `Scalar` works fine as an **rhs**.
