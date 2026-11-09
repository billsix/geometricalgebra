# Graded / blade subtypes for G1/G2/G3 (Vector, Bivector, Rotor, ...)

**Created:** 2026-06-06 · **Completed:** 2026-06-06
**Superseded:** the `Vector2`/`Rotor2` names, the shared `scalar.py`, and "no Odd type" all changed later (see `tasks/archive/2026/08/13/drop-graded-type-dimension-suffixes.md`, `tasks/archive/2026/07/22/per-algebra-scalar-types.md`, `tasks/archive/2026/09/05/model-odd-graded-type.md`); the Rotor→Versor rename is `tasks/archive/2026/10/04/rename-rotor-to-versor.md`.

Each dimension had a single full-multivector class (`G1`/`G2`/`G3`). Graded subtypes (vectors,
bivectors, trivectors, rotors = the even subalgebra) were added as first-class, generated,
provably consistent types whose products dispatch by a structural `match` on operand types. The
motive was **pedagogy** (the grade algebra becomes visible and type-checked); speed was secondary.

## Starting point (code pass, 2026-06-06)

- The generator was already a "derive a closed form from the symbolic `Gn` op" engine:
  `emit_bilinear` builds symbolic operands, computes the `Gn` op, `cse`-factors, and emits. For a
  subtype the operands come from a blade subset, and the **support of the result** gives the return
  type.
- A graded type is a class over a blade subset; `generate_class` was refactored to take an explicit
  blade set, with the full `G_n` as the all-blades case.
- Cross-type `__eq__` (simplify-aware over `to_blade_dict()`), the foreign-operand coerce-to-`Gn`
  fallback, and every ABC method written against the interchange protocol already worked for any
  subtype.

## Design

- **Return type = closure of the symbolic support.** For each ordered pair `(T1, T2)` and each
  bilinear op, the generator computes the symbolic `Gn` result and returns the **smallest registered
  type whose blade set ⊇ the support**, falling back to the full `G_n`. This is decided at generation
  time, exactly, so it never depends on runtime float values: `Vector × Vector → Rotor` holds by
  construction, even for orthogonal vectors whose scalar part is exactly 0. `+`/`-` use the same
  closure over the union of the operands' blade sets. A pure blade is obtained with `^`.
- **Dispatch via `match`:** each subtype's `__mul__`/`__xor__`/`inner_product`/`__add__` has one
  `case` per registered rhs type plus a coerce fallback, so the generated code reads as the grade
  product table. The generator emits the T1×T2 table (no multipledispatch dependency). Python numbers
  scale a graded type in place.
- **Widen freely, narrow only on request.** Subtype → full → general is lossless; full → subtype is
  never implicit (narrowing is the one float-sensitive step and stays opt-in).
- In 1D–3D every k-vector is a blade, so grade-subspace types are blade types; the split appears only
  at n ≥ 4.

## Decisions (2026-06-06)

1. **Minimal registry + full-`G_n` fallback:** grade-pure types plus the even `Rotor` type only. No
   `Odd`/`Paravector` types (Paravector stays deferred per `CLAUDE.md`); a mixed result such as
   `Vector3 * Bivector3` (grades {1, 3}) widens to `G3`.
2. **Dimension-suffixed names** (`Vector2`, `Bivector3`, `Rotor3`, …), matching `G2`/`G3` and
   collision-free when families are imported together.
3. **A dedicated `Scalar` type** for grade 0 (plain numbers still scale), so a pure-scalar result
   narrows to `Scalar` rather than `Rotor`. One shared `Scalar {()}` serves every dimension.
4. **The fallback widens both operands to the same-dimension full `G_n`**, not general `Gn` (a Phase
   0 finding: `G2.__add__` coerced a foreign rhs all the way to `Gn`). Whether the existing `G2`/`G3`
   foreign-operand coercion should also prefer same-dimension was left open.
5. **Phase 5 (the maintainer):** the identity is checked against the ABC `rotate(from, to)`, with
   general symbolic vectors (not unit, not angle-parameterized), in both 2D and 3D, as both a
   notebook demo and a test, with a reusable `rotor_from_vectors(from, to)` helper; the project's
   `.inverse()` (= `reverse()/|R|²`) is used so the sandwich is a pure rotation with no manual scaling.

The registry:

| Dim | Graded types (name → blade set) | Full |
|---|---|---|
| all | `Scalar {()}` | — |
| 1D | `Vector1 {(1,)}` | `G1` |
| 2D | `Vector2 {(1,),(2,)}`, `Bivector2 {(1,2)}`, `Rotor2 {(),(1,2)}` (≅ ℂ) | `G2` |
| 3D | `Vector3`, `Bivector3 {(1,2),(1,3),(2,3)}`, `Trivector3 {(1,2,3)}`, `Rotor3 {(),(1,2),(1,3),(2,3)}` (≅ ℍ) | `G3` |

