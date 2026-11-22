# Annotate every binding in the doctests

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## BLUF

gacalc annotates every binding in its source, tests and notebooks, but not inside its
docstring examples: 184 hand-written `>>> name = …` lines carry no type, against 2 that do.
Give every doctest binding its type, the same way the rest of the code does, in the
hand-written modules and in the docstrings the generator emits. Then teach
`tools/check_annotations.py` to report a doctest binding that lacks one. Done = no bare
doctest binding remains in `src/` or `tools/`, the checker lists none, and `make format`,
`make test`, `make check-generated` and `make check-regions` pass.

## The request (2026-11-22, the maintainer's words)

> make a task to add types in doctests the way I want types added everywhere else.

## Context

- The rule: the shared Python standard, `tasks/reference/python-coding-standard.md` in
  github.com/billsix/runClaudeInContainer, section "Type annotations — annotate every
  binding". Since 2026-11-22 it says in so many words that a doctest is code under the rule,
  and that an unpacked name is declared on its own `>>>` line above. The sibling
  `doctests-by-default.md` in the same repo has said so since 2026-10-27 ("Annotate every
  binding IN the doctest too").
- gacalc's own rules: `CLAUDE.md`, "Coding standard (Python)" (every binding typed; each name
  of a `sympy.symbols` unpack declared on the line above, as `tests/` does 141 times), and
  `tasks/reference/type-annotation-exemptions.md` (what `tools/check_annotations.py` reports
  and what it exempts).
- `pytest.ini` runs every docstring example (`--doctest-modules` over `src`, `tests`, `tools`),
  so a wrong edit fails `make test`. `ty` does not read inside a docstring, so a wrong *type*
  in a doctest annotation is caught by nothing today.
- A doctest runs in its module's namespace. A type an annotation names must be importable
  there, or imported on a `>>>` line of the example (`base.py`'s examples already carry 110
  such import lines).
- The generated modules (`src/gacalc/g1.py`, `g2.py`, `g3.py`, gitignored) get their docstrings
  from `tools/gen_specialized.py`: the `CUSTOM_METHOD_DOCS` table and the
  `inject_method_docstrings` pass (`tasks/reference/generated-docstrings.md`). Fix the
  generator and regenerate; never edit the output.

## Where the bare bindings are (counted 2026-11-22)

Hand-written, `>>> name = …` or `>>> a, b = …` with no annotation:

| file | bare | annotated |
|---|---|---|
| `src/gacalc/base.py` | 78 | 0 |
| `src/gacalc/transforms.py` | 40 | 0 |
| `src/gacalc/functions.py` | 16 | 0 |
| `src/gacalc/measure.py` | 12 | 0 |
| `src/gacalc/frame.py` | 11 | 0 |
| `src/gacalc/nbdisplay.py` | 10 | 0 |
| `src/gacalc/standardposition.py` | 6 | 0 |
| `src/gacalc/vectorcalc.py` | 4 | 0 |
| `src/gacalc/gl/grapher3d.py` | 3 | 2 |
| `src/gacalc/gn.py` | 2 | 0 |
| `src/gacalc/cayley/cayleygraph.py` | 1 | 0 |
| `src/gacalc/cayley/cayleyscene.py` | 1 | 0 |

42 of those lines are tuple unpacks, nearly all `sympy.symbols`.

Generated: `g1.py` 27 bare, `g2.py` 40, `g3.py` 38. Some emitted examples are already typed
(`>>> v: Vector = 2 * Vector.e_1 + 3 * Vector.e_2` in `tools/gen_specialized.py`); the
symbol unpacks and the rest are not. The book pages and `README.md` have no `>>>` examples.

## How each binding is written

- A single binding takes its type inline: `>>> residue: Versor = Versor(coeff_scalar=173.6, …)`.
  Use the type the code around it would use: the graded type where the value is one, the
  abstract base for a polymorphic value, a parameterized generic (`dict[Blade, Real]`), never a
  bare one.
- An unpack declares each name on its own line above, as the tests do:

  ```
  >>> a: sympy.Symbol
  >>> b: sympy.Symbol
  >>> a, b = sympy.symbols("a b")
  ```

  This adds a line per name to the rendered API docs. It is the house form, so it is used; where
  an example needs one symbol, `>>> a: sympy.Symbol = sympy.Symbol("a")` is shorter and equal.
- A continuation line (`...`) belongs to the binding that opened it and takes nothing.
- Loop, `with` and comprehension targets stay inferred, as everywhere else.
- Add a `>>> from … import …` line for a type the annotation names when the module's namespace
  lacks it.

## Plan

1. Extend `tools/check_annotations.py`: for each docstring, parse the examples with
   `doctest.DocTestParser`, parse each example's source with `ast`, and report a bare `Assign`
   (and an unpack whose names were not declared in the same docstring) as a row, like any other
   missing annotation. It stays a report, not a gate. Run it first; its rows are the worklog.
2. Hand-written modules, one file at a time, largest last; `make test` after each (the
   doctests run there).
3. The generator: `CUSTOM_METHOD_DOCS` and whatever `inject_method_docstrings` emits; then
   `make generate`, and read the regenerated `g2.py` examples.
4. Check the types, since `ty` cannot: write the examples of each module out to a scratch `.py`
   file and run `ty check` on it. Fix any annotation it rejects. Keep the extractor under
   `tasks/adhoc/annotate-doctest-bindings/` if it is more than a few lines.
5. Gates: `make format`, `make test`, `make check-generated`, `make check-regions`, `make docs`
   (the API pages render the examples).
6. Doc deltas: a line in `tasks/reference/type-annotation-exemptions.md` (doctest examples are
   now covered) and in `CLAUDE.md`'s "every binding typed" bullet (it names notebooks and
   tests; add docstring examples). No `CHANGELOG.md` entry: no public name or behaviour changes.

## History

All on 2026-11-22 (William Emerison Six <billsix@gmail.com>).

1. Asked for together with a change to the shared Python standard, which now says a doctest is
   code under "annotate every binding" (github.com/billsix/runClaudeInContainer, and its two
   copies in github.com/billsix/runCrushInContainer).
2. The bare bindings were counted, by file and in the generated modules. No question was open:
   an unpack declares each name above, as the tests do, and the checker is extended because
   `ty` does not read docstrings.
