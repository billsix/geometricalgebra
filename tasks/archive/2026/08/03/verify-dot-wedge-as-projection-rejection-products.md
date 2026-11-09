# Verify dot/wedge as the projection/rejection geometric products

**Created:** 2026-08-03 · **Completed:** 2026-08-03

Confirmed, symbolically in gacalc and with a written proof suitable for the book, that for two
vectors `a, b`, splitting `a` into projection `a_∥ = proj_b(a)` and rejection `a_⊥ = rej_b(a)`
gives `a_∥ b = a·b` (dot) and `a_⊥ b = a∧b` (wedge). The asker was the maintainer (2026-08-03),
while scoping the OpenStax-pedagogy reference doc.

The durable result (the boxed theorem, the two-line proof, the verification summary) was harvested
into `tasks/reference/dot-wedge-projection-rejection.md`, which the book pulls from. It is the
archetype box/unbox result from `tasks/reference/openstax-math-pedagogy.md` §10–11.

## What was done

- `a_∥ b = a·b` and `a_⊥ b = a∧b` verified symbolically (general 2D + 3D vectors, exact `==` on
  `Gn`).
- Sanity checks: `a_∥ + a_⊥ = a`, and `a_∥ b + a_⊥ b = ab = a·b + a∧b`.
- Numeric random trials: 100 float vectors per dimension (2D, 3D), `isclose`
  (`rel_tol = abs_tol = 1e-9`), all passed.
- Proof written up (parallel ⇒ zero wedge; perpendicular ⇒ zero dot) in the reference note.

The verification became a test rather than a throwaway script:
`tests/test_dot_wedge_projection_split.py` (10 tests: 4 symbolic identities × {2D,3D}
parametrized + 2 numeric-trial cases), using the library's own `Gn.project` / `Gn.reject`,
geometric product `*`, `dot`, `wedge`, and `isclose`. ruff + ty clean.

## Decisions

- Used the general `Gn` algebra, since the generated `G1`/`G2`/`G3` are gitignored build
  artifacts. `Gn.project`/`Gn.reject` return `ComposableFunction` typed at `MultiVectorBase`, so
  the split's locals are typed `MultiVectorBase`, not `Gn`.
