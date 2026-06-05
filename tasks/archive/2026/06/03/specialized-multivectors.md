# Specialized, performant MultiVector for 2D and 3D

Status: **COMPLETE** — Phases 0–5 done · Created 2026-06-04 · Archived 2026-06-04

## Goal

Make the geometric product (and the whole `MultiVector` API) much faster in 2D and 3D
without losing the general N-dimensional implementation, by introducing an abstract base
class and concrete representations. Specialized 2D/3D classes use fixed, named-field
dataclasses whose `__mul__` is **code-generated from the existing symbolic product**, so the
fast path stays provably consistent with the reference implementation.

## Decisions (settled 2026-06-04)

1. **Coefficient policy: symbolic everywhere; eager simplify on `Gn` only, lazy on `G2`/`G3`.**
   Keep `sympy` coefficients in all representations. **`Gn` keeps its eager `__post_init__`
   simplify and stays as-is** — it is allowed to be slow; we don't optimize it. The specialized
   **`G2`/`G3` do NOT eager-simplify**: they get speed from a closed-form `__mul__` and simplify
   only **lazily, on display / equality / on demand**. Consequence: the existing `Gn` tests are
   untouched (they still rely on eager-simplified exact `==`); only the `G2`/`G3` tests need
   simplify-aware comparison (see decision 4). Profiling (below) shows eager simplify is ~100% of
   `Gn`'s cost, so this is exactly the knob that separates "slow `Gn`, fine" from "fast `G2`/`G3`".
2. **Specialized shape: named-field dataclasses via codegen.** Classes are named after Hestenes'
   notation 𝒢ₙ (the geometric algebra of n-dimensional Euclidean space ℝⁿ): **`G2`** = 𝒢₂ (the
   plane, 2² = 4 blades), **`G3`** = 𝒢₃ (3D space, 2³ = 8 blades), and **`Gn`** = 𝒢ₙ for the
   general implementation. Field names mirror the existing `e_n` constants: scalar is `scalar`,
   vectors are `e_1, e_2, e_3`, blades are `e_12, e_13, e_23, e_123`. So `G2` =
   `{scalar, e_1, e_2, e_12}`, `G3` = `{scalar, e_1, e_2, e_3, e_12, e_13, e_23, e_123}`. A
   committed generator script (in `tools/`) emits a **static, human-readable `.py`** for these
   classes (their fields and `__mul__`); we re-run it by hand when the algebra changes. No runtime
   `lambdify`/`exec`.

   *Sub-task:* rename the existing dimension parameter from `grade`/`g` to `n` (or `dim`) in
   `bases`, `unit_pseudoscalar`, `symbolic_multivector`, `dual`, etc. "Grade" already means a
   blade's grade in GA (scalar = 0, vector = 1, bivector = 2); that parameter is really the
   dimension n of 𝒢ₙ, and the `G2/G3/Gn` naming makes the confusion visible.
3. **Each dimension gets its own basis constants.** Provide dimension-specific basis constants /
   constructors for 2D and 3D (separate from the general `e_1..e_n`). A general representation and
   a specialized one should **never interact**; if they ever do, the result **coerces to the
   general (blade-dict) representation** rather than raising.
4. **Lazy-simplify test policy (G2/G3 only).** Because `G2`/`G3` don't eager-simplify, their
   coefficients aren't canonical, so `G2`/`G3` equality (`__eq__`/`is_close`) and the conformance/
   equivalence tests must **simplify before comparing**. The existing `tests/test_multivector.py`
   (which exercise `Gn`) keep relying on eager simplify and are **unchanged**.

(Considered and rejected for now: float fast-path — would be fastest but needs tolerance
equality and breaks exact symbolic tests; single Cayley-table `DenseEuclidean(n)` class —
DRYer/faster but no named-component API.)

## Why this is the right structure (design notes)

The abstraction boundary is **"touches the raw representation"**, NOT "transitively depends on
`__mul__`". Almost the entire class transitively uses `__mul__`, but only through the public
operator, so Python dispatch handles it — those methods stay in the ABC.

