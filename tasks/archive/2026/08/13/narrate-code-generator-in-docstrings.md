# Narrate the code generator in its own docstrings (co-located story)

**Status:** COMPLETED 2026-08-13 — narrative + docstrings landed and committed; archived.
The durable knowledge lives in the code (the `tools/gen_specialized.py` / `astbuild.py`
module docstrings) cross-linked with `tasks/reference/code-generator-architecture.md`, so
this archives as a lean work record with nothing extra to harvest.
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-08-13

## Goal

Make the code generator (`tools/gen_specialized.py` + `tools/astbuild.py`)
**human-understandable from the source itself** — the flow of ideas, told as a
narrative, co-located with the code it describes. Bill's words: "I just don't
understand the code as it is, the generator." The specific confusion this must
dispel: whether `Gn` is *parsed*/macro-expanded (his original Lisp-macro idea) or
something else. It is something else — **the generator runs `Gn` on sympy symbols
and keeps the formula that falls out** (partial evaluation / symbolic execution),
never touching Gn's source text.

## Why this, and not a separate Sphinx doc set

This **supersedes** the "human-readable Sphinx reference for the code generation"
effort (runClaudeInContainer `tasks/sphinx-human-readable-reference-docs.md`,
archived 2026-08-13). Co-locating the story in docstrings/comments:

- **Can't drift from the code** — it lives next to what it describes, so a
  contributor editing the generator sees and updates it. This is the lowest-drift
  option, and it makes the markdown↔RST drift-check obligation the old task
  invented **unnecessary** (dropped, not built).
- **Adds no infrastructure** — no second Sphinx project beside gacalc's existing
  `book/docs/` book, no second `conf.py`/`Makefile`/entrypoint/`output/` target.
- **Renders where it's read** — plain text in the source, on GitHub, in `pydoc`.

The dense agent-facing map `tasks/reference/code-generator-architecture.md` stays
as the random-access reference; the module docstring is the narrative front door
you graduate *from*. The two cross-link each other.

## Approach — three vehicles, three levels of zoom

- **Module docstring = the story.** Top-down narrative + ASCII pipeline diagram +
  one doctest'd worked trace. Told once, at the top. Must NOT be repeated in every
  method (that recreates the density problem).
- **Function/method docstrings = local contracts.** What *this* builder does and
  why, read at the point you're looking at it. Stay local; don't re-tell the story.
- **Inline comments = the non-obvious *why* at the exact line.** Already heavy.

## Done so far (2026-08-13)

- [x] `tools/gen_specialized.py` **module docstring** rewritten: the "one idea"
      (symbolic execution, not parsing/macros), an ASCII pipeline diagram, a live
      doctest trace (`Gn` on symbols → the scalar+bivector formula → why it
      resolves to `Rotor2`), a three-file map, and the golden rule. Kept the
      existing naming-conventions legend. Fixed a stale line ("committed module" →
      the modules are gitignored).
- [x] **Doctests in `tools/` now run.** `pytest.ini` `testpaths` extended to
      `src tests tools` so `--doctest-modules` executes the generator's trace like
      any other docstring example. Verified: `pytest tools` green, `ruff` clean.
- [x] Cross-link added in `tasks/reference/code-generator-architecture.md` →
      the module docstring (and the reverse pointer is in the docstring).
- [x] `tools/astbuild.py` **module docstring** rewritten as the sub-story: why a
      node-DSL, why AST instead of string templates, the three casts, and the
      doc-region-marker machinery — cross-linked to the reference doc and the
      `gen_specialized.py` pipeline. (Also corrected stale builder names in it.)
- [x] **Function-level docstrings** — audited every function in `tools/`. The
      load-bearing top-level builders (`resolve`, `product_result`,
      `dispatch_method`, `product_overload_stubs`, `result_block_stmts`,
      `generate_class`/`_graded_type`/`_scalar`) already had good ones. Filled the
      three genuine gaps: `main` (the driver), and the nested `bilinear` / `linear`
      full-class builders. **Deliberately left undocumented** per the house style
      ("don't over-document"): the trivial DSL one-liners in `astbuild.py`
      (`name_ref`/`call`/`cast`/...) and the well-commented nested closures — the
      module docstrings + inline comments already cover them.

## Remaining

- [x] One `gn.py` line noting it's the object the generator runs on symbols —
      added to the `Gn` class docstring, cross-linked to the generator's pipeline.
- [x] Bill reviewed the voice/depth and committed the set (2026-08-13); task archived.

## Gotchas (verified while doing the first slice)

- **Story goes in `tools/`, never in the generated output.** `g1.py`/`g2.py`/
  `g3.py` are gitignored build artifacts, and their *method* docstrings are copied
  from `base.py` via `inspect.getdoc`. Authoring generated-method docstrings is a
  different task (`generate-missing-docstrings.md`), done on `base.py`/`gn.py`.
- **Doctest output must be order-stable.** `Gn.__add__` builds its result dict from
  `left.keys() | right.keys()` (a *set* union), so the dict's key order isn't
  guaranteed across Python builds — the trace reads parts by key (`d[()]`,
  `d[(1, 2)]`) instead of printing the whole dict.
- **Keep ASCII art within the 88-col line length** so ruff `E501` doesn't flag it
  (you can't cleanly `# noqa` a line inside a docstring). The pipeline diagram is
  ~55 cols.
- **`tools/` doctests need the generated modules present** (`bench.py` imports
  `g1`/`g2`/`g3` at module top). Every collection flow already runs `make generate`
  first, so this is not a new constraint — but a bare `pytest` with no prior
  generate will fail collection, same as the existing suite.

## See also

- `tasks/reference/code-generator-architecture.md` — the dense contributor map
  (cross-linked; the narrative front door points here and vice versa).
- `tasks/reference/generated-product-typing.md` — the `@typing.overload` rationale.
- `tasks/generate-missing-docstrings.md` — the *separate* job of authoring the
  generated classes' method docstrings (via `base.py`, the copy path).
- runClaudeInContainer `tasks/archive/2026/08/13/sphinx-human-readable-reference-docs.md`
  — the superseded separate-Sphinx-doc-set task.
- gacalc `tasks/docstrings-for-sphinx.md` — the (open, rescoped) package-wide
  docstring-completeness sweep for the book's autodoc; scoped to not overlap this task.
