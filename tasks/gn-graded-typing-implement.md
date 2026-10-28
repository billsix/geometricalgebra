# Implement the Gn graded-typing narrowing layer (TypeGuard, if a consumer needs it)

**Status:** proposed — needs go-ahead **and** a concrete consumer. The feasibility investigation
recommended doing this only when a dimension-agnostic `Gn` call site actually benefits from narrowing
(otherwise `Gn` stays the simple reference). Don't build speculatively.
**Priority:** 8
**Difficulty:** 6
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

Add a thin, static-only graded-typing narrowing layer to `Gn`, per the verdict in
`tasks/reference/gn-graded-typing-feasibility.md` (design (A): `TypeGuard`, operations widen to `Gn`,
re-narrow at known-grade points — not a hand-written overload table, not grade-driven auto-narrowing).
This is the opt-in follow-on to the investigation (`gn-graded-typing-subclasses.md`, archived 2026-10-28).

## Context (cold start)

- **Read `tasks/reference/gn-graded-typing-feasibility.md` first** — it carries the verdict, the
  empirical findings (cheap subclassing; the `type(self).from_blade_dict` mis-typing; `TypeGuard`/`TypeIs`
  narrowing under `ty`), the design fork, and the rejected alternatives.
- The precise *per-dimension* graded typing already exists on the generated `G` classes
  (`generated-product-typing.md`); this layer only adds *dimension-agnostic* narrowing on `Gn`.

## Plan (design (A) — static-only via TypeGuard)

1. Add marker subtypes in `gn.py`: `class Vector(Gn): __slots__ = ()` (and `Bivector`, `Scalar` as
   warranted). No behaviour, no new fields.
2. Add **`Gn`-specific** narrowing helpers returning `TypeGuard[...]` (NOT a retype of the inherited
   `base.is_*`, which is shared with `G` and can't name a `gn`-level subtype). Either `gn`-level free
   functions (`gn_as_vector`?) or `Gn` methods. Use `TypeGuard`, not `TypeIs` (a plain grade-1 `Gn` is
   not a subtype instance — `TypeIs` would be unsound).
3. Wire `@typing.overload`s onto the **specific** `Gn` signatures the identified consumer needs — and
   only those. Operations still return `Gn`; the caller re-narrows at the next known-grade step.
4. Keep house rules: externally-fixed names exempt, `cls`/`n` naming, annotate every binding, `ty` clean
   (`make type-check` / the full-context generated check if any `G` signature is touched — it should not
   be).

## Open questions

1. **Who is the consumer?** Name the dimension-agnostic `Gn` call site(s) that need narrowing before
   starting — the investigation found none today, and the verdict is "do nothing until one exists."
2. Marker subtypes as real `Gn` subclasses (design A, runtime value stays `Gn`) vs. real instances +
   widening overrides (design B) — A unless a consumer needs `isinstance` dispatch. Confirm per the
   reference doc.