- **Concrete-subclass primitives** (touch the fields/dict directly, reimplemented per representation):
  `__mul__`, `__add__`, `__eq__`, `r_vector_part`, `scalar_part`, `grades`/`max_grade`,
  `__iter__`, `_repr_latex_`, and constructors (`from_scalar`, `zero`/`one`, blade access).
- **ABC methods** (written purely against the primitives, shared by ALL representations):
  `__sub__`, `__neg__`, `__abs__`/`magnitude`/`magnitude_squared`/`normalize`, `inner_product`,
  `dot`, `outer_product`, `wedge`/`__xor__`/`outer_product_of_vectors`, `reverse`, `inverse`,
  `dual`, `even_part`/`odd_part`, `cosine`, `component`, all `is_*` predicates, `is_orthogonal_to`,
  `is_parallel_to`, `project`, `reject`, `reflect`, `identity`, `rotate`, `is_close`.

Required enabler: the ABC methods currently build results via module globals (`zero`, `one`)
and `MultiVector({...})`. To stay polymorphic they must build results of `self`'s concrete
type. Add a small **construction protocol** on the ABC:
`cls.zero()`, `cls.one()`, `cls.from_scalar()`, `cls.from_blade_dict()`, and replace
`start=zero` with `start=type(self).zero()` etc. This polymorphism refactor is the bulk of the work.

**Canonical interchange.** Define `to_blade_dict()` / `from_blade_dict()` on every class as the
common interchange format. Equality and any cross-representation comparison go through it, so a
2D value and a general value representing the same multivector compare equal. This is what makes
the conformance test suite possible. Per decision 3, mixed general/specialized operations
coerce to the general representation via this interchange (specialized values are not expected to
mix with general ones in normal use, but if they do, general wins).

## Naming & terminology (docstring-ready)

Use Hestenes' script-G notation 𝒢ₙ in the class docstrings. Note the algebra-vs-element
distinction: **𝒢ₙ is the algebra; an instance of the class is an element of 𝒢ₙ (a multivector).**
The class is named after its algebra as a common shorthand. Drop these in verbatim:

```python
class Gn:
    """An element (multivector) of 𝒢ₙ, the geometric algebra of n-dimensional
    Euclidean space ℝⁿ (Hestenes' notation).

    𝒢ₙ has 2ⁿ basis blades. This is the general, dimension-agnostic
    representation; G2 and G3 are specialized, faster representations of 𝒢₂ and 𝒢₃.

    Terminology: 𝒢ₙ denotes the *algebra*; an instance of this class is an
    *element of* 𝒢ₙ. The class is named after its algebra as a shorthand.
    """


class G2:
    """An element (multivector) of 𝒢₂, the geometric algebra of the Euclidean
    plane ℝ² (Hestenes' notation).

    𝒢₂ has 2² = 4 basis blades, stored as named fields:
        scalar          grade 0 (scalar)
        e_1, e_2        grade 1 (vectors)
        e_12            grade 2 (bivector / pseudoscalar)

    A specialized, performant representation of 𝒢₂; see Gn for the general 𝒢ₙ case.
    """


class G3:
    """An element (multivector) of 𝒢₃, the geometric algebra of 3D Euclidean
    space ℝ³ (Hestenes' "algebra of physical space"; the Pauli algebra).

    𝒢₃ has 2³ = 8 basis blades, stored as named fields:
        scalar                  grade 0 (scalar)
        e_1, e_2, e_3           grade 1 (vectors)
        e_12, e_13, e_23        grade 2 (bivectors)
        e_123                   grade 3 (trivector / pseudoscalar)

    A specialized, performant representation of 𝒢₃; see Gn for the general 𝒢ₙ case.
    """
```

## Codegen approach

`MultiVector.symbolic_multivector(grade=g, prefix=...)` already builds a fully general symbolic
multivector; multiplying two and reading `coefficient_of_blade` yields the closed-form bilinear
formula for each output blade. The generator (`tools/gen_specialized.py`, name TBD):

