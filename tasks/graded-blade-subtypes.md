# Graded / blade subtypes for G1/G2/G3 (Vector, Bivector, Rotor, ...)

**Status:** plan / design — needs go-ahead (recommend a 2D prototype first)
**Started:** 2026-06-06

## Goal

Today each dimension has a single full-multivector class (`G1`/`G2`/`G3`) carrying all 2ⁿ fields.
Mathematicians instead work with *graded* objects — vectors, bivectors, trivectors, rotors (the even
subalgebra), etc. — and a product moves between them by well-defined rules (two vectors multiply to a
scalar+bivector; orthogonal vectors to a pure bivector). This task plans introducing those graded
subtypes as first-class, **generated, provably-consistent** types whose operations are dispatched by
a structural `match` on operand types — primarily for **pedagogy** (the grade algebra becomes
visible and type-checked), secondarily for efficiency.

Answers to the four motivating questions are folded in below (§ "The four questions").

## Code-pass findings (what we have to build on — 2026-06-06)

Studied `base.py`, `gn.py`, the generated `g*.py`, `tools/gen_specialized.py`, `tools/bench.py`,
`tests/test_conformance.py`.

1. **The generator already is a "derive a closed form from the symbolic Gn op" engine.**
   `emit_bilinear` (`gen_specialized.py:207`) builds symbolic operands `a_mv`, `b_mv` from the type's
   blades, computes the `Gn` op (`a_mv * b_mv`, `.inner_product`, `.outer_product`), reads the result
   blade-dict, `sympy.cse`-factors it, and emits a closed form. **This is exactly the primitive we
   need** — the only change is that operands are built from a *subset* of blades, and the *support of
   the result* tells us the return type.
2. **A graded type = a class over a blade-subset.** `generate_class` (`gen_specialized.py:336`) is
   hard-wired to `blades_for_dim(n)` (all blades). Refactor it to take an explicit blade-set; the
   existing full `G_n` becomes the special case "blade-set = all blades." Same machinery emits both.
3. **Cross-type equality already works.** The generated `__eq__` (`gen_specialized.py:397`) compares
   via `to_blade_dict()` against *any* `AbstractMultiVector`, simplify-aware. So `Vector2(...) ==
   G2(...) == Gn(...)` already holds when blade-dicts match — a major enabler: subtypes interoperate
   with the existing classes for free.
4. **Foreign-operand fallback is already the pattern.** `emit_bilinear`'s `cross` argument coerces a
   non-matching rhs to `Gn` and runs the general op (`gen_specialized.py:219-223`). The subtype design
   generalizes this: a *registered* rhs type uses its specific closed form; anything else coerces to
   `Gn`.
5. **Shared ABC methods come for free.** Everything written against the interchange protocol in
   `base.py` (inner/outer via `*`, project/reject/reflect, magnitude, normalize, dual, ...) works on
   any subtype without change; only the representation-touching primitives are per-type.
6. **Test/bench scaffolding is parametrized and easy to extend.** `tests/test_conformance.py:44`
   (`CASES = [(n, cls) ...]`) and `tools/bench.py:36` (`SPECIALIZED`) are simple registries to add
   types to.

## Design

### A. Type registry per dimension (the set of blade-subsets to emit)

Each entry is `(class_name, frozenset_of_blades, dimension)`:

- **1D:** `Vector1 {(1,)}`; (scalars are just numbers); full `G1` already exists.
- **2D:** `Vector2 {(1,),(2,)}`, `Bivector2 {(1,2)}`, `Rotor2 {(),(1,2)}` (even ≅ ℂ); full `G2`.
- **3D:** `Vector3 {(1,),(2,),(3,)}`, `Bivector3 {(1,2),(1,3),(2,3)}`, `Trivector3 {(1,2,3)}`,
  `Rotor3 {(),(1,2),(1,3),(2,3)}` (even ≅ ℍ), optionally `Paravector3 {(),(1,),(2,),(3,)}` and an
  `Odd3 {(1,),(2,),(3,),(1,2,3)}`; full `G3`.