2D resolution examples: `{()}` → `Scalar` (`Bivector2 * Bivector2`, `Vector2 · Vector2`);
`{(1,2)}` → `Bivector2` (`Vector2 ^ Vector2`); `{(),(1,2)}` → `Rotor2` (`Vector2 * Vector2`); a
mixed support → `G2`.

## Phases

- **Phase 0 — hand-written 2D prototype** (`graded2d.py`, committed in `09fe2c7` and removed in
  `07028d0`; it survives in git history only). `Vector2`/`Bivector2`/`Rotor2` with `match`-based
  `*`/`^`/`+`, closure return types, widen-to-`G2`, cross-type `__eq__`. Ergonomics were good (the
  dispatch reads as the product table); typing was float-proof; symbolic coefficients worked; `Rotor2`
  behaved as ℂ. Speed, microseconds per `vector * vector`: typed `Vector2` 1.18 numeric / 21.4
  symbolic, full `G2` 3.12 / 83.2, `Gn` 968 numeric. About 2.7× (numeric) and 3.9× (symbolic) over
  `G2`, small next to the `Gn → G2` jump, so **pedagogy, not speed, justified going on**. Without a
  `Scalar` type, `Bivector2 * Bivector2` landed in `Rotor2`, which motivated decision 3.
- **Phase 1 — registry and closure policy** decided (above).
- **Phase 2 — the generator emits graded types**, additively (the full classes untouched):
  `TypeSpec`, `graded_specs(n)`, `registry_for_dim`, `resolve(support)`; `generate_graded_type`
  (match dispatch for the three bilinear products, scalar-correct `__mul__`/`__rmul__`, a
  widen-both `_coerce(x, cls)` fallback, in-type linear ops and `reverse`); `generate_scalar` for a
  shared `src/geometricalgebra/scalar.py`. Each `g{1,2,3}.py` held the full class plus its graded
  types. Grade-changing ops initially deferred to `G_n` (value-correct, typed too wide).
- **Phase 3 — narrowing, tests, notebook, bench.** `dual`, `r_vector_part`, `even_part`, `odd_part`
  are emitted like the products (symbolic support → `resolve`), e.g. `dual(Bivector3) → Vector3`,
  `Rotor3.r_vector_part(2) → Bivector3`, `Vector3.even_part() → Scalar` (zero). New
  `tests/test_graded.py` (graded types cannot represent arbitrary multivectors, so not the conformance
  parametrization): a product table checking type and value against `Gn`, narrowed grade ops,
  scalars, widen fallbacks, cross-type `==`, ℂ/ℍ identities, inherited ABC methods, symbolic
  products, with values built by linear combination of the basis. New `notebooks/displaygraded.py`,
  whose theme is "the operation decides the type". Bench rows added. Also added mid-phase: narrowing
  `+`/`-` (`Scalar + Bivector2 → Rotor2`) and `Rotor.plane_of_rotation()`.
- **Phase 4 — docs:** a "Graded subtypes" section with the 𝒢₂ return-type table in `README.md`;
  `CLAUDE.md` module layout, an architecture note, and future directions changed from "not built" to
  "built".
- **Phase 5 — the rotor sandwich equals `rotate(from, to)`.** `AbstractMultiVector.rotate(from, to)`
  was fixed to normalize `from`/`to`: un-normalized, it scaled the in-plane part by `|from||to|` and
  left the perpendicular part alone in 3D, a distortion no rotor sandwich can equal. Added
  `rotor_from_vectors(from, to)` = `|from||to| + to·from`, the un-normalized half-angle rotor (the
  `to·from` order sets the direction; `|from||to|` is one `sqrt`, avoiding the nested radical that
  normalizing `R` would need). `R v R̃ = (R R̃) · rotate(v)`; dividing by the scalar
  `R.magnitude_squared()` recovers the rotation and keeps `|v|` (not the sandwich's own magnitude,
  which gives the geometric inverse, and not `.normalize()`, which discards `|v|`). Worked example:
  `e₁ → e₂` gives `R = 1 − e₁₂`, `R R̃ = 2`, `R e₁ R̃ = 2·e₂`. The antiparallel case is a measure-zero
  degeneracy, noted in a comment rather than special-cased. Proved symbolically in 2D and by value in
  3D across `Gn`/`G2`/`G3`, with a notebook walkthrough.

## Verification

Phase 2: graded products matched `Gn` in 1D–3D (including symbolic), ruff + `ty check src` clean,
118 tests. Phase 3: 131 tests. Phase 5: 135 tests. ruff and ty clean at every phase.