1. For n in {2, 3} (i.e. 𝒢₂ and 𝒢₃): build two symbolic multivectors with distinct prefixes.
2. Compute their product with the **general** `Gn` implementation.
3. For each output blade, take the coefficient expression; run `sympy.cse` across all output
   components for common-subexpression elimination.
4. Emit a static dataclass (`G2`, `G3`) with named fields + a `__mul__` (and any other
   representation primitives that are cheap to specialize) into a committed `.py`.

This keeps generated code reviewable, type-checkable, and dependency-free at import time.

## Testing strategy

- **Conformance suite**: parametrize one test body over `[Gn, G2, G3]` and assert all
  implementations agree (via the blade-dict interchange) for products, inner/outer products,
  reverse, inverse, dual, projection/reflection/rotation, etc. This is how the ABC contract /
  "abstract methods" get tested uniformly.
- **Equivalence test**: for symbolic inputs, assert `G2`/`G3` product == `Gn` product (comparison
  simplifies, since `G2`/`G3` aren't pre-simplified — decision 4).
- The existing `tests/test_multivector.py` (which exercise `Gn`) stay **unchanged** — `Gn` keeps
  eager simplify, so its exact `==` still holds.
- Add a micro-benchmark (see Baseline) and record `G2`/`G3` before/after numbers here.

## Baseline measurements (2026-06-04)

Wall-clock per operation (averaged; Python 3.14, sympy 1.14):

| Operation | Time |
|-----------|------|
| numeric 3D geometric product (floats) | **0.80 ms** |
| symbolic 2D vector × vector | 54.86 ms |
| symbolic 3D vector × vector | 239.33 ms |
| symbolic 3D wedge | 305.40 ms |
| symbolic 3D inverse | 237.23 ms |
| full 𝒢₂ symbolic × (4×4 blades) | 732 ms |
| full 𝒢₃ symbolic × (8×8 blades) | **10,548 ms** (~10.5 s) |

`cProfile` of one full 𝒢₃ symbolic product (28 s under the profiler):
- `__mul__` cumulative = 28.116 s (100%).
- **Of that, `__post_init__` = 28.098 s and `sympy.simplify` (548 calls) = 28.091 s ≈ 100%.**
- One 𝒢₃ product constructs **128 MultiVectors**, each running `simplify` on its coefficients.
- The numeric path (0.80 ms) shows dict/object/structural overhead is negligible — `sympy.simplify`
  is ~100% of the symbolic cost and ~300× the entire numeric pipeline.

**Conclusions that steer the plan:**
- Eager `sympy.simplify` is ~100% of `Gn`'s cost. We deliberately leave it in `Gn` (slow is fine).
- `G2`/`G3` get their speed from two stacked effects: (a) a closed-form `__mul__` that builds a
  handful of components instead of 128 intermediate `MultiVector`s, and (b) **no eager simplify**
  (lazy on display/equality). Without (b), `G2`/`G3` would still pay simplify on every result.
- The dict representation itself is not the problem; do not over-invest in micro-optimizing it.

## Step plan

0. **Measure baseline** — `cProfile` a symbolic 3D product; confirm `sympy.simplify` dominates.
   **DONE — see Baseline above.** (`Gn` is ~100% eager simplify; we leave it alone.)
1. **Introduce the ABC + `Gn`.** Lift representation-independent methods, define the construction
   protocol and `to/from_blade_dict`; make the current dict class the concrete `Gn` subclass —
   **keeping its eager `__post_init__` simplify unchanged.** Rename the `grade`/`g` dimension param
   to `n`. Existing tests stay green untouched. **DONE — see "Phase 1 result" below.**
2. **Codegen `G2`/`G3`** via `tools/gen_specialized.py` into a committed file. These classes have a
   closed-form `__mul__` and **no eager simplify** — they simplify lazily on display/equality.
   **DONE — see "Phase 2 result" below.**
3. **Conformance + equivalence tests** over `[Gn, G2, G3]`. `G2`/`G3` comparisons simplify before
   asserting (decision 4). **DONE — see "Phase 3 result" below.**
4. **Benchmark `G2`/`G3` vs `Gn`**; record results here. Decide whether to make `e_1 * e_2` etc.
   return specialized types by default in low dimensions (API question — see open questions).
   **DONE — benchmarks above; API decisions resolved/implemented (see API section).**
5. **Update `CLAUDE.md`** to reflect the shipped result: the new `Gn`/`G2`/`G3` architecture and
   ABC, the 𝒢ₙ terminology, the eager-(`Gn`)/lazy-(`G2`/`G3`) simplify policy, the `grade`→`n`
   rename, the `tools/` generator + committed generated module, and the before/after benchmark
   numbers. Reframe Assessment item #1 from "fix globally" to "intentionally scoped to `Gn`".
   Then **archive this task** (`tasks/archive/specialized-multivectors.md`).
   **DONE — `CLAUDE.md` rewritten for the new layout/architecture/codegen/benchmarks; item #1
   reframed as resolved-by-design; repo-hygiene note updated (README now exists). Task archived.**

(Note: there is no longer a global "remove eager simplify" phase — eager simplify is a `Gn`
property we keep; lazy simplify is a `G2`/`G3` property baked in at codegen.)

## Phase 1 result (2026-06-04)

Done in `src/geometricalgebra/multivector.py`:
- New ABC **`AbstractMultiVector`** holds all representation-independent methods, written against a
  tiny interchange protocol so subclasses only need to implement the primitives.
- **Abstract primitives** a concrete representation must supply: `from_blade_dict` (classmethod),
  `to_blade_dict`, `_geometric_product` (the multivector×multivector core), plus dataclass `__eq__`.
  Everything else (`__add__`, `__mul__` scalar-dispatch, `r_vector_part`, `scalar_part`, `grades`,
  `__iter__`, `reverse`, `inner/outer_product`, `dual`, `project/reject/reflect/rotate`,
  `_repr_latex_`, `is_close`, …) is shared and constructs results via `type(self).from_blade_dict`
  / `type(self).zero()` so it stays polymorphic.
- **`Gn(AbstractMultiVector)`** is the concrete general representation (the old dict class), keeping
  its eager `__post_init__` `sympy.simplify` unchanged.
- **`MultiVector = Gn`** backward-compat alias (so `MultiVector({...})`, `MultiVector.unit_pseudoscalar`,
  etc. keep working). `MultiVectorFn` now typed over `AbstractMultiVector`.
- Renamed dimension param `grade`/`g` → `n` on `unit_pseudoscalar`, `bases`, `symbolic_multivector`,
  `unit_pseudoscalar_squared`, `dual`.
- Shared methods annotated `-> typing.Self` so a `Gn` op returns `Gn` (a few `typing.cast`s on
  `sum()`/product results where the checker can't infer it).

Verification: **23/23 tests pass**; `ruff check` clean; `ruff format` clean; **`ty check src` and
`ty check tests` both pass** (baseline was 0 ty errors — parity preserved).

Edits outside `multivector.py` (all annotation/rename only, no logic change):
- `tests/test_multivector.py`: 2 lines `dual(g=…)` → `dual(n=…)` (the rename); 2 lines dropped a
  now-inaccurate `: MultiVector` annotation on `project`/`reject` results (they're representation-
  generic → `AbstractMultiVector`).
- `notebooks/displaymv.py`: `symbolic_multivector(grade=…)` → `n=` (notebook, not under test).

Note for Phase 2: the shared methods route construction through `to_blade_dict`/`from_blade_dict`,
which is fine for correctness but is the slow general path. `G2`/`G3` should override the hot ones
(`_geometric_product` is the main one) so they don't round-trip through the dict.

## Module layout (2026-06-04, after Phase 2)

Split one-class-per-file so a newcomer can import just the algebra they need
(`from geometricalgebra.g2 import G2`). No import cycles: each module imports only "downward".

- **`base.py`** — `AbstractMultiVector` (the abstract base) + `BladeCoef` / `MultiVectorFn`.
- **`gn.py`** — `Gn` + `BladeDictionaryEntry` + the `e_1..e_10` / `zero` / `one` constants + the
  `InvertibleFunction` / transform helpers + the `MultiVector = Gn` alias. Imports from `base`.
- **`g1.py` / `g2.py` / `g3.py`** — one generated concrete class each (𝒢₁/𝒢₂/𝒢₃). Import from
  `base` + `gn`. (`G1` added as the simplest teaching on-ramp.)
- **`multivector.py`** — now a thin **umbrella facade** that re-exports everything previously
  importable from it (via explicit imports + `__all__`), so existing
  `from geometricalgebra.multivector import ...` keeps working. Nothing internal imports the facade,
  so importing `gn`/`g1`/`g2`/`g3` directly never triggers a cycle.

(There is no `specialized.py` — that name was replaced by the per-algebra modules.)

## Phase 2 result (2026-06-04)

- **`tools/gen_specialized.py`** generates **`g1.py` / `g2.py` / `g3.py`** (committed), one class
  each. It builds two symbolic `Gn` multivectors, multiplies them with the
  reference `Gn` product, runs `sympy.cse`, and emits each closed-form output component. Long sums
  are wrapped term-by-term so the output stays under the 88-col limit and readable. The symbolic
  operands are rendered straight back to attribute access (`self.e_1 * rhs.e_12`) via a
  word-boundary regex, so there are **no pointless alias locals** in the generated product.
- Each class is a `@dataclasses.dataclass(eq=False)` with named fields (`scalar`, `e_1`, …) and
  implements the four primitives: `from_blade_dict`, `to_blade_dict`, a closed-form
  `_geometric_product`, and a lazy-simplify `__eq__` (simplifies the per-blade difference; works
  cross-representation via `to_blade_dict`). **No eager simplify** anywhere.
- Cross-type guard: `G2 * <non-G2>` (or G3) coerces both operands to `Gn` and returns the general
  result (per decision 3).
- Everything else (`reverse`, `inverse`, `dual`, `inner/outer_product`, `project`, …) is inherited
  from `AbstractMultiVector` and works on `G2`/`G3` unchanged, returning the specialized type.

Verification: `ruff check` clean, `ruff format` clean, `ty check src` clean; the existing 23 `Gn`
tests still pass. Correctness was spot-checked: `G2`/`G3` symbolic products equal the `Gn` product
(via simplify), cross-type `==` works, pseudoscalar squares and reverse/inverse behave. **Formal
conformance tests are Phase 3.**

Preliminary benchmark (regenerate-and-time; full numbers in Phase 4):

| Operation | `Gn` | `G2`/`G3` | speedup |
|-----------|------|-----------|---------|
| full 𝒢₃ symbolic product | 10,587 ms | **1.25 ms** | ~8,500× |
| numeric 3D vector product | 3.47 ms | **0.52 ms** | ~6.7× |

The symbolic win is enormous because `Gn` eagerly simplifies 128 intermediate constructions while
`G3` is one closed-form pass with lazy simplify.

## Open questions (resolved 2026-06-04)

- ~~Field names~~ → `scalar`, `e_1/e_2/e_3`, `e_12/e_13/e_23/e_123` (decision 2).
- ~~Module constants / mixed-type~~ → each dimension gets its own basis constants; general and
  specialized never interact, but if they do the result coerces to the general representation
  (decision 3).
- ~~Lazy-simplify vs existing tests~~ → tests will simplify within their assertions (decision 4).
- ~~Generator home~~ → `tools/` (generated output committed under `src/geometricalgebra/`).

Still to confirm during implementation:
- ~~Generated module / generator path~~ → one file per algebra (`g1.py`/`g2.py`/`g3.py`) generated
  by `tools/gen_specialized.py` (done in Phase 2 + module split).

## Phase 3 result (2026-06-04)

- **`tests/test_conformance.py`** — a parametrized suite over `(dimension, implementation)` for
  every `(n, cls)` in `{1: [Gn, G1], 2: [Gn, G2], 3: [Gn, G3]}` (Gn included as a baseline).
  Inputs are built in `Gn`, converted to the implementation under test via `to(cls, g) =
  cls.from_blade_dict(g.to_blade_dict())`, and the result compared back to the `Gn` result through
  the simplify-aware `__eq__`.
- Coverage: geometric product (numeric all-blades for every dim + **symbolic** full product for
  n=1,2 and symbolic vector product for n=3, the "provably consistent" check), add/sub/neg, scalar
  multiplication, `r_vector_part`/`scalar_part`/`grades`, even/odd part, reverse, dual, inner/outer
  product, dot/wedge, `magnitude_squared`/inverse, project/reject (+ reconstruct), reflect, rotate
  (n≥2), **result-type preservation** (`G2*G2` is `G2`, etc.), **cross-type coercion** (`G2 * Gn`
  → `Gn`), and `is_close`.
- Result: **89 conformance tests; full suite 112 passing in ~20 s.** `ruff` clean, `ty check src`
  and `ty check tests` clean.
- API note: the tests use the blade-dict interchange for construction, so **per-dimension basis
  constants (API topic #1) were not needed and remain deferred**; the dimension-fixed-method
  question (#2) likewise didn't block the tests (`dual(n)` is called with the right `n`).

## Phase 4 result — benchmarks (2026-06-04)

`tools/bench.py` (committed, reproducible: `python tools/bench.py`). `Gn` vs the specialized class:

| operation | `Gn` | specialized | speedup |
|-----------|------|-------------|---------|
| G1 numeric full product | 0.129 ms | 0.008 ms | 15× |
| G2 numeric full product | 0.650 ms | 0.031 ms | 21× |
| G3 numeric full product | 4.355 ms | 0.130 ms | 34× |
| G1 reverse | 0.153 ms | 0.057 ms | 2.7× |
| G2 reverse | 0.283 ms | 0.132 ms | 2.1× |
| G3 reverse | 0.563 ms | 0.412 ms | 1.4× |
| **G1 symbolic full product** | 51.9 ms | 0.016 ms | **3,157×** |
| **G2 symbolic full product** | 725.6 ms | 0.084 ms | **8,660×** |
| **G3 symbolic full product** | 10,529 ms | 0.396 ms | **26,578×** |

Notes:
- **Symbolic** products are where the specialization pays off most (3 000–26 000×): `Gn`
  eager-simplifies every intermediate construction; the specialized closed form does one pass with
  no simplify.
- **Numeric** products are 15–34× faster (closed form + no dict/object churn).
- `reverse` and other inherited derived ops gain less (1.4–2.7×) because they currently route
  construction through the `to_blade_dict`/`from_blade_dict` interchange. If we want those faster
  too, the specialized classes could override the hot ones (`r_vector_part`, `reverse`, `__add__`)
  — noted as a possible follow-up, not done here.

## API topics — resolved in Phase 4 (2026-06-04)

1. **Per-dimension basis constants** → **DONE (full basis).** The generator emits, into each
   `g1.py`/`g2.py`/`g3.py`, module-level constants of that module's own type: `zero`, `one`, and a
   named constant for every basis blade (`e_1`, `e_2`, …, and the pseudoscalar `e_12`/`e_123`). So
   `from geometricalgebra.g2 import G2, e_1, e_2` then `3 * e_1 + 4 * e_2` builds a `G2`. Putting
   them in each module disambiguates 2D vs 3D `e_1`. (`gn.py` keeps its own `Gn`-typed `e_1..e_10`.)

2. **Dimension-fixed methods** → **DONE (n implicit).** `G1`/`G2`/`G3` carry a
   `DIMENSION: ClassVar[int]` and override `dual`, `unit_pseudoscalar`, `unit_pseudoscalar_squared`,
   `bases`, `symbolic_multivector` so `n` defaults to the class's dimension (`g2.dual()` ==
   `g2.dual(2)`, `G2.unit_pseudoscalar()` == `e_12`). An explicit `n` is still accepted, so the
   conformance tests and any `dual(n)` calls keep working.

3. **Default return type / interop** → **RESOLVED by #1.** Each module's constants are of that
   module's type, so `g2.e_1 * g2.e_2` is a `G2` naturally — no magic coercion in `gn`, and no
   circular imports. The `gn` constants stay `Gn`. Mixing a specialized value with a `Gn` value
   **coerces to `Gn`** (decision 3), verified by `test_mixing_with_gn_coerces_to_gn`.

4. **The `MultiVector` alias** → kept as a back-compat alias for `Gn`; docs/examples will steer
   newcomers to `Gn`/`G2`/`G3` (to be reflected in `CLAUDE.md` in Phase 5).

5. **Equality with raw scalars** → **decided: NO change.** Equality stays multivector-vs-multivector
   only (compare scalars via `.scalar_part()`); `is_close` is the float-tolerant comparison.

6. **Display simplification** → **deferred (not done).** `_repr_latex_` still renders raw,
   lazily-unsimplified coefficients (sympy auto-simplifies trivially). Left as a possible follow-up;
   does not affect equality or correctness.

7. **Per-module `__all__`** → **DONE** for `g1`/`g2`/`g3` (class + `zero`/`one` + basis constants).
   `gn.py` / `base.py` left without an explicit `__all__` for now (the facade `multivector.py`
   already has one).

## Phase 4 result — API (2026-06-04)

Implemented #1, #2, #3, #7 in `tools/gen_specialized.py` (regenerated `g1/g2/g3.py`); #5 needed no
change; #6 deferred. Added tests: `test_basis_constants` and `test_implicit_dimension_methods`
(parametrized over G1/G2/G3). Full suite now **118 passing**; `ruff`, `ty check src`, `ty check
tests` all clean.

Possible follow-ups (not blocking): override the hot derived ops on `G1/G2/G3` (`r_vector_part`,
`reverse`, `__add__`) so they don't round-trip through the blade-dict interchange; display-simplify
(#6).

## Phase 4 follow-up — specialized derived ops + README + G4-readiness (2026-06-04)

Per user request, the specialized classes no longer route their core operations through the
`to_blade_dict`/`from_blade_dict` interchange — the generator now emits closed-form versions:

- **Bilinear, derived from the `Gn` reference op** (same machinery as the geometric product):
  `inner_product`, `outer_product` (so `dot`/`wedge`/`__xor__` get them for free).
- **Linear / grade / comparison, structural**: `__add__`, `__sub__`, `__neg__`, `scalar_part`,
  `grades`, `r_vector_part`, `reverse`, `even_part`, `odd_part`, `is_close`, `__iter__`.
  (Cross-type operands still coerce to `Gn` per decision 3.) `numpy` added to generated imports
  for `is_close`.
- Correctness: the existing conformance suite already exercises all of these against `Gn`; **118
  tests still pass**, `ruff` + `ty` (src & tests) clean.

Measured gains (numeric, `tools/bench.py`): `reverse` **100–170×** (was 1.4–2.7×),
`inner_product` **41–59×**, `add` ~4×. (Geometric product unchanged: 13–35× numeric, thousands ×
symbolic.)

Also in this pass:
- **`README.md` created** with usage + a worked "Adding a new algebra (G4)" guide.
- Generator hardened so adding an algebra is a **one-line `ALGEBRAS` edit**: class docstrings now
  auto-generate for any dimension (`docstring_for`/`generic_docstring`), and a subscript bug in the
  header (`"₁₂₃"[n-1]`) was fixed to use `_sub(n)`. Verified end-to-end by generating a throwaway
  `G4` (symbolic product == `Gn`, `I²=+1`, ruff/ty clean) and removing it.
- Generation is now slower (it runs the symbolic geometric + inner + outer products in `Gn`):
  ~tens of seconds for 𝒢₃, minutes for 𝒢₄. One-time cost; documented in the README.

## Related

- Findings/overview live in repo-root `CLAUDE.md` (Assessment section); the eager-simplify
  performance issue there is item #1. Note: per the decision here we **keep** eager simplify on
  `Gn` (accepted slowness) and only avoid it in `G2`/`G3`, so `CLAUDE.md` item #1 should be
  reframed as "scoped to `Gn`, intentionally" rather than "fix globally".
