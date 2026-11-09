# More descriptive function/variable names in the code generator

**Created:** 2026-06-27 · **Completed:** 2026-06-27

## What it was

A readability pass on the names in `tools/gen_specialized.py` — terse locals, abbreviations and opaque
parameters — so a newcomer can read the generator top to bottom. The hard invariant: not one byte of
generated output may change. It was not the builder-suffix convention pass (#6 of
`tasks/archive/2026/06/07/gen-specialized-structure-refactor.md`, whose `*_method` / `*_stmt(s)` /
`*_value` conventions stayed), and it did not touch the GA math, the `TypeSpec`/`resolve` registry, or
the conventional short DSL primitives in `tools/astbuild.py` (`nm`/`dot`/`lit`/`call`/`cast`/`fn`/`cls`).
It builds on `tasks/archive/2026/06/07/codegen-via-python-ast.md`.

## What was renamed (2026-06-27)

- **Batch 1 — nested locals:** `generate_scalar` `s`/`sr`/`mul`/`selfsc`/`numlike` →
  `scalar_const`/`scalar_const_coef`/`mul_expr`/`self_scalar_field`/`number_types`; `graded_specs`
  `by_grade(g)`/`bl` → `blades_of_grade(grade)`/`blades`; `generate_graded_type` `thunk` → `gn_unary`;
  `generic_docstring` `bl`/`g` → `blades`/`grade`.
- **Batch 2 — parameters and locals:** `product_result` `t1`/`t2`/`gn_op`/`a_syms`/`b_syms`/`rd`/`rspec`
  → `lhs_spec`/`rhs_spec`/`gn_product`/`lhs_symbols`/`rhs_symbols`/`result_coeffs`/`result_spec`;
  `unary_result` `t1`/`gn_fn`/`a_syms` → `operand_spec`/`gn_unary`/`operand_symbols`; `dispatch_method`
  `t1`/`t2` → `self_spec`/`rhs_spec`; `rspec` → `result_spec` everywhere; `name_` → `type_name`
  (`is_close_method`/`result_stmts`/`scaled_stmt`); `_match_class` `cls_node` → `class_expr`.
- **Batch 3 — module functions:** `_sub`/`_sup` → `_subscript`/`_superscript` (parameter `k` → `number`).
- **Left unchanged, because they would alter emitted bytes:** the cse temp names (`str(t)`), the
  `"a_"`/`"b_"` symbol prefixes, `field_name(...)` outputs, and the `_coerce(x, cls)` helper, which lives
  in a raw header string emitted verbatim.
- **Batch 4 (`astbuild` `cls(name_)` → `class_name`) was skipped**, by default leaving the DSL alone.

The longer names pushed several lines past 88 columns; `ruff format` fixed the code lines and four
docstring lines got manual f-string splits, leaving the strings unchanged.

## Verification

The generator ran; all four `scalar/g1/g2/g3.py` were byte-identical to the pre-change baseline and
deterministic (regenerated twice); `ruff` and `ty check` were clean on `tools/`; the full suite passed
(226). The diff touched `tools/gen_specialized.py` only, nothing under `src/gacalc/`.
