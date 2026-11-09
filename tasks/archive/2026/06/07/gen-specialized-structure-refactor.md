# Refactor `tools/gen_specialized.py` structure for clarity

**Created:** 2026-06-07 · **Completed:** 2026-06-07

## Background

`tools/gen_specialized.py` had just been rewritten from string concatenation to hand-built `ast` nodes
(alternative C of `tasks/archive/2026/06/07/codegen-via-python-ast.md`, committed as "completed C").
It was correct and verified, but its ~1790 lines had grown in waves across A → B → C: node-builders sat
in three separate blocks, `generate_scalar` was stranded mid-file among helpers, docstring text was
scattered, and `generate_class` / `generate_graded_type` duplicated structure. This task changed only
the generator's internal clarity, never its output.

**Invariant held at every step:** the generated `scalar/g1/g2/g3.py` stayed AST-identical to the
baseline and run-to-run byte-identical (`make check-generated`), and the full suite (161 tests), `ruff`
and `ty check src tests` stayed green.

## What was done

- **#1 + #2 — one top-down layering.** `generate_scalar` was moved to the generators region and the
  whole file reordered into 8 banner-delimited sections: AST emission primitives → node-builder DSL →
  GA utilities → docstrings → type registry + resolution + value policies → shared class/method
  builders → the four generators → headers/driver. A script captured each top-level node's source and
  re-emitted them in order, asserting every node was covered. Pure movement.
- **#3 — shared builders.** The duplication was extracted into `class_header(doc, n, blades)`,
  `is_close_method(name, fields)`, `iter_method(name, blades)` and `grades_method(grade_groups)` (the
  grade set is passed in, since the full class covers `0..n` and a graded type only its present grades).
  `reverse` was deliberately not merged: the full class emits a `result =` local, the graded type
  returns the cast directly.
- **#4 — named the two return idioms:** `return_construct(name, pairs)` for the direct
  `return cast(Self, Name(...))`, kept distinct from the `result`-local variant.
- **#5 — all docstring text and builders** (`SCALAR_DOC`, `PLANE_DOC`, `DOCSTRINGS`,
  `generic_docstring`, `docstring_for`, `graded_docstring`, …) moved into one "Docstrings" section.
- An orphaned `EQ_METHOD` comment was removed, and `from __future__ import annotations` was added so the
  reorder's forward references (e.g. `graded_docstring(spec: TypeSpec)` before `TypeSpec`) are valid and
  ruff-clean rather than relying on Python 3.14's PEP 649. The file went from ~1790 to 1773 lines.
- **#6 — naming convention,** so a name predicts its return type: `*_method` → `FunctionDef` (all
  annotated `-> ast.FunctionDef`), `*_stmt` → one statement, `*_stmts` → `list[stmt]`, `*_value` → expr.
  The misleading `dispatch_nodes` → `dispatch_method` rename was committed first; the rest were
  `scaled_nodes→scaled_stmt`, `unary_nodes→unary_stmt`, `result_block_nodes→result_block_stmts`,
  `result_return→result_stmts`, `method_doc→method_doc_stmts`, `class_doc→class_doc_stmt`,
  `class_header→class_header_stmts`. Already-clear names (`field_decls`, `dimension_decl`,
  `coerce_pair_gn`, `rename_map`, `*_call`, `dim_or_n`) and the DSL primitives kept their names.
- **#7 — `main()` consistency:** the scalar module's `__all__` became node-built like
  `generate_constants`'. That removed the last `parse_stmts` user, so `parse_stmts` and the unused
  `textwrap` import were deleted.
- **#8 — the domain-agnostic DSL moved to `tools/astbuild.py`** (215 lines, 28 builders:
  `parse_expr`/`module_source`/`SymbolToAttr`, `nm`/`dot`/`lit`/`call`/`cast*`/`ret`/`fn`/`cls`/
  `ann_assign`/`assign`/`construct`/`return_construct`/`bool_or`/`bool_and`/…). `gen_specialized.py`
  imports it (`tools/` is on `sys.path` as the script's own dir; the generator only runs as a script)
  and keeps `expr_to_ast` and all GA logic; it shrank from ~1773 to 1611 lines. `astbuild.py` carries
  the license header and a docstring noting it knows the output's `Self`/`Real` cast conventions but
  nothing about GA.
- **Docs:** CLAUDE.md "Module layout" lists `tools/astbuild.py`; "Code generation" describes the AST
  build, the DSL and the raw-header caveat (the CLAUDE.md item pending from the AST rewrite task).

## Deliberately not changed

- The value-policy split (`summed_value` / `result_value` / `unary_value`): it mirrors three different
  cast/term-order policies, and merging would change the output.
- `expr_to_ast` + `SymbolToAttr`, and the `TypeSpec` / `resolve` registry.

## Verification

After every step the generator ran (the `astbuild` import resolves in script mode), the output was
AST-identical to the baseline, `make check-generated` was deterministic, the full suite passed (161),
and `ruff` (both files) and `ty` (src + tests) were clean.
