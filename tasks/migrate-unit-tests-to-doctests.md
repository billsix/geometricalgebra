# Migrate unit tests into doctests where they read well

**Status:** DONE — exhaustive pass complete (William Emerison Six <billsix@gmail.com>, 2026-10-27).
Every test with a clean doctest home is now a doctest; suite **711 → 690**, `make test` / `make
format` green after each batch (the generator was unchanged after the rotate_90 batch, so
`make check-generated` is unaffected since the maintainer last ran it). The tests that remain pytest
**lack a clean doctest home** (documented below), not pending work.
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-10-27 **Updated:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

Every `tests/` unit test with a clean doctest home was pushed into a **doctest** in the library
source, and the redundant pytest test deleted. The suite went **711 → 690**, with **~46 pytest tests
consolidated into doctests** across `vectorcalc`, `measure`, `frame`, `base.py`, `gn.py`, and the g2
code generator; gates green. The doctest wiring already existed (`pytest.ini`: `testpaths = src tests
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

### Exhaustive pass (batches 5–6)

- **`base.reflect`** — reflect across vectors / planes / a one-vector span; removed `test_reflect`.
- **`gn.bivector_from_vectors`** — the un-normalized wedge + parallel→zero; removed 2 from
  `test_unit_bivector_i.py`.
- **`base.blade_latex` / `blade_dict_latex`** — default / explicit-symbol / unmapped LaTeX
  rendering (`blade_dict_latex` made a raw docstring so the backslashes survive); removed 4
  pure-parameter tests from `test_blade_symbols.py` (the session-map / fixture / raises ones stay).
- **`base.__mul__`** — the basis-vector anti-commutation / permutation-sign identities (documentation
  only; `test_multivector_absolute_units` **kept** — it is a broad 2-D/3-D/4-D regression).
- **`base.magnitude` / `base.normalize`** — `|3e_1+4e_2| == 5`, the `3/5, 4/5` unit; removed
  `test_inherited_abc_methods` (`reverse` was already doctested).
- **`base.from_real`** — the scalar blade is `()` (`{(): 7}`); removed `test_scalar_blade_is_the_empty_tuple`.
- **`base.__truediv__`** — `(3e_1+4e_2)/2`; removed `test_scalar_division`.
- **`g2.Vector.sine`** — already doctested in `SINE_METHOD_DOC`; removed 2 from `test_signed_sine.py`.

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
- A doctest that prints coordinate **values** uses a lazy `g2`/`g3` type, not the eager `Gn` (whose
  simplify normalizes numbers to `sympy`, so `list(...)` would print `1.50000…` not `1.5`) — or
  compares with `==` to stay repr-safe.
- A LaTeX doctest needs a **raw** docstring (`r"""`) so `\vec` / `\mathbf` survive as literal
  backslashes (`blade_dict_latex` was converted to raw).

## Kept as pytest (no clean doctest home — not pending)

What remains pytest after the exhaustive pass, each because a doctest cannot cleanly live where it
would need to:

- **`test_coordinate_read`** (x/y/z props): the only home is a generated property docstring built
  directly as an AST constant, and `Vector`'s arity (and which axes exist) differ by dimension — a
  reliable, dim-safe doctest there is fragile.
- **`e_12² = -1`** (`test_versors_are_complex_numbers_2d`) and **`test_versors_are_quaternions_3d`**:
  the home is the generated class-level docstring (shared across every graded class and dimension);
  the quaternion test also asserts operation-driven **type** (`type(x) is Versor`).
- **`.i()` instance** (`test_i_method_on_a_bivector` / `_rotor`): one shared `I_DOC` serves both
  `Bivector.i()` and `Versor.i()`, so a single doctest can't be valid for both roles.
- **`from_blade_dict` silent-drop** (`test_graded_from_blade_dict_keeps_only_own_blades`): the shared
  role-doc runs in every dimension, and `g1.Vector` has no grade-2 blade to drop.
- **`test_multivector_absolute_units`**: a broad 2-D/3-D/4-D product regression (its anti-commutation
  subset is now a `*` doctest; the rest has no single home).
- The large suites — `conformance`, `transforms`, `matrix_template`, `plane_rotation`, `sandwich`,
  `operator_typing`, and the `test_graded` type assertions — stay pytest: parametrized,
  tolerance-based (`isclose` / numpy), `typing.assert_type`, or `raises`. These are the bulk and are
  correctly not doctests.

Migrating the first four would mean editing the generator's docstring-building code (AST-constant
indentation + regen determinism) or splitting a shared doc per role/dimension — fragile for a handful
of small tests. Left as pytest deliberately.
