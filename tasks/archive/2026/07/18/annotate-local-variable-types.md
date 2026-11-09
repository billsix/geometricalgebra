# Add type annotations to local variables & untyped functions

**Created:** 2026-07-18 · **Completed:** 2026-07-18

`ty check` was already clean on `src`, `tests` and `tools`, but ty (like every Python checker) infers
local types, so many annotations lived only in the checker's head. This was a **readability /
pedagogy** pass, not a correctness fix: explicit types make the shapes of GA values (`Vector2`,
`Rotor2`, `Bivector3`, `ComposableFunction[...]`, …) visible to a reader. The principle (the
maintainer left the extent to the agent's discretion): annotate where the type is non-obvious or
pedagogically useful; leave obvious locals alone (`n: int = 3` is noise).

## Audit (2026-07-18)

An `ast`-based audit (`audit.py`, a scratch script, not committed) over every hand-written file
counted untyped params, missing returns and bare local assignments. The raw local counts were an upper
bound: they included module-level type aliases, `__all__`, `__slots__` and loop targets. It corrected
two assumptions of the first draft:

- **Test `-> None` was not universal; it was split per file.** `test_transforms.py` (44 of 44
  missing), `test_generator.py` (21/21), `test_graded.py` (20/23), `test_numeric_magnitude.py` (4/4)
  lacked it; `test_conformance.py`, `test_multivector.py`, `test_subclass_preservation.py` were
  annotated bar a helper; `test_plane_rotation.py` and `test_vector_ergonomics.py` were fully
  annotated.
- **`src/gacalc/` was not fully typed** — ty was clean because it inferred. Gaps: `base.py`
  `from_blade_dict`'s param, the arithmetic dunders' `rhs`/`lhs` params, `__iter__`/`_repr_latex_`
  returns and a nested helper; `functions.py` `compose` and its closures; `gn.py` `from_blade_dict`,
  `as_multivector`/`__post_init__`; `transforms.py` `to_matrix`'s return.

The generated `g1/g2/g3.py`/`scalar.py` were out of scope (a generator change is a separate task).

## What was done

Scope was the widest option considered: notebooks, the mechanical test `-> None` / `setup.py` /
`tools/bench.py` cleanup, **and** the `src/gacalc/` hand-written core — 19 files in all.

- Test functions got `-> None` in the four files lacking it; `setup.py`'s
  `build_py_with_codegen.run` got `-> None`; `bench.py` locals were annotated.
- **Notebooks** (jupytext percent-format, so cells and the `.ipynb` round-trip were kept intact):
  helper signatures (`kind`, `show`, `rotate`) and only the display locals whose GA type is the
  teaching point; scratch/string-table locals were skipped.
- **Tests:** locals polymorphic over a `cls` parameter were typed `MultiVectorBase`, never a concrete
  class; parametrized `cls` params and the `to()` helper's return were left unannotated, preserving the
  gradual typing that dimension-defaulting calls (`dual()`, `unit_pseudoscalar()`) rely on.
- **`nbplotutils.py` plotting locals were skipped**: matplotlib artist glue with no GA value.

## Decisions (each a small standard, carried into
`tasks/archive/2026/07/18/python-programming-standard.md`)

- **`from_blade_dict`'s param became `Mapping[tuple[int, ...], Coef]`, not `BladeCoef` (`dict`).**
  `dict` is invariant in its value type, so callers passing `dict[..., Symbol]` were rejected; the
  method only reads, so the covariant `Mapping` supertype is correct (ty suggested it). Fixed in
  `base.py` and `gn.py`.
- **`__iter__` was deliberately left unannotated**, with an explanatory comment. Typing it
  `Generator[Coef]` made ty treat a multivector as destructurable, so the `case [*sequence]:` patterns
  in `project`/`reject`/`reflect` matched a lone multivector and widened the element type — a false
  positive. A correct annotation that forces edits to unrelated logic isn't worth it in a readability
  pass.
- **Reused-name locals stayed unannotated** (`bench.py` `sa`/`sb`, assigned a `Gn` then a
  `MultiVectorBase`): flow inference handles them; one declared type can't.
- **`_same_value` (test_conformance) was wrapped in `sympy.sympify(...)`**, mirroring the sibling
  `simplify_equal` (test_graded): once its params were typed, `Coef` arithmetic no longer matched
  `sympy.simplify`'s overloads.

## Verification

`make format`: **ty clean on src, tests, tools**; `make test`: **285 passed**. Ruff reported zero new
errors; its 6 `E501`s were pre-existing prose lines in `notebooks/displaymv.py`, byte-identical to
HEAD, and were left untouched.
