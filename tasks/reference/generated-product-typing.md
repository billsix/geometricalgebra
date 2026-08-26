# How the generated graded types type their products & sums

**Reference document** — the design and *rationale* for the precise `@typing.overload` typing on
the generated graded types' products/sums (so `v2 * v2 : Rotor`, not `Vector`). Not a task;
update in place if the generator's product typing changes. Last updated 2026-08-22. Origin: the
type-precise products/sums work — `tasks/archive/2026/07/21/typed-product-helper-functions.md`.

## The design

Each generated graded type (`Scalar`/`Vector`/`Bivector`/`Rotor`, and the 𝒢₃ set — the grade-0
`ScalarN` is per-algebra since the 2026-07-22 split, so grade-0 results below read `Scalar`
by algebra where this doc's older examples say bare `Scalar`) carries
`@typing.overload` signatures on its product/sum methods, so a known-type call site gets the
**exact** result type:

- `__mul__` (`*`), `__xor__` (`^`), `outer_product`, `inner_product`, `_geometric_product`,
  `__add__`, `__sub__` — one `@overload` per rhs type returning the **resolved concrete type**
  (e.g. `Vector * Vector -> Rotor`, `Vector ^ Vector -> Bivector`, `Bivector + scalar ->
  Rotor`), plus a scalar/number overload and a `MultiVectorBase` catch-all (→ the full class
  `G_n`). (`_geometric_product` — the primitive `__mul__` delegates to — was overloaded in a
  2026-07-22 follow-up so a direct caller also gets the precise type.)
- `__radd__` / `__rsub__` (number on the **left**, `2 + 3*i2`) are typed directly to the resolved
  `self ± scalar` type — no overloads, since their left operand is always a bare number.
  **Reflected ops need no overloads (investigated & confirmed 2026-07-23).** The "left is always a
  number" premise was verified by tracing: `__rmul__`/`__radd__`/`__rsub__` fire *only* with a number
  on the left, because every gacalc multivector-on-the-left is handled by that operand's own forward
  op (which never returns `NotImplemented`), so a multivector never reaches the reflected op. For that
  sole number-left case the single-signature typing is already precise (`2 * v → Vector`,
  `2 + i2 → Rotor`, `2 - v → G`, `2 * Scalar → Scalar`). **The one imprecision is a `sympy.Expr`
  on the left** (`t * v`): `ty` infers `Unknown` — but that is a **sympy operator-stub limitation, not
  a gacalc gap**, and **overloads cannot fix it**: `sympy.Expr.__mul__(Vector)` "handles" the op in
  the checker's view (returns `Unknown`), so the checker never consults gacalc's `__rmul__` at all. At
  runtime sympy returns `NotImplemented`, so `__rmul__` fires and the value is correct (`Vector`).
  Guarded by `test_reflected_operators_are_precise_for_numbers` /
  `…_runtime_including_symbolic_left` in `tests/test_operator_typing.py`; see
  `tasks/archive/2026/07/23/reflected-operator-typing-overloads.md`.
- `r_vector_part` (2026-07-22 follow-up) — same technique, but keyed on an **int literal** rather
  than an operand type: one `@overload` per grade `r: Literal[<0..DIMENSION>]` → that grade's
  resolved part type (present grade → its type, e.g. `Rotor.r_vector_part(Literal[2]) ->
  Bivector`; absent grade → `Scalar`, the returned zero), plus an `r: int -> MultiVectorBase`
  catch-all. Impl broadened to `-> MultiVectorBase`, unsound `Self` casts dropped (each `if r ==
  …:` arm returns its concrete type). Mechanism: a `cast` callback on `unary_stmt`/`unary_body`
  (default `cast_self`; identity for these broadened arms).
- `even_part` / `odd_part` (2026-07-22 follow-up) — **no argument to overload on**, so instead of
  `@overload`s the graded override just *declares* its resolved return type directly (`Vector.even_part
  -> Scalar`, `Bivector.odd_part -> Scalar`, `Rotor.even_part -> Rotor`), with no cast. That
  required retyping **`base.even_part`/`odd_part` from `-> Self` to `-> MultiVectorBase`** (a
  `-> Self` base can't be overridden by `-> Scalar`); the full class `G_n` keeps `-> Self` (a valid
  narrowing), and **`Gn` inherits the `-> MultiVectorBase` floor** (no override — nothing depended on
  `Gn.even_part()` statically being `Gn`, so no ceremony/cast was added). Emitted via the generator's
  `parity_part` helper; the `gn_unary` param on `unary_result`/`unary_body`/`parity_part` is
  `Callable[[Gn], MultiVectorBase]` so it accepts the now-`MultiVectorBase`-returning
  `even_part`/`odd_part` (Gn-returning ops like `dual` still fit by covariance).
- `exp` (2026-07-29) — a thin cast-and-delegate narrowing override on `Bivector_n` only:
  `Bivector_n.exp() -> Rotor_n` (the exponential map onto the rotors). Unlike the products, the
  body is NOT a generated closed form (transcendental — the cse machinery is polynomial); it
  delegates to the shared `MultiVectorBase.exp`, whose dispatching-add construction already
  produces a `Rotor_n` at runtime. `Vector_n`/`Trivector` get no override (scalar+vector /
  scalar+trivector have no covering graded type — they widen honestly to `G_n`).
- `dual` (2026-07-22, closes the unary-op family) — same "retype `base.dual` off `-> Self` to
  `-> MultiVectorBase`, graded override narrows to the resolved grade-(n−r) type" pattern as even/odd
  (`Bivector.dual -> Vector`, `Trivector.dual -> Scalar`, `Rotor.dual -> G` — odd {1,3} widens
  honestly). Two twists: (1) `dual` keeps the `n` (dimension) param, so a fixed-dimension type
  **raises on a mismatched `n`** rather than falling back to `G_n` (the old `_coerce(self, G_n).dual(n)`
  branch is gone — a `dim_mismatch_guard` helper); the full class `G_n` keeps `-> Self`. (2) The
  grade-0 `Scalar` had to become **per-algebra** (`Scalar`, one per `gN.py`, no
  shared `scalar.py`) for `ScalarN.dual()` to name the same-module pseudoscalar without a circular
  import — see `tasks/archive/2026/07/22/per-algebra-scalar-types.md`. Emitted via a `dual_method` helper (graded) and a
  parametrized `generate_scalar(n, name, full_name)`.
- The **implementations keep the inline `match`** — runtime is unchanged; the overloads only supply
  static types. Each overloaded impl returns **`-> MultiVectorBase`** (not `-> Self`), and because
  of that its arms construct the result with **no cast** (`return Rotor(...)`) — the old
  `cast(typing.Self, Rotor(...))` was unsound and is gone from every product/sum arm (the
  grade-changing arms *and* the `case _:` Gn-fallback; 2026-07-22 follow-up).
- The full class `G_n` is **not** overloaded — its products return the concrete `-> G` (a `@final`
  class; changed from `-> typing.Self` 2026-08-22, see the high-dim ty section below), already
  correct (`G * G → G`), and its coerce-branch keeps a `cast(Self, …)` (fine: `Self <: G`).

Precision (guarded by `typing.assert_type` in `tests/test_operator_typing.py`, so a regression
fails `ty check tests`): `v2 * v2 → Rotor`, `v2 ^ v2 → Bivector`, `.inner_product → Scalar`,
`v2 * 3 → Vector`, `2 + 3*i2 → Rotor`, `rotor2.r_vector_part(2) → Bivector`,
`v2.r_vector_part(0) → Scalar`; 𝒢₃ likewise (grade-0 → `Scalar`). Runtime was always correct — this was a
static-typing fix, replacing an unsound `typing.cast(typing.Self, Rotor(...))`.

## Why this design (decisions & rejected alternatives)

- **Overloads on the methods, not free functions.** An earlier version used per-pair free
  functions + a front per op + generic-`match` delegation, leaving the operators untouched — so
  `v2 * v2` still mistyped as `Vector`. Overloading the methods fixes the operator itself; the
  free-function approach was reverted.
- **No base.py change is needed.** `MultiVectorBase._geometric_product` etc. are `-> Self`. It's a
  natural assumption (I held it, wrongly) that overloading a subclass method to return a
  non-`Self` type is a Liskov violation the checker rejects. **`ty` accepts it** — a base-typed
  caller gets the base type, a concrete-typed caller gets the precise overload type, subclasses
  inherit the overloads — and it is **sound**: the overload return equals what the impl returns at
  runtime (unlike the old `-> Self` cast, which lied). So base.py stayed untouched.
- **Impl return is `MultiVectorBase`, not `Self` or `G_n`.** An overloaded impl's return must be a
  supertype of *every* overload return. The overload returns (`Rotor`, `Bivector`, `Scalar`,
  `Vector`, `G`) are **all siblings under `MultiVectorBase`** — none subclasses another or the
  full class `G_n`. So `MultiVectorBase` is the only common supertype. `-> G` was tried and
  fails (a `Rotor` is not a `G`). The old `-> Self` was internally inconsistent with its own
  overloads (claimed `Vector` while an overload said `Rotor`).
- **Not declaring the operator `-> G_n`** (a single wide return instead of overloads):
  **dominated.** Runtime returns a `Rotor` (not a `G_n` subclass), so it still needs a cast, and
  `G_n` exposes coefficients the real `Rotor` lacks (type-checks, crashes at runtime). Overloads
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
  `ty` too. **pyright** was mvp's emacs LSP only and was **removed 2026-08-23** (switched to a
  `ty server` LSP — `tasks/archive/2026/08/23/switch-typechecker-pyright-to-ty.md` in
  `github.com/billsix/modelviewprojection`); it never reached either gate. A one-off pyright check surfaced `reportInconsistentOverload` (the impl's `-> Self` inconsistent with its
  overloads) — that is what motivated the `-> MultiVectorBase` broadening (an honesty improvement
  even for `ty`, which is lenient about it). pyright would also flag `reportOverlappingOverload`
  on the catch-all overlapping the specific overloads; **not chased**, since we are `ty`-only.
