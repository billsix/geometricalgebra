# A `ty` gate for the generated modules

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §2.1, §8.1
**Decisions** (William Emerison Six <billsix@gmail.com>, 2026-11-08):

1. Add the gate and make it pass, rather than adopting a baseline or correcting the docs only.
2. Once the findings below showed the full fix was a redesign, take option (a2): keep the base's
   `-> Self`, suppress narrowly at each conflicting generated override, and add the gate. Park
   (a1), the redesign, as `tasks/typing-base-return-types-redesign.md`.

## What was wrong

Three docs called `make test-all-dims` "the full-dim + full-context ty gate", but it ran no `ty`:

- `CLAUDE.md` › "Dev workflow";
- `tasks/reference/design-decisions.md`;
- `tasks/reference/generated-product-typing.md`.

`entrypoint/format.sh`'s `ty check src` respected `.gitignore`, so it skipped the generated
`g*.py`. Nothing type-checked them. The target also lacked the `: image` prerequisite.

On 2026-11-08 (ty 0.0.91), the generated g1–g3 had **121 `invalid-method-override` errors**. g1–g3
had been recorded clean on 2026-08-22, so this check is newer in `ty`.

## Findings

**The cause.**

- `MultiVectorBase` declares 15 methods `-> typing.Self`: `_geometric_product`, `__mul__`,
  `__add__`, `__radd__`, `wedge`/`outer_product`/`__xor__`, `dot`/`inner_product`, the contractions,
  `__lt__`/`__gt__`, `r_vector_part`, `plane_of_rotation`.
- The graded types return the resolved product type instead (`Vector * Vector` is a `Versor`).

**Widening the 15 base returns to `MultiVectorBase`** (tried, then reverted) cleared the generated
modules but surfaced about 120 errors elsewhere:

- `base.py` compositions;
- `transforms.py`'s `V → V` generics;
- `Gn`-typed tests.

That is a typing redesign, about D8. Hence decision 2.

**How ty matches the base signature:**

- for a base method taking `rhs: Self`, the override conflicts only when its own-type `@overload`
  returns another type (`Vector.wedge(Vector) -> Bivector`);
- for an any-operand method, the override conflicts when the implementation returns another type.

A first rule that marked every non-own-type return gave 162 comments, 41 of which ty reported as
unused. The refined rule gives exactly 121, with none unused.

## What changed

- **`tools/astbuild.py`:** `header_comment(text)`, a sentinel decorator that `module_source` rewrites
  into a trailing `# <text>` on the `def` line. It works like `marker`, because comments can't live
  in an AST, and ty accepts the comment at the end of a ruff-wrapped header.
- **`tools/gen_specialized.py`:**
  - `SELF_OPERAND_RETURN_OVERRIDES` / `ANY_OPERAND_RETURN_OVERRIDES`, which hold the reason;
  - `mark_graded_return_overrides`, run after the docstring pass. It gives each conflicting graded
    implementation `# ty: ignore[invalid-method-override]`: 17 in g1, 38 in g2, 66 in g3.
- **`entrypoint/format.sh`** runs `ty check --no-respect-ignore-files src`, so `make format` (which
  regenerates g1–g3 first) and CI's `check-format` type-check the generated modules in full context.
- **`Makefile` `test-all-dims`:** `: image`, plus the same `ty` step after generating g1–g5. Its help
  text says so.
- **Tests (`tests/test_generator.py`):**
  - `test_header_comment_renders_at_the_end_of_the_def_line`;
  - `test_mark_graded_return_overrides_marks_only_conflicting_overrides`, which checks the own-type
    overload rule, the any-operand rule, and the full class being skipped.
- **Docs:**
  - `CLAUDE.md` (the `format.sh` and `test-all-dims` bullets);
  - `tasks/reference/design-decisions.md`: the generated-module bullet now says ruff skips them and
    ty checks them;
  - `tasks/reference/generated-product-typing.md`: "Verification method", and a new section, "Graded
    overrides of the base's `-> Self`".
- **The parked redesign, `tasks/typing-base-return-types-redesign.md`.** It records the
  maintainer's question, "a Protocol, or `typing.overload`?", investigated with a toy model in
  `tasks/adhoc/typing-base-return-types-redesign/`:
  - honest overloads in the base fix the contract;
  - a `LinearSpace` Protocol makes the transforms' `V → V` true;
  - a Protocol alone can't type the products.

## Verification

- `ty check --no-respect-ignore-files src`, `tests`, `tools`, `book/docs/notebooks`: all clean, with
  no unused-suppression warnings.
- Determinism (regenerated twice, `cmp`) and `tools/check_doc_regions.py`: OK.
- `ruff check .` and `ruff format --check .`: clean.
- `pytest -m "not slow"`: 813 passed, 2 skipped.
- `make help` shows the new `test-all-dims` text. The full `make test-all-dims` (about 1.5 h,
  generating g5) was not run in this session.
