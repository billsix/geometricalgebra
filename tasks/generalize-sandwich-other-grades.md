# Generalize the derived sandwich to other grades (Versor·Bivector → Bivector, …)

**Status:** **partly DONE** 2026-06-08 · the Versor conjugation family landed; reflections + higher-dims remain
**Priority:** 8
**Difficulty:** 5

**Update:** the implementation (`tasks/archive/2026/06/08/derived-sandwich-operation.md`) generated
the **whole `Versor` conjugation family** via `dispatch_method`, not just
`Versor·Vector` — so `Versor3.sandwich(Bivector3) → Bivector3`,
`Versor3.sandwich(Trivector3) → Trivector3` (pseudoscalar invariance),
`Versor3.sandwich(Versor3) → Versor3`, etc. are **already done and tested**. What
remains really is future work:

- **Vector-as-versor reflections** (`v X v⁻¹`, an improper versor) — orientation
  / sign conventions to settle. Not generated (only the even `Versor` class gets a
  `sandwich`).
- **Higher dimensions** (𝒢₄+) once those algebras are generated.

The original notes below are superseded for the Versor-grade cases.

---

## Background

`tasks/archive/2026/06/08/derived-sandwich-operation.md` adds a generated, type-correct sandwich for
**`Versor·Vector → Vector`** only (what rotations need). But the versor
conjugation `R X R⁻¹` is **grade-preserving for any `X`** (when `R` is a versor):
a bivector rotates to a bivector, a trivector to a trivector, and a general
multivector rotates grade-by-grade. So the same derive-the-closed-form trick
applies to every operand grade, and each comes out type-correct.

## What to consider later

- **`Versor3.sandwich(Bivector3) → Bivector3`** — rotating a plane/area element
  (e.g. rotating a rotation plane, or an oriented area). `Versor3 * Bivector3` is
  `{0,2}·{2} = {0,2}` then `·Versor3` = `{0,2}` — but the *grade-0 part of the full
  sandwich* is zero (a versor conjugation preserves grade 2), so the derived
  result is a pure `Bivector3`. Worth confirming symbolically as we did for the
  vector case.
- **`Versor3.sandwich(Trivector3) → Trivector3`** — the pseudoscalar is invariant
  under rotation, so this should derive to the identity on `Trivector3` (a nice
  sanity check / teaching point).
- **`Versor3.sandwich(Versor3) → Versor3`** — conjugating one versor by another
  (composition of rotations in a rotated frame); stays even.
- **`Versor3.sandwich(G3) → G3`** — the general multivector, grade-by-grade.
- **Vector as the versor (reflections):** `v X v⁻¹` is a *reflection* (an
  improper versor). Could generate `Vector.sandwich(...)` for reflections too —
  but mind the sign/orientation conventions (reflections flip orientation).
- **Higher dimensions:** once 𝒢₄+ are generated, the same family applies (with
  more grades).

## Why deferred

`Versor·Vector → Vector` covers the immediate need (rotations in mvp). The other
grades have no current consumer, and each adds generated code + tests. Pick them
up when a use appears (e.g. rotating bivectors/planes in a demo, or a reflection
teaching example), so the generator surface grows only where it's exercised.

## Pointers

- Main task: `tasks/archive/2026/06/08/derived-sandwich-operation.md`
- Complementary type work: `tasks/archive/2026/09/05/model-odd-graded-type.md`
- The generic fallback already covers all grades: `MultiVectorBase.sandwich`
  in `base.py` (runtime `type(x)` projection). This future work is about
  *type-correct closed forms* for the specialized classes, not new capability.
```
```