- **What precise types unlock for consumers:** direct `.coeff_e_12` field access instead of the
  base `.coefficient(blade)` reader — the reader was the workaround forced by the old mistype
  (`.coeff_e_12` was type-rejected on a mis-typed `Vector`). See
  `tasks/archive/2026/07/22/precise-product-types-coefficient-cleanup.md` in
  `github.com/billsix/modelviewprojection`.
- **The odd-type gap is not a prerequisite.** In 𝒢₃ only the *raw full geometric product* of an
  odd-producing pair (e.g. `Rotor * Vector`, `Vector * Bivector`) widens to `G` for lack of a
  registered `{1,3}` type; the operations actually reached for are already precise
  (`Rotor.sandwich(x) -> type(x)`, `Vector.inner_product(Bivector) -> Vector`,
  `Vector ^ Bivector -> Trivector`). Left at `-> G`; see `tasks/model-odd-graded-type.md`.

## `ScalarN` as a product lhs (done 2026-07-23)

`Scalar` now carry the same overloads as the other graded types — so
`Scalar * Vector → Vector`, `Scalar * Bivector → Bivector`, `Scalar * Trivector →
Trivector`, `Scalar + Bivector → Rotor`, `Scalar + Vector → G`, and `Scalar.inner_product(X)
→ Scalar` (scalar·X ≡ 0 under the Hestenes dot). **How:** `generate_scalar`'s bespoke hand-built
`__mul__` / `_geometric_product` / `outer_product` / `inner_product` / `__add__` / `__sub__` bodies
(which returned `-> Self` with an unsound `cast(Self, coeff * rhs)` on the general arm) were replaced
by the **same `product_overload_stubs(...)` + `dispatch_method(...)`** the graded generator uses —
so ScalarN is no longer a special case. The impls return `-> MultiVectorBase`, construct the resolved
concrete type per rhs, and the `case _` **coerces a foreign/`Gn` operand to `G_n`** (the old
hand-built body returned a bare `Gn` for a `Gn` rhs — now `Scalar * Gn → G`, matching the
catch-all overload). Runtime is value-identical (conformance green); the changed return *types*
(`inner_product` now builds `Scalar(0)` not a coerced `Gn`; `+`/`-` coerce to `G`) are covered by
`assert_type` + runtime guards in `tests/test_operator_typing.py`
(`test_scalar_lhs_static_types` / `…_runtime_types_and_values`). The **reflected** ops
(`__rmul__`/`__radd__`/`__rsub__`) were left as-is — their overloads are the separate
`tasks/archive/2026/07/23/reflected-operator-typing-overloads.md`. See
`tasks/archive/2026/07/23/scalar-product-typing-overloads.md`.

