# Investigate making the full classes `G1`/`G2`/`G3` `@typing.final` and dropping `type(self)`

**Status:** complete
**Completed:** 2026-07-23

## Done

**Blocker checked first (it was the whole question): nothing subclasses `G_n`.** A repo-wide + mvp
search found the *only* subclass anywhere was `class MyG2(G2)` inside
`tests/test_subclass_preservation.py` — the test asserting subclassing was *possible*; mvp never even
references `G1/G2/G3` (it uses the graded types directly). So `@typing.final` is safe.

Changes (generator-only, `tools/gen_specialized.py`):
- Added `@typing.final` to the full class decorator (`generate_class`).
- `result_stmts` (full-class-only — all callers are in `generate_class`) now constructs the concrete
  class (`G2(...)`) instead of `construct_type_self` (`type(self)(...)`). Result: **zero `type(self)`
  in the generated full class** (`grep -c` → 0). `-> Self` still holds (Self ≡ `G_n` for a final class).
- Collapsed the now-dead `result_spec.kind != "full"` branches in `result_block_stmts` / `unary_stmt`
  (only reachable via `dispatch_method`, which the full class doesn't use).
- Dropped the unused `construct_type_self` import; kept it as a general astbuild primitive (via
  `return_construct(..., final=False)`) in case a non-final generated type is ever added.
- **`base.py` untouched** — `MultiVectorBase`'s `type(self).zero()`/`from_blade_dict()` is
  cross-*representation* polymorphism (`Gn` + all specialized types), not subclass preservation; out of
  scope as the task noted. `Gn` (gn.py) also untouched.

Test (`tests/test_subclass_preservation.py`): flipped `test_full_classes_are_not_final` →
`test_all_generated_types_are_final` (now includes `G1`/`G2`/`G3`); replaced the `MyG2` subclass +
its preservation tests with `test_full_class_products_construct_concretely` (arithmetic returns exactly
`G2`); rewrote the module docstring. Confirmed `ty` rejects `class X(G2)` with
`error[subclass-of-final-class]`.

Rationale harvested to `tasks/reference/design-decisions.md` ("Same-type generated ops" entry) and
`tasks/reference/code-generator-architecture.md` (construction helpers + finality note).

**Gates:** ruff clean · ty src/tests/tools clean · full suite 299 pass · doc-regions clean ·
generation deterministic. Runtime value-identical (no real code subclassed `G_n`, so `type(self)`
always was `G_n`). Generator-only change; regenerated `g*.py` are gitignored.

## Original task


## Goal

The **graded** types (`Vector2`/`Bivector2`/…/`ScalarN`) are `@typing.final` (not subclassable), so
their generated methods construct the **concrete class directly** (no `type(self)` indirection). The
**full** classes `G1`/`G2`/`G3` are deliberately left **subclassable** (the "extension point"), so
their shared/generated methods go through `type(self)` / `type(self).zero()` /
`type(self).from_blade_dict(...)` to preserve a subclass's type. Determine whether `G_n` can *also* be
`@typing.final`, letting us delete that `type(self)` indirection in the full-class code.

## Current state (starting point)

- `tests/test_subclass_preservation.py` **asserts `G2` is NOT final** ("The full G_n classes remain
  subclassable (the extension point)") — this task would flip that assertion.
- The generator keeps `type(self)` specifically for the `"full"` kind: `result_stmts` /
  `result_block_stmts` / `unary_stmt` branch on `owner`/`kind` and use `construct_type_self` for the
  full class but `construct(<concrete>)` for the final graded types
  (`tools/gen_specialized.py:867,928,995`).
- `MultiVectorBase` (`base.py`) also uses `type(self).zero()`/`from_blade_dict` — **but that is
  different**: base is polymorphic across *every* representation (`Gn` + `G1/G2/G3` + all graded
  types), so its `type(self)` is doing cross-representation dispatch, **not** subclass-preservation.
  That likely must stay; scope this task to the *generated full-class* methods + whether `G_n` needs
  to stay subclassable.

## Investigate

1. **Is `G_n` subclassing actually used** anywhere — in-repo, in `tests/`, in `notebooks/`, or
   downstream (mvp)? If nothing subclasses `G1/G2/G3`, `@typing.final` is safe and the `type(self)`
   in the *generated full-class* methods can become the concrete class (`G2(...)` instead of
   `type(self)(...)`), simplifying + letting `ty` treat results as exactly `G_n`.
2. **`Gn` (the dimension-agnostic reference in `gn.py`) is separate** — it inherits `MultiVectorBase`
   directly and is the general representation; decide whether it's in scope (probably stays
   subclassable/uses base's polymorphic `type(self)`).
3. **What the generator change looks like:** collapse the `kind == "full"` special-cases so the full
   class emits like the graded ones (concrete construct, `@final` decorator). Confirm the
   sandwich/`_OperandT` and any `super()` calls still type.
4. **Weigh the loss:** `@final` removes the extension point. Confirm no downstream relies on
   subclassing `G_n` (mvp uses the graded types directly; check its ports/mathutils).

## Verify

Regenerate; `ty`/ruff/suite/regions/determinism green; flip `test_subclass_preservation` to assert
`G_n` **is** final; a `class X(G2): ...` is rejected by `ty`; runtime unchanged.

## Relationships

- Model: the archived graded-subtypes work that made the graded types `@typing.final`
  (`tasks/archive/2026/06/06/graded-blade-subtypes.md`) and the "final -> concrete class, no cast"
  pattern in `tasks/reference/generated-product-typing.md`.
- `tests/test_subclass_preservation.py` (the assertion that would flip).
