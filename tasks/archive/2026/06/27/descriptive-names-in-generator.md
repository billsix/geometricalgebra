# More descriptive function/variable names in the code generator

**Status:** complete — Batches 1–3 applied & verified (2026-06-27); ready to archive
**Proposed:** 2026-06-27
**Completed:** 2026-06-27

## Done (2026-06-27)

Renamed in `tools/gen_specialized.py` only (output byte-identical to baseline throughout):
- **Batch 1 — nested locals:** `generate_scalar` `s`/`sr`/`mul`/`selfsc`/`numlike` →
  `scalar_const`/`scalar_const_coef`/`mul_expr`/`self_scalar_field`/`number_types`;
  `graded_specs` `by_grade(g)`/`bl` → `blades_of_grade(grade)`/`blades`;
  `generate_graded_type` `thunk` → `gn_unary`; `generic_docstring` `bl`/`g` → `blades`/`grade`.
- **Batch 2 — params/locals:** `product_result` `t1`/`t2`/`gn_op`/`a_syms`/`b_syms`/`rd`/`rspec` →
  `lhs_spec`/`rhs_spec`/`gn_product`/`lhs_symbols`/`rhs_symbols`/`result_coeffs`/`result_spec`;
  `unary_result` `t1`/`gn_fn`/`a_syms` → `operand_spec`/`gn_unary`/`operand_symbols`;
  `dispatch_method` `t1`/`t2` → `self_spec`/`rhs_spec`; `rspec`→`result_spec` everywhere;
  `name_`→`type_name` (is_close_method/result_stmts/scaled_stmt); `_match_class` `cls_node`→`class_expr`.
- **Batch 3 — module fns:** `_sub`/`_sup` → `_subscript`/`_superscript` (param `k`→`number`).
- **Off-limits (left unchanged, would alter emitted bytes):** cse temp names (`str(t)`), the `"a_"`/`"b_"`
  symbol prefixes, `field_name(...)` outputs, and the `_coerce(x, cls)` helper (it lives in a raw header
  string and is emitted verbatim).
- **Batch 4 (astbuild `cls(name_)` → `class_name`): skipped** per the default (left the DSL alone).
- Longer names pushed several lines over 88; fixed with `ruff format` (code lines) + manual f-string
  splits (4 docstring lines) — resulting strings unchanged.

**Verified:** generator runs; all four `scalar/g1/g2/g3.py` **byte-identical** to the pre-change
baseline; deterministic (regen twice); `ruff` + `ty check` clean on `tools/`; full suite **226 passed**.
Git shape: `tools/gen_specialized.py` only; nothing under `src/gacalc/`.

## (original plan below)

## Goal

Make the names in the code generator (`tools/gen_specialized.py`, and where relevant
`tools/astbuild.py`) more **descriptive and self-explanatory** — function names, parameters,
and local variables — so a newcomer can read the generator top-to-bottom without decoding terse
abbreviations. This is a pure **readability / naming** pass on the *generator source itself*; it
must **not** change a single byte of the generated output.

## Scope / what this is NOT

- This is **not** the builder-suffix *convention* pass — that was item #6 of
  `tasks/archive/2026/06/07/gen-specialized-structure-refactor.md` (done & committed): it settled
  `*_method` → `FunctionDef`, `*_stmt`/`*_stmts` → statement(s), `*_value` → expr, and renamed
  `dispatch_nodes → dispatch_method`. Those suffix conventions stay; this task is about the
  **remaining terse / cryptic identifiers** the convention pass didn't touch (single-letter locals,
  abbreviations, opaque parameter names).
- It does **not** touch the GA math, the `TypeSpec`/`resolve` registry logic, or the generated
  `scalar/g1/g2/g3.py` (those are gitignored build artifacts anyway). Output stays byte-identical.