In 1D–3D every k-vector is a blade, so each grade-subspace type *is* the blade type (the
blade-vs-general-k-vector split only appears at n ≥ 4 — note for any future `G4`).

### B. Return type = symbolic support → closure (this is the crux, and it kills the FP problem)

For each ordered pair `(T1, T2)` and each bilinear op, the generator computes the `Gn` symbolic
result and takes its **support** = the set of blades with a nonzero symbolic coefficient. The return
type is the **smallest registered type whose blade-set ⊇ support** (a lattice "join"/closure). This
is decided **at generation time, symbolically and exactly** — so it never depends on runtime float
values. `Vector × Vector → Rotor` is true *by construction of the wedge*, not by inspecting whether a
computed scalar happens to be ~0.

- If no registered type covers the support, fall back to the full `G_n` for that dimension (always a
  valid covering type). **Registry must be "closure-complete" or accept the full-`G_n` fallback** —
  e.g. `Vector3 × Bivector3` → support {grade 1, grade 3} = needs `Odd3` or falls back to `G3`. This
  is a registry-design decision (include `Odd3`/`Paravector3` or let those land in `G3`).
- `+`/`-` return type = smallest type covering the *union* of the operands' blade-sets (same closure
  logic on grade-sets rather than product support).
- `dual`, `reverse`, grade projection: `dual` changes grade so its return type is resolved the same
  way (e.g. `dual(Vector3) → Bivector3`); `reverse` stays in-type; `r_vector_part(r)` of a type that
  lacks grade r returns that type's zero (or a dedicated grade-r type) — an edge case to pin down.

### C. Dispatch via structural `match` (the pedagogical payoff)

Each subtype's `__mul__`/`__xor__`/`inner_product`/`__add__` dispatches on the rhs type. The generator
emits, per method, a branch per registered rhs type with the right closed form and return type, and a
final coerce-to-`Gn` fallback. Presented as a `match`/`isinstance` ladder it reads as the grade
product table — e.g.:

```python
def __mul__(self, rhs):
    match rhs:
        case Vector3():    ...   # -> Rotor3   (scalar + bivector)
        case Bivector3():  ...   # -> Odd3 / G3
        case Trivector3(): ...   # -> Bivector3 (a dual)
        case _:            ...   # coerce to Gn
```

Binary ops need genuine double dispatch; the generator emits the T1×T2 table (no runtime
multipledispatch dependency). Scalars (Python numbers) scale a graded type in-place (`2 * Vector3 ->
Vector3`).

### D. Conversions: widen freely, narrow only on request

- **Widen** (subtype → full / general): always valid, lossless — `Vector2 -> G2 -> Gn`.
- **Narrow** (full → subtype): only when the other grades are zero — and *this* is the one place
  floats bite. So narrowing is **never implicit**; provide an explicit, opt-in `.as_vector(tol=...)`
  / `.compress(tol=...)` / reuse `r_vector_part`. The automatic product path never narrows by value
  (§B handles typing structurally).

## The four questions (direct answers)

1. **Possible?** Yes. A subtype is a blade-subset class; the generator's symbolic-derivation engine
   already produces the closed forms and (now) the return types. Refactor `generate_class` to take a
   blade-set; full `G_n` = all-blades case.
2. **Efficiency?** Yes but secondary — real arithmetic savings (a `Vector3×Vector3` closed form does
   ~9 mul-adds vs the full 8-field `G3` product that still evaluates `0*0` terms), larger symbolic
   savings (no zero-term construction), ~2.7× memory for `Vector3` vs `G3`. But Python per-op +
   dispatch overhead can erode it; the big jump already happened at `Gn → G3`. **Benchmark before
   selling it.**
3. **`match` dispatch?** Yes — and it's the main reason to do this. It makes the grade algebra
   explicit, type-checked, and teachable; the generated dispatch table *is* the product table.