## Aliases & ScalarN contractions (done 2026-08-02)

The two remaining gaps below are now closed. A new generator helper
**`alias_dispatch(alias, target, …)`** (`tools/gen_specialized.py`) emits the
precise `@overload` stubs (resolved the same as `target`) plus a one-line impl
that *delegates* to `target` and returns `MultiVectorBase` — for the
methods/operators that are *defined as* a delegation of a dispatched product. The
graded generator's inline `__xor__`/`__lt__`/`__gt__` blocks were refactored onto
it (AST-identical output — verified) and it now also emits the additions:

- **`wedge` / `dot` aliases** — were inherited from `base` as `-> Self`, so
  `Vector.wedge(Vector)` mistyped as `Vector` (want `Bivector`) and
  `.dot` as `Vector` (want `Scalar`). Now overridden on **every** graded type
  (Vector/Bivector/Trivector/Rotor **and** ScalarN): `wedge → outer_product`,
  `dot → inner_product`, typed precisely.
- **`ScalarN` operators** — `generate_scalar` emitted **none** of
  `__xor__`/`__lt__`/`__gt__`/`wedge`/`dot` and no contraction dispatch, so all
  were inherited `-> Self` (`Scalar < Vector` mistyped as `Scalar`; `Scalar ^
  Vector` as `Scalar | Vector`). ScalarN now carries `left_contraction` /
  `right_contraction` as full `dispatch_method`s and `__xor__` / `wedge` / `dot` /
  `__lt__` / `__gt__` as `alias_dispatch` — matching the other graded types.
  (`__xor__` was not in the original "not yet done" list but was the same gap,
  fixed for consistency.)

