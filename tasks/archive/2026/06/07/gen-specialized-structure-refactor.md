# Refactor `tools/gen_specialized.py` structure for clarity

**Status:** complete — **#1–#8 all done + verified; CLAUDE.md refreshed.** #1–#4 committed
("completed 1-4"); #7/#8/docs committed; the `dispatch_nodes→dispatch_method` rename committed; the full
#6 naming pass done this round (awaiting author commit). Output stayed AST-identical to baseline at
every step; `make check-generated` + 161 tests + `ruff`/`ty` green throughout. Ready to archive.
**Started:** 2026-06-07
**Completed:** 2026-06-07

## Done: #7, #8, docs (2026-06-07, after the #1-#4 commit)

- **#7 — `main()` `__all__` consistency.** The scalar module's `__all__` is now node-built
  (`assign("__all__", ast.List([lit("Scalar")]))`) like `generate_constants`, not `parse_stmts`. That
  removed the last `parse_stmts` user, so `parse_stmts` and the now-unused `textwrap` import were
  deleted and the stale `main()` comment fixed.
- **#8 — split the node-builder DSL into `tools/astbuild.py`** (215 lines): the 28 generic builders
  (`parse_expr`/`module_source`/`SymbolToAttr` + `nm`/`dot`/`lit`/`call`/`cast`/`cast_self`/`cast_real`/
  `ret`/`subscript`/`opt_int`/`arg`/`fn`/`cls`/`dataclass_decorator`/`ann_assign`/`assign`/
  `isinstance_`/`not_`/`ne_zero`/`construct`/`return_construct`/`bool_or`/`bool_and` + `_LOAD`/`_STORE`).
  `gen_specialized.py` imports them (`from astbuild import (...)`; `tools/` is on `sys.path` as the
  script's own dir — the generator only runs as a script / subprocess, never imported as a module) and
  keeps `expr_to_ast` (the sympy→ast bridge) plus all GA logic. Generator dropped from ~1773 → 1611
  lines; the DSL is now reusable + independently inspectable. `astbuild.py` carries the GPL header + a
  docstring noting it knows the output's `Self`/`Real` cast conventions but nothing about GA.
- **Docs — CLAUDE.md refreshed:** "Module layout" now lists `tools/astbuild.py` and notes the generator
  builds via `ast` nodes + `ast.unparse`; "Code generation" describes the AST build + the `astbuild`
  DSL + the raw-header caveat. (This also satisfies the pending CLAUDE.md item noted in
  `tasks/codegen-via-python-ast.md`.)

**Verified after every step:** generator runs (the `astbuild` import resolves in script mode), output
AST-identical to the original baseline, `make check-generated` deterministic, full suite **161 passed**,
`ruff` (both files) + `ty` (src+tests) clean.

## Done: #6 (2026-06-07)

Builder-naming convention settled so a name predicts its return type:
- **The misleading one first (committed separately):** `dispatch_nodes` → `dispatch_method` (it returns a
  whole `FunctionDef`, not "nodes").
- **Full pass:** `*_method` → `FunctionDef` (and all such builders now annotate `-> ast.FunctionDef`:
  `eq_method`/`from_blade_dict_method`/`to_blade_dict_method`/`is_close_method`/`iter_method`/
  `grades_method`/`dispatch_method`); `*_stmt` → one statement, `*_stmts` → `list[stmt]`; `*_value` →
  expr. Renames: `scaled_nodes→scaled_stmt`, `unary_nodes→unary_stmt`,
  `result_block_nodes→result_block_stmts`, `result_return→result_stmts`,
  `method_doc→method_doc_stmts`, `class_doc→class_doc_stmt`, `class_header→class_header_stmts`. The
  already-clear names kept: `field_decls`/`dimension_decl`/`coerce_pair_gn`/`rename_map`/`*_call`/
  `dim_or_n`, and the `astbuild.py` DSL primitives (conventionally named).
- Verified: output AST-identical to baseline, `make check-generated` deterministic, `ty` (src+tests)
  clean, `ruff` clean, full suite **161 passed**.

**All of #1-#8 are now done.** This task is complete and ready to archive.

## Done: #1–#4 (2026-06-07)

- **#1 + #2 — moved `generate_scalar` and reordered the whole file into 8 banner-delimited sections**
  (AST emission primitives → node-builder DSL → GA utilities → docstrings → type registry +
  resolution + value-policies → shared class/method builders → the four generators → headers/driver).
  Done with a script that captures each top-level node's source and re-emits them in the target order
  (asserting every node is covered, so nothing was dropped). Pure movement — output unchanged.
- **#3 — extracted the `generate_class` / `generate_graded_type` duplication** into
  `class_header(doc, n, blades)`, `is_close_method(name, fields)`, `iter_method(name, blades)`,
  `grades_method(grade_groups)`. Both generators now call them; the parts that actually differ
  (products / dispatch) stand out.
- **#4 — added `return_construct(name, pairs)`** for the direct `return cast(Self, Name(...))` idiom and
  used it (graded `reverse`, the `r_vector_part` fallthrough, …). The with-a-`result`-local variant
  stays `result_return` (different output; kept distinct).
- **#5 (incidental)** — all docstring text + builders (`SCALAR_DOC`, `PLANE_DOC`, `DOCSTRINGS`,
  `generic_docstring`, `docstring_for`, `graded_docstring`, `method_doc`, `class_doc`) now live in one
  "Docstrings" section.
