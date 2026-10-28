# Lean: make dot/wedge/measures faithful to Python's grade-projection definitions

**Status:** done — 2026-10-28. `make lean` green (8958 jobs; completeness gate OK).
**Priority:** 7
**Difficulty:** 4
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer flagged two linked things in the Lean proofs: (A) the fundamental identity embedded the
dot product with `smul (dot a b) one` ("multiply `one` by a scalar to change its type"), and (B) more
broadly, Lean reads a raw coordinate field (`.s`, top-grade `.c12`/`.c123`) where **Python** defines
dot/wedge/scalar-product as **grade projections** of the geometric product (`r_vector_part(k)`), even
though the grade-projection operator `rVectorPart` already exists and `Contractions.lean` already uses it.
Resolution: (A) a **`scalar` constructor + `IsScalar` predicate** (the `vec`/`IsVector` pairing) replaces
the `smul … one` idiom; (B) **bridging lemmas** tie the coordinate definitions to `rVectorPart` without
changing them. Both implemented; `make lean` green. The durable rationale, the full site catalog, and the
rejected alternatives live in `tasks/reference/lean-ga-proof-architecture.md` → "Scalars into the algebra".

## Part A — scalar embedding via a constructor

Root cause of the asymmetry: `dot a b : ℝ` is a scalar while `wedge a b : Gₙ` is a multivector, so an
object-valued conclusion must *embed* the scalar; `smul (dot a b) one` was that embedding and could not
simply be dropped (`= dot a b` is `ℝ ≠ Gₙ`). The maintainer chose a named `scalar` constructor + `IsScalar`
predicate over the `smul … one` spelling. Done:

- **G2** gained `def scalar (a : ℝ) : G2` (named fields — G2 has no `zero`), plus `isScalar_scalar` and
  `eq_scalar_of_isScalar` (the latter renamed from `eq_smul_one_of_isScalar`; no external consumers). G3
  already had `scalar`/`IsScalar`/the bridges.
- `AlgebraLaws.scalar_mul : mul (scalar k) b = smul k b` added (G2 + G3) — an embedded-scalar factor pulls
  out in one step.
- Every grade-0 embedding of `dot`/`normSq` in a conclusion now reads `scalar (…)`: `mul_eq_dot_add_wedge`,
  `dot_is_sym_part`, `vec_mul_eq_dot_add_wedge`, `mul_vec_self` (G3 and `ProjectionRotation2D`), and the
  `hsplit`s in `Projection3D`/`StandardPosition2D`.
- **G1 left on `smul k one`** (trivial algebra; no `rVectorPart`/`IsScalar`) — deliberate; a cheap parity
  follow-up if ever wanted. `eq_smul_basis` keeps its `smul g.s one` term on purpose (a basis expansion
  where `one` is the grade-0 basis blade, not a type-cast).

## Part B — dot/wedge/measures as grade projections (bridging lemmas)

Chosen option: **keep the fast coordinate definitions, add bridging lemmas** (not a redefinition; the a/b/c
analysis is in the reference doc). Added:

- `GradeProjection.G2`/`G3` `dot_eq_rVectorPart_zero : scalar (dot a b) = rVectorPart 0 (mul a b)` — object
  form, all multivectors (also ties Part A's `scalar` to the projection).
- `GradeProjection.G2`/`G3` `wedge_eq_rVectorPart_two {a b} (IsVector a) (IsVector b) :
  wedge a b = rVectorPart 2 (mul a b)` — vectors → the grade-2 part.
- `Measures.G2.signedArea_eq_rVectorPart_two`, `Cross.G3.signedVolume_eq_rVectorPart_three` — the top-grade
  reads; `Measures`/`Cross` gained `import GacalcProofs.GradeProjection`.

`normSq` got no separate bridge (it is `dot a a` up to `reverse`; add one only if a consumer needs it).

## Files touched

`G2.lean`, `G3.lean`, `AlgebraLaws.lean` (scalar constructor/bridges/`scalar_mul`, embedding sites);
`Projection3D.lean`, `ProjectionRotation2D.lean`, `StandardPosition2D.lean` (embedding sites + consumers);
`GradeProjection.lean`, `Cross.lean`, `Measures.lean` (Part B lemmas + imports); and the reference doc.

## Notes / history

- **The `hsplit` consumer coupling (the one non-obvious fix).** Changing the `hsplit` in
  `Projection3D`/`StandardPosition2D` from `smul (dot …) one` to `scalar (dot …)` broke their downstream
  rewrite chains, which had relied on the `smul`/`one` structure (`smul_mul` then `one_mul`). The fix is
  the single `scalar_mul` lemma in place of that pair. (The intermediate commit that changed the `hsplit`
  statements without this consumer fix did not build — a reminder to grep consumers before changing a
  widely-`rw`-ed lemma's shape.)
- Both original open questions resolved: policy → bridging lemmas (a); dims scope → G2/G3 only.

See also: [[lean-g2-object-out-parity]] (lifted the dot/wedge *conclusions* to object form — this task is
its sibling, about their *definitions*); `tasks/reference/lean-ga-proof-architecture.md` → "Scalars into
the algebra" (the durable catalog, rationale, and rejected alternatives);
`proofs/GacalcProofs/GradeProjection.lean`, `proofs/GacalcProofs/Contractions.lean`.
