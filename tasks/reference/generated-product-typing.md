# How the generated graded types type their products & sums

**Reference document** — the design and *rationale* for the precise `@typing.overload` typing on
the generated graded types' products/sums (so `v2 * v2 : Rotor2`, not `Vector2`). Not a task;
update in place if the generator's product typing changes. Last updated 2026-07-23. Origin: the
type-precise products/sums work — `tasks/archive/2026/07/21/typed-product-helper-functions.md`.

## The design

Each generated graded type (`Scalar2`/`Vector2`/`Bivector2`/`Rotor2`, and the 𝒢₃ set — the grade-0
`ScalarN` is per-algebra since the 2026-07-22 split, so grade-0 results below read `Scalar2`/`Scalar3`
by algebra where this doc's older examples say bare `Scalar`) carries
`@typing.overload` signatures on its product/sum methods, so a known-type call site gets the
**exact** result type:

- `__mul__` (`*`), `__xor__` (`^`), `outer_product`, `inner_product`, `_geometric_product`,
  `__add__`, `__sub__` — one `@overload` per rhs type returning the **resolved concrete type**
  (e.g. `Vector2 * Vector2 -> Rotor2`, `Vector2 ^ Vector2 -> Bivector2`, `Bivector2 + scalar ->
  Rotor2`), plus a scalar/number overload and a `MultiVectorBase` catch-all (→ the full class
  `G_n`). (`_geometric_product` — the primitive `__mul__` delegates to — was overloaded in a
  2026-07-22 follow-up so a direct caller also gets the precise type.)
- `__radd__` / `__rsub__` (number on the **left**, `2 + 3*i2`) are typed directly to the resolved
  `self ± scalar` type — no overloads, since their left operand is always a bare number.
  **Reflected ops need no overloads (investigated & confirmed 2026-07-23).** The "left is always a
  number" premise was verified by tracing: `__rmul__`/`__radd__`/`__rsub__` fire *only* with a number
  on the left, because every gacalc multivector-on-the-left is handled by that operand's own forward
  op (which never returns `NotImplemented`), so a multivector never reaches the reflected op. For that
  sole number-left case the single-signature typing is already precise (`2 * v → Vector2`,
  `2 + i2 → Rotor2`, `2 - v → G2`, `2 * Scalar2 → Scalar2`). **The one imprecision is a `sympy.Expr`
  on the left** (`t * v`): `ty` infers `Unknown` — but that is a **sympy operator-stub limitation, not
  a gacalc gap**, and **overloads cannot fix it**: `sympy.Expr.__mul__(Vector2)` "handles" the op in
  the checker's view (returns `Unknown`), so the checker never consults gacalc's `__rmul__` at all. At
  runtime sympy returns `NotImplemented`, so `__rmul__` fires and the value is correct (`Vector2`).
  Guarded by `test_reflected_operators_are_precise_for_numbers` /
  `…_runtime_including_symbolic_left` in `tests/test_operator_typing.py`; see
  `tasks/archive/2026/07/23/reflected-operator-typing-overloads.md`.
- `r_vector_part` (2026-07-22 follow-up) — same technique, but keyed on an **int literal** rather
  than an operand type: one `@overload` per grade `r: Literal[<0..DIMENSION>]` → that grade's
  resolved part type (present grade → its type, e.g. `Rotor2.r_vector_part(Literal[2]) ->
  Bivector2`; absent grade → `Scalar`, the returned zero), plus an `r: int -> MultiVectorBase`
  catch-all. Impl broadened to `-> MultiVectorBase`, unsound `Self` casts dropped (each `if r ==
  …:` arm returns its concrete type). Mechanism: a `cast` callback on `unary_stmt`/`unary_body`
  (default `cast_self`; identity for these broadened arms).
- `even_part` / `odd_part` (2026-07-22 follow-up) — **no argument to overload on**, so instead of
  `@overload`s the graded override just *declares* its resolved return type directly (`Vector2.even_part
  -> Scalar`, `Bivector3.odd_part -> Scalar`, `Rotor2.even_part -> Rotor2`), with no cast. That
  required retyping **`base.even_part`/`odd_part` from `-> Self` to `-> MultiVectorBase`** (a
  `-> Self` base can't be overridden by `-> Scalar`); the full class `G_n` keeps `-> Self` (a valid
  narrowing), and **`Gn` inherits the `-> MultiVectorBase` floor** (no override — nothing depended on
  `Gn.even_part()` statically being `Gn`, so no ceremony/cast was added). Emitted via the generator's
  `parity_part` helper; the `gn_unary` param on `unary_result`/`unary_body`/`parity_part` is
  `Callable[[Gn], MultiVectorBase]` so it accepts the now-`MultiVectorBase`-returning
  `even_part`/`odd_part` (Gn-returning ops like `dual` still fit by covariance).
- `dual` (2026-07-22, closes the unary-op family) — same "retype `base.dual` off `-> Self` to
  `-> MultiVectorBase`, graded override narrows to the resolved grade-(n−r) type" pattern as even/odd
  (`Bivector3.dual -> Vector3`, `Trivector3.dual -> Scalar3`, `Rotor3.dual -> G3` — odd {1,3} widens
  honestly). Two twists: (1) `dual` keeps the `n` (dimension) param, so a fixed-dimension type
  **raises on a mismatched `n`** rather than falling back to `G_n` (the old `_coerce(self, G_n).dual(n)`
  branch is gone — a `dim_mismatch_guard` helper); the full class `G_n` keeps `-> Self`. (2) The
  grade-0 `Scalar` had to become **per-algebra** (`Scalar1`/`Scalar2`/`Scalar3`, one per `gN.py`, no
  shared `scalar.py`) for `ScalarN.dual()` to name the same-module pseudoscalar without a circular
  import — see `tasks/archive/2026/07/22/per-algebra-scalar-types.md`. Emitted via a `dual_method` helper (graded) and a
  parametrized `generate_scalar(n, name, full_name)`.
- The **implementations keep the inline `match`** — runtime is unchanged; the overloads only supply
  static types. Each overloaded impl returns **`-> MultiVectorBase`** (not `-> Self`), and because
  of that its arms construct the result with **no cast** (`return Rotor2(...)`) — the old
  `cast(typing.Self, Rotor2(...))` was unsound and is gone from every product/sum arm (the
  grade-changing arms *and* the `case _:` Gn-fallback; 2026-07-22 follow-up).
- The full class `G_n` is **not** overloaded — its products stay `-> Self`, already correct
  (`G2 * G2 → G2`), and its arms keep the `Self` cast (legitimately: `-> Self` return).

Precision (guarded by `typing.assert_type` in `tests/test_operator_typing.py`, so a regression
fails `ty check tests`): `v2 * v2 → Rotor2`, `v2 ^ v2 → Bivector2`, `.inner_product → Scalar2`,
`v2 * 3 → Vector2`, `2 + 3*i2 → Rotor2`, `rotor2.r_vector_part(2) → Bivector2`,
`v2.r_vector_part(0) → Scalar2`; 𝒢₃ likewise (grade-0 → `Scalar3`). Runtime was always correct — this was a
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
  `ty` too. **pyright** only appears in mvp's emacs LSP (being removed —
  `tasks/switch-typechecker-pyright-to-ty.md` in `github.com/billsix/modelviewprojection`),
  so it never reaches either gate. A one-off pyright check surfaced `reportInconsistentOverload` (the impl's `-> Self` inconsistent with its
  overloads) — that is what motivated the `-> MultiVectorBase` broadening (an honesty improvement
  even for `ty`, which is lenient about it). pyright would also flag `reportOverlappingOverload`
  on the catch-all overlapping the specific overloads; **not chased**, since we are `ty`-only.