Now precise (guarded by `assert_type` in `tests/test_operator_typing.py`
`test_alias_and_scalar_contraction_static_types` + a runtime companion):
`v.wedge(v) → Bivector`, `v.dot(v) → Scalar`, `s ^ v → Vector`,
`s.wedge(v) → Vector`, `s.dot(v) → Scalar`, `s < v → Vector`,
`s > v → Scalar`; 𝒢₃ likewise. Runtime was always correct (conformance green) —
a static-typing fix. The full class `G_n` keeps its inherited `-> Self` aliases,
already correct (`G.wedge(G) → G`).

## Remaining candidates for the same treatment (analysis 2026-08-03)

A survey of `base.py`'s return annotations for methods still returning the abstract type where
a concrete one is statically knowable. Full analysis + rationale in
`tasks/precise-typing-remaining-methods.md`.

- **`project` / `reject` / `reflect` — DONE 2026-08-03, extended to any blade grade 2026-08-22.**
  The function-returning family were `ComposableFunction[MultiVectorBase]` /
  `InvertibleFunction[MultiVectorBase]`; now, on the **vector** graded types, they resolve to
  `ComposableFunction[Vector_n]` / `InvertibleFunction[Vector_n]` (`reflect` uses
  `InvertibleFunction`, being an involution) when projecting/rejecting/reflecting onto a
  **grade-pure blade of any supported grade** — because a *vector* onto a blade stays a vector.
  `project` emits a precise overload for **every** grade-pure blade type (Vector, Bivector,
  Trivector, FourVector, … up to the algebra's pseudoscalar); `reject`/`reflect` emit them only
  **up to Bivector** (grade 3+ still raises at runtime — the separate
  `tasks/generalize-reject-reflect-higher-grade.md`), with the `MultiVectorBase | Sequence[…]`
  catch-all after. So in 𝒢₃, `Vector.project(onto=Bivector)(v)` / `onto=Trivector` are statically
  `Vector` (verified via `ty reveal_type`), not `MultiVectorBase`.
  Mechanism: the generator helper **`transform_factory_overrides(self_spec, onto_types, method,
  param_name, wrapper, max_onto_grade)`** emits one `@typing.overload @classmethod` stub per
  grade-pure blade type with `grade <= max_onto_grade`, then the catch-all, then a one-line
  `return super().<method>(...)` impl (runtime unchanged — base does the work), injected only on
  vector specs (`spec.name.startswith("Vector")`), exactly like the `exp`-on-Bivector /
  `sandwich`-on-Rotor grade-specific injections. **`base.py` needed no signature change** (inside
  base, `cls` is generic `Self`). **One soundness fix in `base.py`:** `base.reject` was NOT
  narrowing its result to the operand grade (in 3D it returned the raw `G` container — grade-1
  data, higher coeffs identically zero), so a `Vector` overload would have been unsound;
  `reject`'s inner `r` now narrows to grade via
  `type(value).from_blade_dict(rejected.r_vector_part(1)…)`, mirroring `project` and matching the
  CLAUDE.md Architecture claim ("project/reject are grade-preserving"). Guarded by `assert_type`
  (`Vector`/`Vector.project`/`reject`/`reflect → Vector_n`, 2D+3D). Origin: Bill noticing
  `proj_b(a)` of a vector is a `Vector`, not `MultiVectorBase`.
- **The project/reject/reflect *pass-through* instance methods (2026-08-26)** —
  `projected_onto(onto)` / `rejected_away_from(away_from)` / `reflected_across(across)` on
  `MultiVectorBase`, value-returning sugar for `factory(arg)(self)` (the factories stay for
  compose/label/pipeline). Same precision via the **instance-method analog**
  **`passthrough_method_overrides(self_spec, onto_types, method, param_name, max_onto_grade)`**: one
  `@typing.overload` per grade-pure blade type up to the same caps (project any grade; reject/reflect
  ≤ Bivector), then the `MultiVectorBase` catch-all, then a `return super().<method>(...)` impl —
  `self` not `cls`, and the return is the plain **value** type (`Vector_n` / `MultiVectorBase`), NOT a
  `ComposableFunction` wrapper, so the impl returns `MultiVectorBase` directly (no invariance issue,
  unlike the factory case's `wrapper[Any]` impl). Names mirror each factory's keyword; guarded by
  `assert_type`. — `tasks/archive/2026/08/26/precise-typing-remaining-methods.md`.
- **`rotor_from_vectors`** — `-> MultiVectorBase`, but always builds scalar + bivector = a rotor,
  so `Vector_n.rotor_from_vectors → Rotor_n` (mirrors `Bivector_n.exp() → Rotor_n`). **DONE
  2026-08-15**, with the plane helpers: **`bivector_from_vectors` / `i` → `Bivector_n`** and
  **`.i()` / `plane_of_rotation` → `Bivector_n`** (all narrow to the algebra's grade-2 type; gated
  on n≥2, since 𝒢₁ has no bivector/rotor). Two new generator helpers do it:
  **`classmethod_narrowing_overloads`** (precise + `MultiVectorBase` catch-all `@overload`s that
  discriminate on the `Vector` param type — sound because the wedge/rotor of two *same-algebra*
  vectors is that algebra's `Bivector`/`Rotor` at runtime) and **`inherited_classmethod_narrowing`**
  (those stubs + a `super()`-delegating impl, for the base-inherited `bivector_from_vectors` /
  `rotor_from_vectors`). The `inverse` `-> Self` spot-check also landed (confirmed it returns the
  concrete type, not `Gn`). Caveat: this does **not** help `transforms.plane_rotation` (generic over
  `V` — a concrete-returning classmethod would widen it); the `i`-first `bivector_rotation` builder
  is operand-agnostic for the same reason — see `design-decisions.md`.
- **`identity`** — `InvertibleFunction[MultiVectorBase]`; could be generic `InvertibleFunction[T]`.
  Minor.
- **Not this mechanism:** `transforms.projection_rotation`/`rotor_rotation`/`plane_rotation` are
  free functions (generics, not graded overloads); the `-> Self` grade-preservers
  (`reverse`/`normalize`/`simplified`/`expanded`/`inverse`) are already precise on the `@final`
  types; `outer_product_of_vectors` genuinely widens (variadic grade).

## High-dimension ty findings (g4/g5) — why generated typing must be verified in full context

Generating 𝒢₄/𝒢₅ for the first time (2026-08-22) surfaced **179 ty diagnostics in g4, zero in
g1–g3** — but the flagged code was *byte-identical* to g1–g3. Root cause: **ty's checking is
incomplete at smaller module scale** and only catches several genuinely-imprecise (but latent)
patterns once the module is ~3× larger (g4 = 529 KB vs g3 = 166 KB). g3 "passing" was ty missing
them, not the code being sound. All were fixed with real changes (no suppressions); each also made
g1–g3 more sound. Work record + full tally: `tasks/generator-ty-clean-high-dim.md`.

**Durable rules that came out of it:**

- **`@final` generated types must annotate returns with the CONCRETE class name, not `typing.Self`,
  wherever the body constructs concretely** (`return G(...)`). ty does not reliably collapse `Self`
  to the class even under `@final` on a large module, so `return G(...)` vs `-> typing.Self` is
  flagged. `-> G` matches exactly, and a `cast(Self, …)` branch still matches (`Self <: G`). Applied
  via `self_ann = name_ref(<class>)` in all three generators (scalar/full/graded). (This *finishes*
  the concrete-construction work of `investigate-final-full-classes`.)
- **You cannot covariantly narrow an INVARIANT generic in an overload.** `ComposableFunction`/
  `InvertibleFunction` are invariant (`func: Callable[[V], V]` uses V as input *and* output), so a
  precise overload `-> ComposableFunction[Vector]` is NOT assignable to an impl `->
  ComposableFunction[MultiVectorBase]` (unlike the product overloads, whose concrete multivector
  returns *are* covariant subtypes of `MultiVectorBase`). Fix: the overloaded impl returns the
  **gradual** `wrapper[Any]` (impl is never called directly; overloads keep the precise type).
- **`_coerce` is generic** `_coerce[T: MultiVectorBase](x, cls: type[T]) -> T` (was
  `-> MultiVectorBase`), so `_coerce(self, G)` returns `G`.
- **`base.__radd__` param is `Coef`, not `MultiVectorBase | Coef`** — `__radd__` only ever receives a
  bare number (a multivector left operand uses its own `__add__`), which also matches the generated
  override (Liskov-clean).
- **`cast_coef` skips a bare field, a negated field, AND a single `field ** constant`** — all are
  already `Coef`; casting warns (`redundant-cast`). Multi-term sympy *sums* still cast.

**Verification method (important): ty and ruff both respect `.gitignore`, and the generated
`g*.py` are gitignored, so the dev gate `ty check src` / `ruff check src` SKIP every generated
module** — they only check the hand-written code. To check generated-module typing you must pass the
files **explicitly and together** (full context):
`ty check src/gacalc/g1.py … g5.py gn.py base.py functions.py transforms.py nbplotutils.py`. A
**single-file** `ty check src/gacalc/g3.py` is NOT valid — it gives ~119 *isolation* false positives
(unresolved cross-module types). This full-context check is what should be wired into the opt-in
full-dim gate (`make test-all-dims`), since the dev gate cannot see generated-module regressions.
`.gitignore` uses the glob `/src/gacalc/g[0-9]*.py` (covers g1..g10+, spares the tracked `gn.py`).