- The short, *conventional* DSL primitive names in `astbuild.py` (`nm`/`dot`/`lit`/`call`/`cast`/
  `ret`/`fn`/`cls`/…) are an established mini-DSL — leave them as-is unless a specific one is
  genuinely confusing. The win here is in `gen_specialized.py`.

## Candidate names to improve (grounded in current source, 2026-06-27)

A non-exhaustive starter list found by reading `tools/gen_specialized.py`:

- **`generate_scalar` nested helpers** (lines ~832–838): `s(value)`, `sr(value)`, `mul(a, b)` —
  one-letter helper names for "wrap as Scalar" / "wrap as Scalar with Coef cast" / "scalar product
  expr". Rename to intent-revealing names (e.g. `scalar_const` / `scalar_const_coef` / `scalar_mul`).
- **`product_result` / `unary_result`** (~371, ~389): params `t1`, `t2`, `gn_op`, `gn_fn` — the two
  operand `TypeSpec`s and the `Gn` operation callable. `t1`/`t2` → `lhs_spec`/`rhs_spec` (or
  `self_spec`/`rhs_spec`); `gn_op`/`gn_fn` → `gn_product`/`gn_unary` (or `…_op`).
- **`_sub(k)` / `_sup(k)`** (~172, ~176): unicode sub/superscript helpers; `k` → `digit`/`n`.
- **`graded_specs.by_grade(g)`** (~336): `g` → `grade`.
- **`result_block_stmts(rspec, …)` / `unary_stmt(rspec, …)`** (~713, ~730) and similar: `rspec` →
  `result_spec`.
- **`is_close_method(name_, fields)`**, **`result_stmts(name_, pairs)`** (~620, ~674): the trailing-
  underscore `name_` (dodging the builtin) reads oddly; consider `class_name` / `type_name`.
- **`generate_graded_type.unary_body(thunk)`** (~1306): `thunk` → `make_value` / `value_builder` (a
  callable producing the result expr).
- **`_match_class(cls_node)`** (~738): `cls_node` → `class_pattern` (it builds the `match` class
  pattern).
- **`_coerce(x, cls)`** (~1614): `x` → the value being coerced (`value`).
- Sweep for any remaining single-letter / abbreviated locals (`g`, `k`, `x`, `s`, …) and opaque
  params while reading each function; rename only where a clearer name genuinely helps.

(Confirm each against the live source before renaming — line numbers drift.)

## Hard invariant

The generated modules must stay **byte-identical run-to-run and vs. the pre-change baseline**.
Renaming identifiers in the generator cannot change emitted code, but verify it:

- `make check-generated` (regenerate twice, assert byte-identical) stays green.
- Capture a baseline of `src/gacalc/{scalar,g1,g2,g3}.py` before starting (after a `make generate`),
  then `diff` against a post-rename regen — expect **zero** diff.
- Full suite green (`make test`, ~141/161 tests incl. doctests), `ruff` + `ty check` clean on
  `tools/` as well as `src`/`tests`.

## Plan (once approved)

- [ ] `make generate`; snapshot the four generated files as the byte-baseline.
- [ ] Rename in `tools/gen_specialized.py` (and `astbuild.py` only if a specific name is confusing),
      working in small batches; re-run after each batch.
- [ ] After each batch: regenerate, `diff` against baseline (must be empty), `make check-generated`,
      `ruff`/`ty`.
- [ ] Final: full `make test`; confirm no stale names remain and CLAUDE.md's generator references
      still read correctly (likely no doc change needed — names are internal to `tools/`).

## Notes / cross-refs

- Builds on / complements `tasks/archive/2026/06/07/gen-specialized-structure-refactor.md` (structure
  + the #6 suffix-convention pass) and `tasks/archive/2026/06/07/codegen-via-python-ast.md` (the
  AST-based generator this all sits on).
- Per CLAUDE.md "Code generation": never hand-edit the generated `g*.py`/`scalar.py`; all changes go
  through the generator, and a correct change here shows up as a `tools/` diff with **nothing** under
  `src/gacalc/`.