- **What precise types unlock for consumers:** direct `.coeff_e_12` field access instead of the
  base `.coefficient(blade)` reader — the reader was the workaround forced by the old mistype
  (`.coeff_e_12` was type-rejected on a mis-typed `Vector2`). See
  `tasks/archive/2026/07/22/precise-product-types-coefficient-cleanup.md` in
  `github.com/billsix/modelviewprojection`.
- **The odd-type gap is not a prerequisite.** In 𝒢₃ only the *raw full geometric product* of an
  odd-producing pair (e.g. `Rotor3 * Vector3`, `Vector3 * Bivector3`) widens to `G3` for lack of a
  registered `{1,3}` type; the operations actually reached for are already precise
  (`Rotor3.sandwich(x) -> type(x)`, `Vector3.inner_product(Bivector3) -> Vector3`,
  `Vector3 ^ Bivector3 -> Trivector3`). Left at `-> G3`; see `tasks/model-odd-graded-type.md`.

## `ScalarN` as a product lhs (done 2026-07-23)

`Scalar1`/`Scalar2`/`Scalar3` now carry the same overloads as the other graded types — so
`Scalar2 * Vector2 → Vector2`, `Scalar2 * Bivector2 → Bivector2`, `Scalar3 * Trivector3 →
Trivector3`, `Scalar2 + Bivector2 → Rotor2`, `Scalar2 + Vector2 → G2`, and `Scalar2.inner_product(X)
→ Scalar2` (scalar·X ≡ 0 under the Hestenes dot). **How:** `generate_scalar`'s bespoke hand-built
`__mul__` / `_geometric_product` / `outer_product` / `inner_product` / `__add__` / `__sub__` bodies
(which returned `-> Self` with an unsound `cast(Self, coeff * rhs)` on the general arm) were replaced
by the **same `product_overload_stubs(...)` + `dispatch_method(...)`** the graded generator uses —
so ScalarN is no longer a special case. The impls return `-> MultiVectorBase`, construct the resolved
concrete type per rhs, and the `case _` **coerces a foreign/`Gn` operand to `G_n`** (the old
hand-built body returned a bare `Gn` for a `Gn` rhs — now `Scalar2 * Gn → G2`, matching the
catch-all overload). Runtime is value-identical (conformance green); the changed return *types*
(`inner_product` now builds `Scalar2(0)` not a coerced `Gn`; `+`/`-` coerce to `G2`) are covered by
`assert_type` + runtime guards in `tests/test_operator_typing.py`
(`test_scalar_lhs_static_types` / `…_runtime_types_and_values`). The **reflected** ops
(`__rmul__`/`__radd__`/`__rsub__`) were left as-is — their overloads are the separate
`tasks/archive/2026/07/23/reflected-operator-typing-overloads.md`. See
`tasks/archive/2026/07/23/scalar-product-typing-overloads.md`.

## Not yet done (see the archived task's follow-ups)

- `wedge` / `dot` **aliases** still return `-> Self` — only `*`/`^`/`outer_product`/
  `inner_product` were overloaded. Secondary; overload them the same way if wanted.
- **`ScalarN` contractions** (`left_contraction`/`right_contraction`/`<`/`>`) are still **inherited
  from `base`** (typed `-> Self`), so e.g. `Scalar2 < Vector2` mistypes as `Scalar2` (runtime widens).
  Out of scope for the products task; give ScalarN its own `dispatch_method` contractions the same way
  if wanted (a small, mechanical addition now that its arithmetic is dispatch-based).