4. **Floating point?** Non-issue with this design: return types are decided **by the operation,
   symbolically at generation time**, never by inspecting runtime coefficients. Want a pure blade →
   use `wedge` (defined to give grade r+s). The only float-sensitive step is explicit, opt-in
   narrowing (§D).

## Phase 1 decisions (settled 2026-06-06)

1. **Minimal registry + full-`G_n` fallback.** Register only the grade-pure types + the even/`Rotor`
   type; any product whose support isn't covered by a registered type widens to that dimension's full
   `G_n`. No `Odd`/`Paravector` types for now (Paravector stays deferred per `CLAUDE.md`).
2. **Dimension-suffixed names** (`Vector2`, `Bivector3`, `Rotor3`, …), matching `G2`/`G3` and
   collision-free when 2D and 3D families are imported together.
3. **Dedicated `Scalar` type** for grade 0 (in addition to plain Python numbers, which still scale).
   Pure-scalar product results narrow to `Scalar` rather than to `Rotor`.

### The registry (final, per dimension)

A single **shared `Scalar`** type `{()}` serves every dimension (a scalar is the same in all `G_n`;
`Scalar * <anything>` just scales). Then:

| Dim | Graded types (name → blade-set) | Full |
|---|---|---|
| 1D | `Vector1 {(1,)}` | `G1` |
| 2D | `Vector2 {(1,),(2,)}`, `Bivector2 {(1,2)}`, `Rotor2 {(),(1,2)}` (≅ ℂ) | `G2` |
| 3D | `Vector3 {(1,),(2,),(3,)}`, `Bivector3 {(1,2),(1,3),(2,3)}`, `Trivector3 {(1,2,3)}`, `Rotor3 {(),(1,2),(1,3),(2,3)}` (≅ ℍ) | `G3` |

`Scalar` and the full `G_n` are both registry entries (grade-0-only and all-blades, respectively).

### Return-type resolution (the closure rule, restated with these choices)