- Also: removed an orphaned `EQ_METHOD` comment left by an earlier deletion; **added
  `from __future__ import annotations` to the generator** — needed so the reorder's annotation
  forward-refs (e.g. `graded_docstring(spec: TypeSpec)` now precedes `TypeSpec`) are lazy/valid and
  ruff-clean (was relying on Python 3.14's PEP 649 deferred annotations).

**Verified after every step:** output AST-identical to the original baseline (`/tmp/ast-ref`),
`make check-generated` deterministic, full suite **161 passed**, `ruff`/`ty` (src+tests) clean. File is
1773 lines (was ~1790; the extraction net-removed duplication despite added shared builders).

**Remaining:** #6 naming convention, #7 `main` `__all__` consistency, #8 split the node-builder DSL into
`tools/astbuild.py`. (Next-steps conversation, per the author.)

## Context

`tools/gen_specialized.py` was rewritten from string-concatenation to the Python `ast` module in three
committed alternatives (see `tasks/codegen-via-python-ast.md`): A (minimal — NodeTransformer rename +
`ast.unparse` emission), B (template-splice), C (hand-built `ast` nodes). The author committed **C** as
the chosen approach (commit "completed C"); the dev-only parity harness `tools/_ast_parity.py` was
removed afterward.

The generator now (~1790 lines) builds every module as `ast` nodes and renders them with `ast.unparse`;
the file header (copyright + imports) stays raw text (comments can't live in an AST). It is **correct
and verified** — but its structure grew in waves across A→B→C and shows it: helpers are scattered, one
generator is stranded mid-file, and the two big generators duplicate structure. This task is purely
about **internal clarity of the generator** — it must not change the generated output at all.

**Hard invariant for every step:** the generated `scalar/g1/g2/g3.py` must stay byte-identical
(run-to-run) — guarded by `make check-generated` (regenerate twice, `cmp`) — and the full suite
(`python -m pytest -q`, 161 tests) + `ruff` + `ty check src tests` must stay green. (The old
`_ast_parity.py` that compared against the original *string* generator is gone and not regenerable; the
behavioural guard is the test suite + determinism check.) Work incrementally, re-running those after
each step.

## Current structure (map, with line numbers as of 2026-06-07)

The reading order is jumbled — note where `generate_scalar` and the helper groups fall:

- AST emission primitives — `parse_stmts`/`parse_expr`/`module_source`/`SymbolToAttr`/`expr_to_ast` (66–107)
- node-builder DSL, block 1 — `nm`/`dot`/`lit`/`call`/`cast`/`ret`/`fn`/`cls`/`ann_assign`/… + `eq_method` (116–329)
- `SCALAR_DOC` + **`generate_scalar`** (331–602)  ← stranded among helpers
- value-policy builders — `_is_neg_term`/`summed_value`/`result_value`/`unary_value` (603–641)
- node-builder DSL, block 2 — `rename_map`/`result_return`/`field_decls`/`dimension_decl`/
  `from_blade_dict_method`/`to_blade_dict_method`/`bool_or`/`bool_and`/`isclose_call`/`super_call`/`dim_or_n` (643–751)
- GA utilities — `out_path`/`blades_for_dim`/`field_name`/`blade_of_field`/`term_grade_key` (753–806)
- docstrings — `_sub`/`_sup`/`generic_docstring`/`docstring_for`/`DOCSTRINGS` (808–895)
- TypeSpec registry — `graded_specs`/`full_spec`/`registry_for_dim`/`resolve`/`product_result`/`unary_result` (897–984)
- **`generate_class`** (986–1221)
- `graded_docstring`/`full_name_for` (1223–1246)
- node-builder DSL, block 3 (graded) — `scaled_nodes`/`result_block_nodes`/`unary_nodes`/`_match_class`/`dispatch_nodes` (1248–1336)
- `PLANE_DOC` + **`generate_graded_type`** (1338–1617)
- **`generate_constants`** (1619–1643)
- `header`/`_coerce`/`SCALAR_HEADER`/`ALGEBRAS` (1645–1732)
- `ruff_format`/`main` (1734–end)

## Findings & proposed refactorings

### High-value, low-risk (clarity)

1. **Move `generate_scalar` down to the generators region.** It sits at 340, stranded between the DSL
   and the value/utility helpers (it landed there because it was built first). It belongs with
   `generate_class` / `generate_graded_type` / `generate_constants` so there is one "generators" region.

2. **Reorder the scattered helpers into a strict top-down layering.** Node-builders are in three blocks
   (116–329, 643–751, 1248–1336); value-policies sit between `generate_scalar` and more helpers; GA
   utilities + docstrings come *after* `generate_scalar`. Target order:
   1. AST emission primitives
   2. the **whole** node-builder DSL (one block)
   3. GA-domain utilities (`blades_for_dim`/`field_name`/`blade_of_field`/`term_grade_key`)
   4. **all** docstring text + builders (see #5)
   5. TypeSpec registry + `resolve` + `product_result`/`unary_result` + the value-policy builders
   6. shared class/method builders (see #3)
   7. the four `generate_*` functions together
   8. `header`/`SCALAR_HEADER`/`_coerce`/`ALGEBRAS`/`ruff_format`/`main`

3. **Extract the duplication between `generate_class` and `generate_graded_type`.** Both inline
   structurally-identical methods. Factor:
   - `class_header(name, n, doc, blades)` → the common prefix list: dataclass decorator setup +
     `class_doc` + `dimension_decl` + `*field_decls` + `from_blade_dict_method` + `to_blade_dict_method`
     + `eq_method()`.
   - `is_close_method(name, fields)` — identical shape in both (only name/fields differ).
   - `iter_method(name, blades)` — identical (per-blade `if self.f != 0: yield Name(f=self.f)`).
   - `grades_method(grade_groups)` — same shape; the *grade set* differs (`generate_class` covers
     grades `0..n`, graded covers only present grades), so pass the grouping in.
   This shortens both generators and makes the part that differs (the products / dispatch)
   stand out. NB: `reverse` differs in output (full class emits a `result =` local; graded returns the
   `cast` directly) — keep two variants or parametrize, don't force-merge.

4. **Name the two "return a constructed value" idioms.** `ret(cast_self(construct(name, pairs)))` is
   inlined ~dozens of times; `result_return` is the variant that emits a `result =` local first. Add a
   `return_construct(name, pairs)` for the direct form and use it consistently so both idioms are named.

5. **Consolidate the docstrings.** `SCALAR_DOC` (331), `PLANE_DOC` (1338),
   `DOCSTRINGS`/`generic_docstring`/`docstring_for` (845), and `graded_docstring` (1223) are scattered.
   Put all docstring text + builders in one section.

### Medium (consistency)

6. **Settle a builder-naming convention.** Currently mixed: `*_method` (returns `FunctionDef`),
   `*_nodes` (stmt/list), `*_return`, `*_value` (expr), `*_decl`, `*_call`. Pick a scheme — e.g.
   `*_method` → `FunctionDef`; `*_stmt`/`*_return` → statement(s); expression builders unsuffixed — so a
   name predicts the return type.

7. **Make `main()` consistent.** The scalar module's `__all__` is built via
   `parse_stmts('__all__ = ["Scalar"]')` while `generate_constants` node-builds its `__all__`. For a
   pure-node generator, node-build the scalar one too (or use `parse_stmts` for both — pick one).

### Bigger / optional (architecture)

8. **Split the node-builder DSL into its own module** (e.g. `tools/astbuild.py`). The ~200 lines of
   `nm`/`dot`/`call`/`cast`/`fn`/`cls`/`ann_assign`/… are entirely **domain-agnostic** (they know
   nothing about geometric algebra). Separating them would shrink `gen_specialized.py` to the GA-specific
   logic, make the DSL reusable + independently testable, and sharpen the "generic AST building" vs "GA
   codegen" boundary. Cost: a second file (and `gen_specialized.py` imports from it). This is the change
   that most improves *architecture* rather than just ordering.

### Explicitly NOT changing

- The value-policy split (`summed_value`/`result_value`/`unary_value`) — it faithfully mirrors three
  different cast/term-order policies from the original; merging would lose fidelity (and break
  byte-identity).
- `expr_to_ast` + `SymbolToAttr` — clean as is.
- The `TypeSpec`/`resolve` registry — solid domain logic, untouched by the rewrite.

## Recommendation / suggested order

Do **1–4** first (move `generate_scalar`, reorder into sections, extract the shared method-builders,
name the return idioms) — that is where the structural confusion lives, it's low-risk, and it makes the
two big generators much clearer. Fold in **5–7** (docstring consolidation, naming, `main` consistency)
along the way. Then **8** (split out the DSL) if the cleaner architecture is wanted.

## Plan (once approved)

- [ ] #5/#6/#7 polish first (cheap, sets naming/sections), or interleave with the reorder.
- [ ] #1 + #2: move `generate_scalar`; reorder file into the target sections (pure code movement —
      output unchanged). Re-run `make check-generated` + suite.
- [ ] #3: extract `class_header`/`is_close_method`/`iter_method`/`grades_method` (+ `return_construct`
      from #4); rewrite `generate_class` and `generate_graded_type` to use them. Re-run gates.
- [ ] #8 (optional): move the DSL to `tools/astbuild.py`, import it. Re-run gates; update CLAUDE.md
      "Code generation" if it should mention the split.
- [ ] Final: `make check-generated` (determinism), full `pytest -q` (161), `ruff`/`ty` clean. Confirm
      no dead helpers remain.

## Notes / cross-refs

- Cross-ref `tasks/codegen-via-python-ast.md` (the A/B/C rewrite this builds on; C is the committed
  approach). Pending from that task: update CLAUDE.md's "Code generation" section to describe the `ast`
  approach (could be done as part of #8 or separately).
- Output-byte-identity is the safety net: any reorder/extraction that changes a generated file is a bug,
  caught by `make check-generated` + the suite.
