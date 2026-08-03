# Dot and wedge are the parallel/perpendicular faces of the geometric product

**Created:** 2026-08-03 (work record: [[verify-dot-wedge-as-projection-rejection-products]])
**What this is:** a settled, book-ready result with its proof and its computational
verification. This is the **archetype "box/unbox" result** the pedagogy survey names
(see [[openstax-math-pedagogy]] §10 rec. 3 and §11): prove it once, box it, then treat
`ab = a·b + a∧b` as the settled decomposition and build projection/reflection/rotors on
top without reopening it.

## The result (boxed theorem)

For two vectors `a`, `b` with `b ≠ 0`, split `a` relative to `b` into its **projection**
(the part parallel to `b`) and its **rejection** (the part perpendicular to `b`):

    a_∥ = proj_b(a) = (a·b) b⁻¹        a_⊥ = rej_b(a) = (a∧b) b⁻¹

so that `a = a_∥ + a_⊥`. Then the geometric product of each part with `b` isolates one
term of the geometric product:

    a_∥ b = a·b        (the dot product — a scalar)
    a_⊥ b = a∧b        (the wedge product — a bivector)

Equivalently: **the dot product is the projection's geometric product with `b`; the wedge
product is the rejection's.** Adding them recovers `ab = a·b + a∧b`.

## Proof (unboxed, skippable)

Two facts about the geometric product of vectors, both from `uv = u·v + u∧v`:

1. **Parallel ⇒ zero wedge.** If `u ∥ b`, the two span no oriented area, so `u∧b = 0`
   and therefore `u b = u·b` (a scalar).
2. **Perpendicular ⇒ zero dot.** If `u ⊥ b`, then `u·b = |u||b|cosθ = 0`, so
   `u b = u∧b` (a bivector).

Both `·` and `∧` are bilinear, so they distribute over the split `a = a_∥ + a_⊥`:

- `a_∥` is parallel to `b` (it is the scalar multiple `(a·b)b⁻¹ = (a·b/|b|²) b` of `b`), so
  by fact 1, `a_∥ b = a_∥·b`. Distributing the dot: `a·b = (a_∥ + a_⊥)·b = a_∥·b + a_⊥·b`,
  and `a_⊥·b = 0` because `a_⊥ ⊥ b`. Hence `a_∥ b = a_∥·b = a·b`. ∎
- `a_⊥` is perpendicular to `b`, so by fact 2, `a_⊥ b = a_⊥∧b`. Distributing the wedge:
  `a∧b = (a_∥ + a_⊥)∧b = a_∥∧b + a_⊥∧b`, and `a_∥∧b = 0` because `a_∥ ∥ b`. Hence
  `a_⊥ b = a_⊥∧b = a∧b`. ∎

Summing the two identities: `a_∥ b + a_⊥ b = (a_∥ + a_⊥) b = a b`, which matches
`a·b + a∧b`. The split of `a` into parallel/perpendicular parts *is* the split of `ab`
into scalar/bivector parts.

(That `proj_b`/`rej_b` genuinely produce the parallel and perpendicular parts is the same
identity read the other way: `a = a b b⁻¹ = (a·b + a∧b) b⁻¹ = (a·b)b⁻¹ + (a∧b)b⁻¹`, i.e.
`a = a_∥ + a_⊥`, with the first term a multiple of `b` and the second orthogonal to it.)

## Computational verification

Verified in gacalc (`github.com/billsix/geometricalgebra`) — see
`tests/test_dot_wedge_projection_split.py`, using the library's own `Gn.project` /
`Gn.reject`, geometric product `*`, `dot`, and `wedge`:

- **Symbolic, exact** — over fully general 2D vectors (`a = a₁e₁ + a₂e₂`,
  `b = b₁e₁ + b₂e₂`) and 3D vectors, on the eager-simplifying `Gn` reference with `==`.
  All four identities (`a_∥ b = a·b`, `a_⊥ b = a∧b`, `a_∥ + a_⊥ = a`,
  `a_∥ b + a_⊥ b = ab = a·b + a∧b`) hold as symbolic equalities.
- **Numeric, tolerant** — 100 random float vectors per dimension (2D and 3D),
  seed `20260803`, compared with the float-tolerant `isclose` (`rel_tol = abs_tol = 1e-9`).
  All trials pass.

Run: `PYTHONPATH=src python -m pytest tests/test_dot_wedge_projection_split.py -q`
(or `make test`, which regenerates the specialized modules first).

## How the book should use this

Per [[openstax-math-pedagogy]] §11: box the theorem above, put the proof in skippable
"Proof" text ending in ∎, and from then on invoke `ab = a·b + a∧b` **by name** — never
re-derive the component grind. This is the levels-of-abstraction lesson delivered by the
box/unbox grammar: the dot product is one proven face of the geometric product, and the
reader may use it without looking inside.
