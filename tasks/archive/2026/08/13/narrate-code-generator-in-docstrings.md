# Narrate the code generator in its own docstrings (co-located story)

**Created:** 2026-08-13 · **Completed:** 2026-08-13

Made the code generator (`tools/gen_specialized.py` + `tools/astbuild.py`)
**human-understandable from the source itself**: the flow of ideas told as a narrative,
co-located with the code it describes. The maintainer's words: "I just don't understand the code as
it is, the generator." The confusion to dispel was whether `Gn` is *parsed*/macro-expanded (the
maintainer's original Lisp-macro idea). It is not: **the generator runs `Gn` on sympy symbols and
keeps the formula that falls out** (partial evaluation / symbolic execution), never touching Gn's
source text.

The durable knowledge lives in the code (the module docstrings), cross-linked with
`tasks/reference/code-generator-architecture.md`; nothing extra needed harvesting.

## Decision: docstrings, not a separate Sphinx doc set

This superseded the "human-readable Sphinx reference for the code generation" effort, recorded in
github.com/billsix/runClaudeInContainer `tasks/archive/2026/08/13/sphinx-human-readable-reference-docs.md`.
Co-locating the story in docstrings and comments:

- **can't drift from the code**: a contributor editing the generator sees and updates it, so the
  markdown↔RST drift check the old task invented was dropped, not built;
- **adds no infrastructure**: no second Sphinx project beside gacalc's `book/docs/`, no second
  `conf.py`/`Makefile`/entrypoint/`output/` target;
- **renders where it's read**: plain text in the source, on GitHub, in `pydoc`.

The dense agent-facing map `tasks/reference/code-generator-architecture.md` stays as the
random-access reference; the module docstring is the narrative front door. The two cross-link.

Three vehicles at three levels of zoom: the **module docstring** tells the story once (top-down
narrative, ASCII pipeline diagram, one doctested trace), never repeated per method; **function
docstrings** are local contracts; **inline comments** carry the non-obvious *why* at the line.

## What was done

- `tools/gen_specialized.py` **module docstring** rewritten: the "one idea" (symbolic execution,
  not parsing/macros), an ASCII pipeline diagram, a live doctest trace (`Gn` on symbols → the
  scalar+bivector formula → why it resolves to `Rotor2`), a three-file map, and the golden rule.
  The naming-conventions legend was kept; a stale line ("committed module") was fixed, since the
  modules are gitignored.
- **Doctests in `tools/` run:** `pytest.ini` `testpaths` was extended to `src tests tools`, so
  `--doctest-modules` executes the generator's trace. `pytest tools` green, `ruff` clean.
- Cross-link added from `tasks/reference/code-generator-architecture.md` to the module docstring
  (and back).
- `tools/astbuild.py` **module docstring** rewritten as the sub-story: why a node DSL, why AST
  instead of string templates, the three casts, and the doc-region-marker machinery (stale builder
  names in it were corrected).
- **Function-level docstrings:** every function in `tools/` was audited. The main top-level
  builders (`resolve`, `product_result`, `dispatch_method`, `product_overload_stubs`,
  `result_block_stmts`, `generate_class`/`_graded_type`/`_scalar`) already had good ones; the three
  gaps were filled: `main` (the driver) and the nested `bilinear` / `linear` full-class builders.
  The trivial DSL one-liners in `astbuild.py` (`name_ref`/`call`/`cast`/...) and the
  well-commented nested closures were deliberately left undocumented (house style: don't
  over-document).
- One line in the `Gn` class docstring (`gn.py`) notes it is the object the generator runs on
  symbols, cross-linked to the pipeline.
- The maintainer reviewed the voice/depth and committed the set (2026-08-13).

## Gotchas found

- **The story goes in `tools/`, never in the generated output.** `g1.py`/`g2.py`/`g3.py` are
  gitignored build artifacts whose method docstrings are copied from `base.py` via
  `inspect.getdoc`; authoring those is a separate job
  (`tasks/archive/2026/09/26/generate-missing-docstrings.md`), done on `base.py`/`gn.py`.
- **Doctest output must be order-stable.** `Gn.__add__` builds its result dict from
  `left.keys() | right.keys()` (a set union), so key order isn't guaranteed across Python builds;
  the trace reads parts by key (`d[()]`, `d[(1, 2)]`) instead of printing the whole dict.
- **ASCII art stays within the 88-col line length** so ruff `E501` doesn't flag it (a line inside a
  docstring can't be cleanly `# noqa`'d). The diagram is ~55 cols.
- **`tools/` doctests need the generated modules present** (`bench.py` imports `g1`/`g2`/`g3` at
  module top). Every collection flow already runs `make generate` first, so this was not a new
  constraint.

## Related

- `tasks/reference/code-generator-architecture.md`: the dense contributor map.
- `tasks/reference/generated-product-typing.md`: the `@typing.overload` rationale.
- `tasks/archive/2026/09/26/generate-missing-docstrings.md`: the separate job of authoring the
  generated classes' method docstrings (via `base.py`, the copy path).
- `tasks/archive/2026/09/26/docstrings-for-sphinx.md`: the package-wide docstring-completeness
  sweep for the book's autodoc, scoped not to overlap this task.
