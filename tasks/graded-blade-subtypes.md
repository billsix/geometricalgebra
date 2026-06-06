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

- [ ] **Phase 0 — 2D prototype (hand-written, not generated).** Implement `Vector2`, `Bivector2`,
      `Rotor2` by hand with a `match`-based `*`/`^`/`+`, the §B closure return types, and
      widen-to-`G2`. Goal: feel the ergonomics, validate the dispatch reads well, confirm cross-type
      `==` works, and **benchmark** `Vector2×Vector2` vs `G2` vs `Gn`. Cheap, reversible, decisive.
- [ ] **Phase 1 — decide registry + closure policy** for 2D/3D from what Phase 0 teaches.
- [ ] **Phase 2 — generalize the generator.** Refactor `generate_class` to take a blade-set;
      add a `TYPES` registry; add support→closure return-type resolution; emit the T1×T2 dispatch
      ladders. Full `G_n` becomes a registry entry (all blades).
- [ ] **Phase 3 — regenerate, extend conformance + bench**, add a teaching notebook showing the grade
      product table (`Vector2 * Vector2 -> Rotor2`, duals, etc.).
- [ ] **Phase 4 — docs:** the type lattice + return-type table per dimension in `README`/`CLAUDE.md`.

## Recommendation

Worth doing **for the pedagogy**, not the speed. But it's a sizable, combinatorial addition, so gate
it on **Phase 0**: a throwaway 2D hand prototype that proves the dispatch reads well and the speedup
is (or isn't) real before touching the generator. If Phase 0 underwhelms on both ergonomics and
benchmark, stop there cheaply.
