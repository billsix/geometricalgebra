# Use `bivector_from_vectors` / `i` in the notebooks and unit tests

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-08-14 **Updated:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Adopted `bivector_from_vectors` / `i` at the genuine "plane as a means to an end" sites (the only two
the 2026-08-27 finding verified), and added one teaching cell introducing the helpers. The Gn-narrowing
prerequisite cleared earlier this session (`Gn.bivector_from_vectors`/`Gn.i` now return `Gn`), so no
binding is type-downgraded. Container `make format` and `make test` (697 passed) green.

## What was done (maintainer decisions, 2026-10-09)

- **Q1 — one teaching cell:** added a cell in `notebooks/displaymv.py`, right after the wedge is
  introduced, showing `i(a, b) == (a ^ b).normalize()` with prose that `bivector_from_vectors(a, b)`
  is exactly `a ^ b` and names the plane; use them when the plane is a means to an end, keep `^` when
  the wedge is the lesson.
- **Adoption at the scaffolding sites** (the only genuine ones per the task's own finding):
  - `notebooks/displaymv.py`: `B = vec_a ^ vec_b` → `MultiVector.bivector_from_vectors(vec_a, vec_b)`
    (the plane then reused across the dual/`B*B`/`B.dual(3)` cells).
  - `tests/test_conformance.py`: `B = vec(n, 0) ^ vec(n, 10)` → `Gn.bivector_from_vectors(vec(n, 0),
    vec(n, 10))` (a bivector fed to `exp`).
- **Kept** every wedge-is-the-subject use (`sym_vec*.wedge(...)` display cells, the `e1e2plane` plane
  cells, the graded expected-value assertions) verbatim — adopting there would erase the lesson.
  `tests/test_unit_bivector_i.py` already covers the helpers directly and was not touched.

## Verification

- Helper equalities confirmed in a `Gn` REPL before editing: `bivector_from_vectors(a,b) == a^b` and
  `i(a,b) == (a^b).normalize()` (2D and 3D), and `Gn.bivector_from_vectors(...)` returns `Gn`.
- Container `make format` (ruff + ty + changelog + epix) all green; container `make test` 697 passed.
- The demo notebook executed past both edited cells (it only hangs on the pre-existing slow
  `n=8 × n=9` symbolic cell, unrelated).

## Ride-along fix: a host/container ruff-format drift (flagged)

Running the container format gate collapsed three stale paren-wrapped lines in `displaymv.py`
(the `(2*e_1 + 3*e_2 + 5*e_1)` / `(2*e_1)*(3*e_3)*…` / `e_1 * ((e_3*e_3)*e_1)` example cells, each
with a long trailing comment). Cause: the **host venv ruff is 0.16.9 but the container/CI ruff is
0.17.0**, and they format a short expression with a long trailing comment differently (0.16.9 wraps,
0.17.0 collapses). Host-side `ruff format` earlier this session left those lines non-container-canonical,
which `make check-format` (container) would have reflowed. Committing the container-canonical form here
fixes the one affected file; the container `ruff format --check` now reports the tree clean. Root-cause
guidance: always run the format gate in-container, or bump the host venv ruff to 0.17.0.

## Open questions

None.
