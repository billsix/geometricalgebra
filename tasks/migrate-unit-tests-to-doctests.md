# Migrate unit tests into doctests where they read well

**Status:** done to the agreed scope (William Emerison Six <billsix@gmail.com>, 2026-10-27). The
reasonable migration landed and all three gates pass — `make test`, `make format`,
`make check-generated`. The remaining long tail is **parked by decision** (below), not pending work.
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-10-27 **Updated:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

As many `tests/` unit tests as read well were pushed into **doctests** in the library source, and the
redundant pytest tests deleted. The suite went **711 → 695**, with **~34 pytest tests consolidated
into doctests** across `vectorcalc`, `measure`, `frame`, `base.py`, and the g2 code generator; the
three gates are green. The doctest wiring already existed (`pytest.ini`: `testpaths = src tests
tools`, `addopts = --doctest-modules`), so a `>>>` example in `src`/`tools` runs automatically — the
work was migration, not plumbing.

## Decision — consolidate

When a doctest covers a pytest case, the pytest duplicate was **deleted**, and any `pinned by
tests/…` / `proved in tests/…` doc reference it left dangling was fixed in the same change. (Chosen
over keep-both; the repo had been carrying both.)

## What was migrated

- **`vectorcalc.cross`** — already carried most doctests; added the general-anticommutative, `Gn`,
  and method-form examples, and repointed the "sign pinned by tests/…" note at the doctests. Removed
  6 duplicates from `test_vectorcalc.py`.
- **`measure`** (`content` / `area` / `volume` / `signed_area` / `signed_volume`) — already
  doctested; filled the few missing example lines (length, unit square/cube, oblique area, content
  aliases, coplanar→0, `abs(signed) == content`, parallel/coplanar signed→0). Removed 8 duplicates
  from `test_measure.py`.
- **`frame.is_frame`** — new doctest (single / 2-D / 3-D / oblique / parallel / coplanar / repeat /
  empty). Removed 3 duplicates from `test_frame.py`.
- **`base.py`** — new doctests on `dot`, `wedge`, `unit_pseudoscalar` (the i² sign pattern, n = 1..15),
  `project`, `reject`, `is_vector`, `is_bivector`, `is_orthogonal_to`, `is_parallel_to`, `cosine`,
  `reverse`, and `coefficient`. Removed 11 duplicates from `test_multivector.py` and 1 from
  `test_graded.py` (`test_coefficient_readback`).
- **g2 generator** — extended the generated `rotate_90_degrees` method and factory docstrings in
  `tools/gen_specialized.py` (`CUSTOM_METHOD_DOCS["vector|rotate_90_degrees"]` and
  `ROTATE_90_FACTORY_DOC`) with the pseudoscalar / symbolic / direction / inverse / composition
  identities, and regenerated. Removed 5 duplicates from `test_rotate_90_degrees.py`.

## gacalc-specific gotchas

The general, cross-project version of these lessons lives in
`~/.claude/reference/doctests-by-default.md` (github.com/billsix/runClaudeInContainer); the
gacalc-specific points:

- Doctests on the specialized classes are authored in `tools/gen_specialized.py` and **regenerated**
  — never hand-edited into the gitignored `g*.py`. A grade-1 `Vector` exposes `e_1` but not the
  bivector `e_12`; use `Bivector.e_12` in a vector-method doctest.
- ruff **E501** counts doctest lines (88 cols). Wrap a long statement with a `...` continuation or
  trim the inline comment.
- `test_multivector_add` / `test_multivector_subtract` carry a `# doc-region-end test add` marker
  (a book literalinclude source) and were **left untouched** — deleting them would break the book
  and `make check-regions`.

## Parked — the remaining long tail (by decision, not pending)

Each item is either entangled with a non-doctestable assertion or needs disproportionate generator
work, so it was deliberately not migrated:

- `test_multivector.py`: `reflect`, `rotate`, and the 3-D `absolute_units` permutation identities.
- `test_graded.py`: the operation-driven **type** assertions (`type(x) is …`) stay pytest; `e_12² =
  -1` is clean but its only doctest home is the generated class-level docstring (shared across every
  graded class and dimension) — awkward for marginal gain.
- A few clean one-liners remain in `test_unit_bivector_i`, `test_vector_ergonomics`,
  `test_blade_symbols`, `test_blade_dict`, `test_signed_sine` if more is ever wanted.
- The large numeric / transform suites (`conformance`, `transforms`, `matrix_template`,
  `plane_rotation`, `operator_typing`, `sandwich`) stay pytest — parametrized, tolerance-based
  (`isclose` / numpy), `typing.assert_type`, or `raises`.
