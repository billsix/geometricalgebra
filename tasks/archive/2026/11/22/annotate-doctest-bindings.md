# Annotate every binding in the doctests

**Status:** done 2026-11-22
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## What this did

gacalc annotated every binding in its source, tests and notebooks but not inside its docstring examples.
Now every `>>> name = …` binding in `src/` and `tools/` carries its type, and each unpacked name is declared on its
own `>>>` line above the unpack, as `tests/` does.

- **`tools/check_annotations.py`** reports a bare doctest binding as a `DOCTEST` row (it parses each docstring
  with `doctest.DocTestParser`, then each example with `ast`). It is still a report, not a gate. It lists none now.
- **Hand-written modules:** 182 bindings typed in `base`, `transforms`, `functions`, `measure`, `frame`, `nbdisplay`,
  `standardposition`, `vectorcalc`, `gn`, `cayley/cayleygraph`, `cayley/cayleyscene` and `gl/grapher3d`.
  A value's type is its runtime class (`Vector`, `Versor`, `Gn`, `sympy.Symbol`); a polymorphic result takes the
  function's declared return type (`w: MultiVectorBase = MultiVector.reflect(across=u)(v)`); a generic is always
  parameterized (`InvertibleFunction[float]`, `CayleyGraph[Space]`, never the bare class). Where a name was missing
  from the example's namespace, an import line was added to the example.
- **Generated modules:** the examples that `tools/gen_specialized.py` emits are typed at their source, so
  `g1.py`, `g2.py` and `g3.py` have none bare after `make generate` (`InvertibleFunction[Vector]` for the line maps,
  `ComposableFunction[Vector]` for `project`, `sympy.Symbol` declarations for the unpacks).
- **Line length:** a typed binding is longer, and `ruff` holds docstring lines to 88 columns, so 26 examples
  are wrapped as `>>> x: T = (` / `...     value` / `... )`.
- **Two examples changed shape, not just type:** `compose_intermediate_fns` returns an `Iterable`, but its
  example indexes the result, so it is `list(compose_intermediate_fns(...))`; the `MODEL.fill` result in
  `to_matrix_template` is named `filled`, because `m` was already the `sympy.Symbol` of the same example.
- **Docs:** `tasks/reference/type-annotation-exemptions.md` (doctest examples are covered; the floor for the
  `DOCTEST` kind is zero) and the "every binding typed" bullet of `CLAUDE.md`. No `CHANGELOG.md` entry: no public
  name or behaviour changes.

## Verification

`tasks/adhoc/annotate-doctest-bindings/annotate.py` made the edit by running each example in its module's
namespace and reading the type of what it bound; run once on the unmodified files it reproduced the diff
(including `tools/gen_specialized.py`). The examples were then written to a scratch module and checked with
`ty`, which does not read docstrings. That found three wrong annotations (a reflection's result typed as `Gn`,
the `to_matrix` result typed as `ndarray` only, and the `Iterable` above); the only complaints left are two
`sympy.simplify` overloads on lines this task did not change. `make format`, `make test` (1407 passed, so every
annotation evaluates in its example), `make check-generated`, `make check-regions` and `make docs` passed.
The extractor that fed `ty` was a one-shot script and is in git history with the codemod.
