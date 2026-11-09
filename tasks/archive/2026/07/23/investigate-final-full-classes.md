# Investigate making the full classes `G1`/`G2`/`G3` `@typing.final` and dropping `type(self)`

**Completed:** 2026-07-23

## Starting point

The graded types (`Vector2`/`Bivector2`/…/`ScalarN`) were `@typing.final`, so their generated
methods constructed the concrete class directly. The full classes `G1`/`G2`/`G3` had been left
subclassable as the "extension point", so their generated methods went through `type(self)`
(`construct_type_self` in `result_stmts` / `result_block_stmts` / `unary_stmt` for the `"full"`
kind), and `tests/test_subclass_preservation.py` asserted `G2` was NOT final. The question was
whether `G_n` could also be final. `MultiVectorBase`'s own `type(self).zero()`/`from_blade_dict()`
is a different thing (cross-*representation* dispatch over `Gn` + every specialized type, not
subclass preservation) and was out of scope.

## Finding: nothing subclasses `G_n`

The blocker was checked first. A repo-wide + mvp (github.com/billsix/modelviewprojection) search
found the only subclass anywhere was `class MyG2(G2)` in `tests/test_subclass_preservation.py`, the
test asserting subclassing was possible; mvp never references `G1/G2/G3` (it uses the graded types
directly). So `@typing.final` was safe, and the loss of the extension point cost nothing in use.

## What changed (generator-only, `tools/gen_specialized.py`)

- `@typing.final` added to the full-class decorator (`generate_class`).
- `result_stmts` (full-class-only; all callers are in `generate_class`) constructs the concrete
  class (`G2(...)`) instead of `type(self)(...)`. Result: **zero `type(self)` in the generated full
  class** (`grep -c` → 0). `-> Self` still holds (Self ≡ `G_n` for a final class).
- The now-dead `result_spec.kind != "full"` branches in `result_block_stmts` / `unary_stmt` (only
  reachable via `dispatch_method`, which the full class doesn't use) were collapsed.
- The unused `construct_type_self` import was dropped; it was kept as a general astbuild primitive
  (via `return_construct(..., final=False)`) in case a non-final generated type is ever added.
- **`base.py` and `Gn` (`gn.py`) were untouched.**

Test (`tests/test_subclass_preservation.py`): `test_full_classes_are_not_final` became
`test_all_generated_types_are_final` (now including `G1`/`G2`/`G3`); the `MyG2` subclass and its
preservation tests were replaced with `test_full_class_products_construct_concretely` (arithmetic
returns exactly `G2`); the module docstring was rewritten. `ty` rejects `class X(G2)` with
`error[subclass-of-final-class]`.

Rationale was harvested to `tasks/reference/design-decisions.md` ("Same-type generated ops" entry)
and `tasks/reference/code-generator-architecture.md` (construction helpers + finality note).

## Verification

ruff clean · ty src/tests/tools clean · full suite 299 pass · doc-regions clean · generation
deterministic. Runtime value-identical (no real code subclassed `G_n`, so `type(self)` always was
`G_n`). The regenerated `g*.py` are gitignored.

## Related

- Model: the graded-subtypes work (`tasks/archive/2026/06/06/graded-blade-subtypes.md`) and the
  "final → concrete class, no cast" pattern in `tasks/reference/generated-product-typing.md`.
