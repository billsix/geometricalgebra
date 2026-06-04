# Specialized, performant MultiVector for 2D and 3D

Status: **in progress** — Phases 0, 1 & 2 done · Created 2026-06-04

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
   asserting (decision 4).
4. **Benchmark `G2`/`G3` vs `Gn`**; record results here. Decide whether to make `e_1 * e_2` etc.
   return specialized types by default in low dimensions (API question — see open questions).
5. **Update `CLAUDE.md`** to reflect the shipped result: the new `Gn`/`G2`/`G3` architecture and
   ABC, the 𝒢ₙ terminology, the eager-(`Gn`)/lazy-(`G2`/`G3`) simplify policy, the `grade`→`n`
   rename, the `tools/` generator + committed generated module, and the before/after benchmark
   numbers. Reframe Assessment item #1 from "fix globally" to "intentionally scoped to `Gn`".
   Then **archive this task** (`tasks/archive/specialized-multivectors.md`).

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

## API topics to decide (Phase 3 / Phase 4)

Public-API questions deferred from earlier phases. Resolve while writing the conformance tests
(Phase 3) and the benchmark/finalize step (Phase 4); they don't block correctness.

1. **Per-dimension basis constants & construction ergonomics** (decision 3, not yet built).
   Today you build specialized values via `G2.from_blade_dict({(1,): 3, (2,): 4})`,
   `G2.from_scalar(...)`, `G2.unit_pseudoscalar(2)`, or the raw dataclass `G2(scalar=…, e_1=…)`.
   Proposal: have each module export its own basis constants so users can write
   `from geometricalgebra.g2 import G2, e_1, e_2` then `3 * e_1 + 4 * e_2`. Putting the constants
   in each algebra's module **naturally disambiguates 2D vs 3D `e_1`** (different modules). Open:
   generate these constants from the same tool? include the pseudoscalar (`e_12`, `e_123`)? a
   one-shot `basis()` helper returning all of them?

2. **Dimension-fixed methods on specialized classes.** `G1`/`G2`/`G3` inherit dimension-taking
   methods from the ABC: `unit_pseudoscalar(n)`, `bases(n)`, `symbolic_multivector(n, …)`, and
   `dual(n)`. On a fixed-dimension class these are fragile/awkward (e.g. `G2.unit_pseudoscalar(3)`
   would try to build a blade `G2` can't hold; `g2.dual(2)` makes you re-state the dimension).
   Decide: override them on `G1/G2/G3` to fix `n` to the class's own dimension (so `g2.dual()` takes
   no arg, `G2.unit_pseudoscalar()` returns `e_12`), or document them as `Gn`-only and raise on the
   specialized classes.

3. **Default return type / interop for low dimensions.** Should `Gn` expressions in 2D/3D
   (e.g. `e_1 * e_2` built from the `gn` constants) return specialized `G2`/`G3` by default? (The
   step-4 API question.) And confirm the public contract that mixing a specialized value with a
   `Gn` value **coerces to `Gn`** (decision 3) — vs. raising. Cross-type equality already works via
   the blade-dict interchange.

4. **The `MultiVector` alias.** `MultiVector = Gn` is kept for back-compat. Decide whether docs/
   examples should steer newcomers to `Gn`/`G2`/`G3` and treat `MultiVector` purely as a legacy
   alias.

5. **Equality with raw scalars.** `G2.from_scalar(5) == 5` currently returns `NotImplemented` →
   `False` (eq is defined only against `AbstractMultiVector`). Decide whether a multivector should
   compare equal to a bare `int`/`float`/sympy scalar, and whether `is_close` is the documented
   float-tolerant comparison.

6. **Display simplification.** Decision 1 said `G2`/`G3` should "simplify on display". Right now
   `_repr_latex_` (inherited) renders raw, lazily-unsimplified coefficients (sympy still auto-
   simplifies trivially). Decide whether to override display to fully simplify first.

7. **Per-module `__all__` / public surface.** Decide the public names each of `gn.py`/`g1.py`/
   `g2.py`/`g3.py` exports (class only? class + basis constants? + helpers?).

## Related

- Findings/overview live in repo-root `CLAUDE.md` (Assessment section); the eager-simplify
  performance issue there is item #1. Note: per the decision here we **keep** eager simplify on
  `Gn` (accepted slowness) and only avoid it in `G2`/`G3`, so `CLAUDE.md` item #1 should be
  reframed as "scoped to `Gn`, intentionally" rather than "fix globally".
