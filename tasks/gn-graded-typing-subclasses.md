# Investigate Gn graded typing-subclasses (Vector/Bivector/Versor/Scalar) + overloads

**Status:** proposed — needs go-ahead (the investigation can start now; implementation after the
feasibility verdict + design are agreed).
**Priority:** 6
**Difficulty:** 6
**Created:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

Investigate whether the **dimension-agnostic `Gn`** can gain graded **typing** subclasses — `Vector`,
`Bivector`, `Versor`, `Scalar`, `Trivector` — the way the generated specialized classes already
carry precise, grade-specific types with `@typing.overload`. The purpose is **purely static typing**:
a value known to be a vector could be annotated/narrowed as such, letting a lot of the rest of the
code use `@overload` for precise `Gn` signatures. Deliverable: a **feasibility verdict + a design
recommendation** (this task), not an immediate rewrite. (Maintainer's idea, 2026-10-27.)

## Context (cold start)

- `Gn` (`src/gacalc/gn.py`) is the one dimension-agnostic reference representation; today it has **no
  graded subtypes**. The **generated** classes (`g1`/`g2`/`g3`) do — `Scalar_n`/`Vector_n`/
  `Bivector_n`/`Trivector`/`Versor_n` — with `@typing.overload` so products/sums are type-precise
  (see `tasks/reference/generated-product-typing.md`, `graded-subspaces-vs-subalgebras.md`).
- `Gn` already has runtime grade **predicates**: `is_vector()`, `is_bivector()`, `is_scalar()`,
  `is_r_vector()`, etc. (in `base.py`). The idea is a typing layer on top of those.

## The idea (maintainer's words, paraphrased)

A subclass `Vector(Gn)` that adds **no behavior** — only a narrowing entry point `as_vector()` that
confirms the value really is a vector and returns it typed as `Vector` (raising otherwise) — and the
same for `Bivector`/`Versor`/`Scalar`/`Trivector`. Purely for typing; then overloads across the code
can state "takes a `Vector`, returns a `Vector`".

## Investigate (the feasibility questions)

1. **Construction/narrowing:** does `as_vector()` return the *same* object re-typed, or a new
   `Vector`-typed instance from the same blade-dict? Can a `@dataclass`/`slots` or plain `Gn` be
   subclassed cheaply with no new fields?
2. **Operation result types — the hard part.** `Gn` methods build results with
   `type(self).from_blade_dict(...)`, so a `Vector(Gn) * Vector(Gn)` would construct a `Vector`
   **even though the product is scalar+bivector** — a *wrong* static (and runtime-class) type. The
   generated classes avoid this with operation-driven `@overload`s *and* value-correct runtime types.
   Determine whether `Gn`'s subclasses must therefore be **narrowing-only "views"** (products widen
   back to `Gn`; you re-narrow with `as_bivector()` etc. at the next known-grade step), or whether
   `from_blade_dict` should pick the class from the result's actual grade.
3. **`TypeIs`/`TypeGuard`:** could `is_vector()` become a `TypeGuard[Vector]` so an `if v.is_vector():`
   branch narrows without an explicit `as_vector()`? That may be more Pythonic than `as_vector()`.
4. **Payoff:** which existing `Gn` signatures would actually become precise with overloads, and does
   `ty` (the repo's type checker) benefit? Keep house rules: externally-fixed names, `cls`/`n`
   naming, annotate-every-binding.

## Initial feasibility notes / suggestions (seed — confirm during the investigation)

- **Likely feasible as a narrowing-view layer.** Thin `Vector(Gn)` subclasses with no new fields +
  `as_vector()` (validate grade, return re-typed) are cheap. Treat them like a *cast you opt into*,
  not a type the algebra preserves.
- **Do NOT let products auto-narrow** unless `from_blade_dict` chooses the class from the result's
  grade — otherwise `vector * vector` mis-types. Safer first cut: operations return `Gn`; the caller
  re-narrows at a known-grade point. Prefer `TypeGuard`-flavored predicates so narrowing is implicit.
- **Keep it consistent with the generated classes' overload vocabulary** so a reader sees one typing
  story across `Gn` and `G`.

## Open questions

1. Narrowing-view (products widen to `Gn`) vs. grade-driven `from_blade_dict` (products land on the
   right subclass automatically)? The latter is more powerful but is effectively re-deriving the
   generated classes' operation-driven typing on `Gn` — recommend the narrowing-view first cut;
   confirm.
2. `as_vector()` methods vs. `TypeGuard`/`TypeIs` on the existing `is_vector()` predicates (or both)?
