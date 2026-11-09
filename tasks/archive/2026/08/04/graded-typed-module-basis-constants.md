# Graded-typed module basis constants (so `from gacalc.g2 import e_1` is a Vector2)

**Created:** 2026-08-04 · **Completed:** 2026-08-04

The goal was to let teaching/notebook code write basis vectors **unqualified and concise**
(`3*e_1 + 4*e_2`, matching the printed `3e₁ + 4e₂`) **without losing the graded `Vector2` type**
(or the fast closed-form paths and precise product types). The maintainer (2026-08-04): "it works
as is, but the math printed in the notebooks looks so concise relative to the python code — it'd be
sweet if it matched a little closer, without losing anything", and was explicitly open to reversing
the earlier decision that module-level constants are the module's full class.

Before the change, `from gacalc.g2 import e_1` gave a **`G2`**, `Vector2.e_1` a `Vector2`, and
`gn`'s `e_1` a `Gn`; no `Vector2`-typed module constant existed, so `3*e_1+4*e_2` silently yielded
a `G2`.

## Decision

**Option A, reverse it** (approved by the maintainer, 2026-08-04): the `g1`/`g2`/`g3` module
constants became the graded types. It broke nothing in the gate, was what the mvp consumer asked
for, improved the graded notebook, and lost nothing (the full class stays reachable as `G_n.e_1` /
`G_n(...)` / `Gn`).

**Option B, additive** (a second export such as `from gacalc.g2.basis import e_1`) was rejected:
zero breakage, but it made the import path *longer* (the opposite of the ask), needed `g2` to
become a package or a parallel `g2basis.py`, and gave two names for one value (the ambiguity the
"no local aliases" rule fights). It would only have won if a gated consumer needed the `G2`-typed
bare constant, and none did.

## Findings

- **Why the constants were the full class:** a historical default, never revisited.
  `generate_constants` in `tools/gen_specialized.py` predated the graded subtypes, when `G_n` was
  the module's only type. CLAUDE.md described the status quo but nothing required it, and the
  generator's `resolve([blade], n, name)` already mapped a blade to its graded type.
- **What relied on the `G2`-typed bare constants** (AST-checked across `src`/`tests`, plus mvp):
  nothing in `src/` or `tests/`, and no generated doctest. The only consumers were the two
  full-class teaching notebooks `notebooks/displayg2.py` and `displayg3.py` (e.g.
  `i: G2 = e_1 * e_2`), which are outside the gate (`testpaths = src tests`; `ty` runs on
  `src`/`tests`/`tools`). mvp imported the classes, never the bare constants.
- **`gn.py` was out of scope:** its constants stay `Gn` (no graded subtypes exist for `Gn`), and
  `displaymv.py` / `displayrotations.py` intend `Gn`.
- **Consequences of A:** `3*e_1 + 4*e_2` → `Vector2`; `e_1 * e_2` → `Rotor2`; `e_1 ^ e_2` →
  `Bivector2`; `zero`/`one` → `Scalar2`. Static types only tightened; runtime values were
  byte-identical (checked). `Rotor2` is a sibling of `G2` under `MultiVectorBase`, not a subtype
  (`tasks/reference/generated-product-typing.md`), so the notebooks' `: G2` annotations on bare
  constants had to migrate.
- **The one cost:** the concise bare name `e_1` was reallocated from "full class" to "graded"; the
  full-class notebooks trade `e_1` for `G2.e_1`.
- **Coverage:** g1 `zero`/`one` → `Scalar1`, `e_1` → `Vector1`; g2 `Scalar2`, `Vector2`,
  `e_12` → `Bivector2`; g3 `Scalar3`, `Vector3`, `Bivector3`, `e_123` → `Trivector3`; any G4+
  falls out of `resolve`. The graded types are emitted before the constants (scalar → full class →
  graded → constants), so the name references resolve.

## What changed

- **Generator** (`generate_constants`): each `g1`/`g2`/`g3` constant is emitted at its
  `resolve`d graded type, built with `Scalar_n.from_scalar(...)` / `<graded>.from_blade_dict(...)`.
  The tracked diff was `tools/` only (the regenerated `g*.py` are gitignored).
- **Notebooks:** `displayg2.py` / `displayg3.py` switched bare `e_1…` → `G2.e_1` / `G3.e_1` (and
  `one`/`zero` → `G_n.from_scalar(1/0)`), keeping every `: G2` / `: G3` annotation exact.
  `displaygraded.py` (the payoff) imports `from gacalc.g2 import e_1, e_2` and writes the 2D basis
  unqualified (`3*e_1 + 4*e_2`) while staying a `Vector2`; its 𝒢₃ section stays `Vector3.e_*`
  because the bare names are already bound to 𝒢₂ in that file (one name per algebra, noted in the
  notebook).
- **CLAUDE.md** "Two ways to name a basis blade" updated (module constants = graded type; full
  class via `G_n.e_1`).
- **One test updated:** `tests/test_conformance.py::test_basis_constants` encoded the old contract
  via `getattr(mod, …)` (`type(mod.zero) is G2`), which the import-only scan had missed. It was
  flipped to assert each constant's graded type; its "arithmetic on the constants widens to the
  full class" sub-check still held (scalar + vectors has no covering graded type). It was the only
  `src`/`tests` code depending on the old behavior.

## Verification

At the REPL after regeneration: `e_1, e_2` → `Vector2`; `3*e_1+4*e_2` → `Vector2`; `e_1*e_2` →
`Rotor2`; `e_1^e_2` → `Bivector2`; `g2.one` → `Scalar2`; `g3.e_123` → `Trivector3`; values equal
the class constants (`e_1 == Vector2.e_1`). `pytest` 347 passed; `ty check src tests tools` clean
(ty 0.0.58); the three notebooks executed headless.

## Consumer

mvp could then `from gacalc.g2 import e_1` and keep `Vector2`, gated on the next gacalc release.
mvp's task: github.com/billsix/modelviewprojection `tasks/archive/2026/08/04/unqualify-graded-basis-imports.md`.
