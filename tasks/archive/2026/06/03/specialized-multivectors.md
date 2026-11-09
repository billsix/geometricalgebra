# Specialized, performant MultiVector for 2D and 3D

**Created:** 2026-06-04 · **Completed:** 2026-06-04

The geometric product (and the whole `MultiVector` API) was made much faster in 2D and 3D without
losing the general N-dimensional implementation: an abstract base class was introduced, with the
old dict class as the concrete general `Gn` and code-generated, fixed-field `G1`/`G2`/`G3` classes
whose `__mul__` is generated from the symbolic `Gn` product, so the fast path stays provably
consistent with the reference. All five phases (0–5) were done the same day.

## Decisions (2026-06-04)

1. **Coefficients symbolic everywhere; eager simplify on `Gn` only, lazy on `G2`/`G3`.** `Gn` kept
   its eager `__post_init__` `sympy.simplify` (allowed to be slow; it is the oracle), so its tests
   stayed untouched. The specialized classes get speed from a closed-form `__mul__` and simplify
   only lazily, on display / equality / on demand.
2. **Named-field dataclasses via codegen, named after Hestenes' 𝒢ₙ.** `G2` = 𝒢₂ (4 blades), `G3` =
   𝒢₃ (8 blades), `Gn` = the general case. Fields mirror the `e_n` constants: `scalar`, `e_1..e_3`,
   `e_12/e_13/e_23/e_123`. A committed generator in `tools/` emits a static, human-readable `.py`
   (no runtime `lambdify`/`exec`). The dimension parameter was renamed `grade`/`g` → `n`, because
   "grade" already means a blade's grade.
3. **Each dimension gets its own basis constants.** General and specialized values are not meant to
   interact; if they do, the result coerces to the general (blade-dict) representation rather than
   raising.
4. **Lazy-simplify test policy.** `G2`/`G3` equality and the conformance/equivalence tests simplify
   before comparing; the `Gn` tests in `tests/test_multivector.py` were unchanged.

Rejected: a float fast path (fastest, but needs tolerance equality and breaks exact symbolic
tests); a single Cayley-table `DenseEuclidean(n)` class (DRYer, but no named-component API).

Further API decisions (Phase 4): equality with raw scalars was left unchanged (multivector vs
multivector only; compare scalars via `.scalar_part()`, `is_close` for floats); the `MultiVector`
alias was kept for back-compat, with docs steering newcomers to `Gn`/`G2`/`G3`; display
simplification was deferred (later done in `tasks/archive/2026/06/12/display-simplify.md`).

## Design

The abstraction boundary is **"touches the raw representation"**, not "transitively depends on
`__mul__`": almost everything uses `__mul__`, but only through the public operator, so those
methods stay in the ABC. Concrete classes supply the primitives; ABC methods build results of
`self`'s type through a construction protocol (`cls.zero()`, `cls.one()`, `cls.from_scalar()`,
`cls.from_blade_dict()`) instead of module globals. `to_blade_dict()`/`from_blade_dict()` is the
canonical interchange: equality and cross-representation comparison go through it, which is what
made the conformance suite possible.

Class docstrings use Hestenes' 𝒢ₙ and the algebra-vs-element distinction: 𝒢ₙ is the algebra; an
instance is an element of 𝒢ₙ (a multivector); the class is named after its algebra as shorthand.
`G3`'s docstring calls 𝒢₃ Hestenes' "algebra of physical space" (the Pauli algebra).

## Baseline (Phase 0, Python 3.14, sympy 1.14)

Numeric 3D product 0.80 ms; symbolic full 𝒢₂ product 732 ms; full 𝒢₃ product 10,548 ms. `cProfile`
of one 𝒢₃ product: `__post_init__`/`sympy.simplify` (548 calls) was ≈100% of the cost; one product
built 128 intermediate `MultiVector`s. Conclusion: eager simplify, not the dict representation, is
the cost, so the speed comes from (a) a closed-form product and (b) no eager simplify.

## What was built