Return type = the **smallest registered type whose blade-set ⊇ the symbolic support** of the result,
searched within {`Scalar`} ∪ {that dimension's graded types} ∪ {full `G_n`}, falling back to full
`G_n` when nothing smaller covers it. Worked 2D examples:

- support `{()}` → `Scalar` (e.g. `Bivector2 * Bivector2`, `Vector2 · Vector2`)
- support `{(1,),(2,)}` → `Vector2`
- support `{(1,2)}` → `Bivector2` (e.g. `Vector2 ^ Vector2`)
- support `{(),(1,2)}` → `Rotor2` (e.g. `Vector2 * Vector2`)
- mixed `{(1,),(1,2)}` etc. → not covered → `G2`

### Operations to emit per type

- **Bilinear, closure-typed:** `_geometric_product`/`__mul__`, `outer_product`/`__xor__`,
  `inner_product`. (Return type from the rule above.)
- **Linear, in-type (widen on cross-grade):** `__add__`, `__sub__`, `__neg__`, scalar `*`.
- **Unary, typed by op:** `reverse` (in-type), `dual` (grade-flipped → resolved type),
  `r_vector_part`/grade projection (→ that grade's type or `Scalar`), `even_part`/`odd_part`.
- **Other shared:** `__eq__` (simplify-aware over `to_blade_dict`, cross-type), `from_blade_dict`/
  `to_blade_dict`, `magnitude`/`abs`/`normalize` (inherited from ABC), per-type basis constants.

### Fallback target (Phase 0 lesson, now a rule)

A graded type's foreign/uncovered-operand fallback widens **both** operands to the **same-dimension
full `G_n`** (not general `Gn`). Open: also change the existing `G2`/`G3` foreign-operand coercion
to prefer same-dimension over general `Gn` (currently it always goes to `Gn`).

## Risks / open questions

- **Combinatorial size.** ~3–8 types/dim × several ops × T1×T2 dispatch. Generatable, but the file
  size and the generation time grow (the generator runs `Gn` symbolic ops; 3D is already tens of
  seconds — though each subtype product is *smaller* than the full one).
- **Registry closure.** Decide whether to include `Odd3`/`Paravector3` so products stay in registered
  types, or accept full-`G_n` fallback for "mixed-grade" results. (Leaning: include the even/rotor +
  the few useful mixed types; fall back to `G_n` otherwise.)
- **Grade-projection / dual edge cases** on narrow types (return-type when a grade is absent).
- **Conformance + bench scope.** Add subtypes to `CASES`/`SPECIALIZED`; but subtypes aren't closed
  under all ops, so conformance must assert *value* equality via `to_blade_dict` (works already) while
  allowing the *type* to widen. New bench rows: `Vector3*Vector3` vs `G3` vs `Gn`.
- **Surface area vs. clarity.** 7 types and their tables can overwhelm a beginner as easily as
  enlighten — the framing/docs matter.

## Recommended staged plan

- [x] **Phase 0 — 2D prototype (hand-written, not generated).** Done 2026-06-06 in
      `tasks/prototypes/graded2d.py` (committed in `09fe2c7`, removed in `07028d0`; preserved in git history) (throwaway, not wired into the package). Implemented `Vector2`,
      `Bivector2`, `Rotor2` with `match`-based `*`/`^`/`+`, §B closure return types, widen-to-`G2`,
      and simplify-aware cross-type `__eq__`. See "Phase 0 results" below.
- [x] **Phase 1 — registry + closure policy decided** (2026-06-06): minimal registry + `G_n`
      fallback, dimension-suffixed names, dedicated `Scalar`. See "Phase 1 decisions" above.
- [x] **Phase 2 — generator emits graded types (2026-06-06).** See "Phase 2 results" below.
- [ ] **Phase 3 — narrow grade ops, then tests + notebook (detailed plan below).**
- [ ] **Phase 4 — docs:** the type lattice + return-type table per dimension in `README`/`CLAUDE.md`.

## Phase 3 plan (detailed, 2026-06-06)

### 3a. Narrow the grade-changing ops (prerequisite — do first)

Today `dual` / `r_vector_part` / `even_part` / `odd_part` on a graded type defer to the full `G_n`
and so return `G_n` (value-correct, typed too wide — e.g. `dual(Bivector3) -> G3` instead of
`Vector3`). Fix by emitting them like the bilinear products: compute the symbolic result, take its
**support**, `resolve()` the tightest type, emit a closed form constructing it. All four are special
cases of machinery already in the generator:

- `dual`: `a_mv.dual(n)` is a fixed unary product (`self * I⁻¹`); resolve its support.
  → `dual(Bivector3) -> Vector3`, `dual(Vector3) -> Bivector3`, `dual(Scalar) -> Trivector3`, etc.
- `r_vector_part(r)`: support = this type's grade-`r` blades → resolve (so `Rotor3.r_vector_part(2)
  -> Bivector3`, `Rotor3.r_vector_part(0) -> Scalar`, `Vector3.r_vector_part(0) -> Scalar` (zero)).
  Emit a per-`r` branch.
- `even_part` / `odd_part`: support = even/odd-grade blades of this type → resolve (`Rotor_n` stays
  `Rotor_n`; `Vector_n.even_part() -> Scalar` (zero)).

Regenerate; the result types narrow. Keep the widen fallback only for genuinely mixed results.

### 3b. Tests — new `tests/test_graded.py`

Graded types can't represent arbitrary multivectors, so they don't fit `test_conformance.py`'s
`[Gn, G1, G2, G3]` full-rep parametrization → a dedicated file. Coverage:

- **Product table (value + type).** A parametrized list of `(T1, op, T2) -> ExpectedType` cases
  (`Vector2 * Vector2 -> Rotor2`, `Vector2 ^ Vector2 -> Bivector2`, `Bivector2 * Bivector2 ->
  Scalar`, `Vector3 * Trivector3 -> Bivector3`, `Vector3 * Bivector3 -> G3`, …). For each: assert
  `type(result) is ExpectedType` **and** the value equals the same op done through `Gn` (widen both
  operands to `Gn`, run the reference op, compare via `==`). The table doubles as documentation.
- **Grade ops narrow (3a):** `type(Bivector3(...).dual()) is Vector3`, `Rotor3.r_vector_part(2) is
  Bivector3`, etc., with value checks.
- **Scalars:** `Scalar * X -> type(X)`; `3 * Vector2 -> Vector2`; `Bivector2*Bivector2 -> Scalar`.
- **Widen fallback:** `Vector2 + Bivector2 -> G2`; `Vector2 * G2 -> G2`; cross-dim/foreign coerce.
- **Cross-type `==`:** `Vector2(3,4) == G2(e_1=3,e_2=4) == Gn(...)`.
- **Rotors as ℂ/ℍ:** `Rotor2` unit bivector squares to −1; `Rotor3` quaternion identities.
- **Inherited ABC still works:** `magnitude`, `normalize`, `reverse`, `is_close` on graded values.
- **Symbolic:** at least one symbolic product per dimension equals the `Gn` symbolic result.
- Helper: a tiny `expected_type(support, n)` mirroring `resolve` so most cases are checked
  structurally rather than by a brittle hand table (keep a few explicit ones as readable docs).

### 3c. Notebook — new `notebooks/displaygraded.py`

A teaching notebook whose star is **the operation decides the type** (printed via
`type(x).__name__`), since that's the pedagogical payoff. Percent-format, GPL header, kernel
`geometricalgebra`. Outline:

1. Intro: grades vs. closed subalgebras; the registry per dimension.
2. **2D:** build `Vector2`; `a * b` → show it's a `Rotor2` with `scalar = a·b`, `e_12 = a∧b`;
   `a ^ b` → `Bivector2`; orthogonal vs. parallel vectors (type stays `Rotor2`, FP-proof);
   `Bivector2 * Bivector2 -> Scalar`; `Rotor2` ≅ ℂ (`e_12² = −1`, rotor rotates a vector).
3. **The grade product table** rendered from live calls (`type(...).__name__`) — the dispatch table
   made visible.
4. **3D:** `Vector3 * Vector3 -> Rotor3`; `Vector3 ^ Vector3 -> Bivector3`; **`dual(bivector) ->
   Vector3`** (the cross-product connection, post-3a); `Rotor3` ≅ ℍ; mixed grade widening to `G3`.
5. "Want a pure blade? use `^`" — the FP/typing note in prose.
6. Interop: a graded value `== G2`/`Gn`; widen with arithmetic.

(Leave `displayg2.py`/`displayg3.py` as-is; the graded story is cross-dimensional, so its own
notebook is cleaner.)

### 3d. (optional) bench rows

Add `Vector2*Vector2` / `Vector3*Vector3` (typed) vs full `G_n` vs `Gn` to `tools/bench.py`, echoing
the Phase 0 numbers from real generated code.

### Sequencing & gates

3a → regenerate → 3b (tests green, count rises from 118) → 3c (notebook executes, ruff clean) →
optional 3d. Keep `ty check src/tests` + ruff clean at every step.

## Phase 2 results (2026-06-06)

Implemented in `tools/gen_specialized.py` (additive — the existing full `G1/G2/G3` generation is
untouched, so the package stayed green throughout):

- **Registry + closure (`resolve`)**: `TypeSpec`, `graded_specs(n)`, `registry_for_dim`, and
  `resolve(support)` → smallest covering type. Verified against the hand table
  (`Vector2*Vector2→Rotor2`, `Bivector2*Bivector2→Scalar`, `Vector3*Bivector3→G3`, …).
- **`generate_graded_type`**: emits each graded class with `match`-on-rhs-type dispatch for the three
  bilinear products (return type from `resolve`), scalar-correct `__mul__`/`__rmul__`, widen-both
  fallback via a module `_coerce(x, cls)`, in-type linear ops + `reverse`, and grade-changing ops
  (`even_part`/`odd_part`/`r_vector_part`/`dual`) deferred to the full `G_n` (value-correct, widens).
- **`generate_scalar`**: the shared dimension-agnostic `Scalar` in its own `src/geometricalgebra/
  scalar.py`; `Scalar * x` scales `x` and returns x's type.
- **Wiring**: each `g{1,2,3}.py` now contains the full `G_n` **plus** its graded types (`Vector_n`,
  `Bivector_n`, `Trivector3`, `Rotor_n`), importing `Scalar`; `__all__` updated.

**Validation:** 1D/2D/3D graded products match the `Gn` reference (incl. symbolic); FP-proof typing
(orthogonal vectors still produce a `Rotor`); `Scalar` as a real result type (`Bivector2*Bivector2`,
`Vector1*Vector1`, inner products); `Rotor` ≅ ℂ/ℍ checks; widen fallbacks land in `G_n`.
**ruff + `ty check src` clean; 118 tests still pass** (full types unaffected).

**Known v1 limitations (for Phase 3/later):** grade-changing ops widen to `G_n` instead of narrowing
(e.g. `dual` of a `Bivector3` returns `G3`, not `Vector3`) — value-correct, just not tightly typed;
graded types not yet in the conformance suite or bench; no teaching notebook/docs yet.

## Phase 0 results (2026-06-06)

Prototype: `tasks/prototypes/graded2d.py` (committed in `09fe2c7`, removed in `07028d0`; preserved in git history) (run `python tasks/prototypes/graded2d.py`).

**Ergonomics — good.** The `match`-on-rhs-type dispatch reads exactly as the grade product table; the
module docstring is literally that table, and each `case` is one line with a "what grade does this
produce" comment. This is the pedagogical artifact we wanted.

**Correctness / FP — confirmed.** Return type is decided by the operation, not by values:
`Vector2(1,0) * Vector2(0,1)` is a `Rotor2` (its scalar part is exactly 0) — we never narrowed on a
float. Cross-type `__eq__` against `G2`/`Gn` works (the simplify-aware compare over `to_blade_dict`).
Symbolic coefficients work unchanged (lazy, no eager simplify). `Rotor2` is ℂ: `e_12² == -1`.

**Speed — real but modest (this is the honest verdict).** Microseconds/op for `vector * vector`:

| | numeric | symbolic |
|---|---|---|
| `Vector2` (typed) | **1.18** | **21.4** |
| `G2` (full) | 3.12 (2.7×) | 83.2 (3.9×) |
| `Gn` (general) | 968 (822×) | (orders slower) |

So the typed path is ~2.7× faster than full `G2` numerically and ~3.9× symbolically (and both are
already enormously faster than `Gn`). A real saving, but small next to the `Gn→G2` jump — consistent
with the prediction that Python per-op overhead caps the win. **Pedagogy, not speed, is the
justification.**

**Design notes learned for the generator:**
- The widen fallback must widen **both** graded operands to the dimension's full type. `G2.__add__`/
  `__mul__` coerce a *foreign* `AbstractMultiVector` rhs all the way to general `Gn`, so
  `Vector2.widen() + Bivector2(...)` lands in `Gn`, not `G2`. The generated graded types' fallback
  should target the same-dimension full `G_n` (and arguably the existing `G2/G3` foreign-operand
  coercion should prefer same-dimension over general `Gn`).
- `Bivector2 * Bivector2 -> Rotor2` (a pure scalar with `e_12=0`): confirms the "smallest registered
  type covering the support" rule, and the case for a dedicated `Scalar` type if we want it to narrow
  further.

## Recommendation (updated after Phase 0)

**Ergonomically it's a win; the speed is a minor bonus, not the reason.** Decision for the human:
proceed only if the *teaching value* justifies the combinatorial surface (a type lattice + dispatch
table per dimension + generator work). If yes, go to Phase 1 (registry + closure policy) then Phase 2
(generalize the generator). If the goal was speed, Phase 0 says it's not worth it — the specialized
full classes already capture most of the win.