- **Phase 1 — ABC + `Gn`.** `AbstractMultiVector` holds every representation-independent method;
  abstract primitives are `from_blade_dict`, `to_blade_dict`, `_geometric_product`, plus `__eq__`.
  `Gn` is the old dict class; `MultiVector = Gn` is a back-compat alias; shared methods return
  `typing.Self`. The `grade`→`n` rename touched `unit_pseudoscalar`, `bases`,
  `symbolic_multivector`, `unit_pseudoscalar_squared`, `dual` (two test lines and
  `notebooks/displaymv.py` followed).
- **Module layout.** One class per file, imports only downward: `base.py` (the ABC), `gn.py` (`Gn`,
  its constants, the transform helpers, the alias), generated `g1.py`/`g2.py`/`g3.py` (`G1` added as
  the simplest teaching on-ramp), and `multivector.py` as a thin re-export facade nothing internal
  imports.
- **Phase 2 — codegen.** `tools/gen_specialized.py` multiplies two symbolic `Gn` multivectors, runs
  `sympy.cse`, and emits each output component, rendering operands straight back to attribute access
  (no alias locals) and wrapping long sums under 88 columns. Each class is a
  `@dataclasses.dataclass(eq=False)` with a lazy-simplify `__eq__` that works cross-representation;
  a non-matching operand coerces both sides to `Gn`.
- **Phase 3 — tests.** `tests/test_conformance.py` parametrizes over `{1: [Gn, G1], 2: [Gn, G2],
  3: [Gn, G3]}`, building inputs in `Gn` and comparing back through the interchange: products
  (numeric all-blades; symbolic full product for n=1,2 and vector product for n=3), linear ops,
  grade parts, reverse, dual, inner/outer, inverse, project/reject/reflect/rotate, result-type
  preservation, cross-type coercion, `is_close`.
- **Phase 4 — API.** The generator emits per-module constants of that module's type (`zero`, `one`,
  every basis blade), so `3 * g2.e_1 + 4 * g2.e_2` is a `G2` with no coercion magic; a
  `DIMENSION: ClassVar[int]` makes `n` implicit in `dual`, `unit_pseudoscalar`, `bases`,
  `symbolic_multivector` (explicit `n` still accepted); per-module `__all__` for `g1`–`g3`.
- **Phase 4 follow-up (at the maintainer's request).** The generator also emits closed forms for
  `inner_product`/`outer_product` (derived from the `Gn` op) and structural `__add__`, `__sub__`,
  `__neg__`, `scalar_part`, `grades`, `r_vector_part`, `reverse`, `even_part`, `odd_part`,
  `is_close`, `__iter__`, so they no longer round-trip through the interchange. `README.md` was
  created with an "Adding a new algebra (G4)" guide; adding an algebra became a one-line `ALGEBRAS`
  edit (auto-generated docstrings, a header subscript bug fixed), verified by generating and
  removing a throwaway `G4`. Generation got slower (tens of seconds for 𝒢₃, minutes for 𝒢₄).
- **Phase 5.** `CLAUDE.md` was rewritten for the new architecture, codegen, and benchmarks, and
  its Assessment item on eager simplify was reframed as "scoped to `Gn`, intentionally".

## Benchmarks (`tools/bench.py`, `Gn` vs specialized)

| operation | `Gn` | specialized | speedup |
|-----------|------|-------------|---------|
| G1 / G2 / G3 numeric full product | 0.129 / 0.650 / 4.355 ms | 0.008 / 0.031 / 0.130 ms | 15× / 21× / 34× |
| G1 / G2 / G3 symbolic full product | 51.9 / 725.6 / 10,529 ms | 0.016 / 0.084 / 0.396 ms | 3,157× / 8,660× / 26,578× |

After the follow-up: numeric `reverse` 100–170× (was 1.4–2.7× when inherited), `inner_product`
41–59×, `add` ~4×.

## Verification

Phase 1: 23/23 tests; Phase 3: 89 conformance tests, 112 total (~20 s); Phase 4 and follow-up: 118
passing. `ruff check`, `ruff format`, `ty check src` and `ty check tests` were clean at every phase.
