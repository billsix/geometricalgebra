# Use `from __future__ import annotations` to drop forward-ref quotes

**Created:** 2026-06-05 · **Completed:** 2026-06-06

Split out of `tasks/archive/2026/06/05/use-match-and-modern-python.md` (item G), because PEP 563
changes annotation semantics module-wide. The trigger: `project`/`reject`/`reflect` had
`"AbstractMultiVector" | Sequence["AbstractMultiVector"]`, a string forward reference `|`'d with a
real type, which `ty` flagged once `requires-python = ">=3.13"` was declared. That instance had been
fixed with a fully quoted union; the `__future__` import removes the need for forward-reference
quotes altogether. The benefit is readability and uniformity, with no behavior change intended.

## What changed

- **`base.py`:** `from __future__ import annotations` added, and the quotes dropped on every
  annotation-position `"AbstractMultiVector"` (parameters, returns, the three `… | Sequence[…]`
  unions). Runtime type arguments (`typing.cast`, `isinstance`, `match … case T():` patterns) were
  left as live classes.
- **The module-level alias `MultiVectorFn = Callable[["AbstractMultiVector"],
  "AbstractMultiVector"]` kept its quotes:** it is a runtime assignment evaluated before the class
  exists, which PEP 563 does not affect (a PEP 695 `type` statement could drop them; out of scope).
- **`gn.py` and the generated `g*.py` were deferred** to
  `tasks/archive/2026/06/06/add-python-types.md` (#1), which already touched `gn.py` and
  `tools/gen_specialized.py`. `Gn` is a `@dataclass(slots=True)`; string field annotations are fine
  for dataclasses, but the generator had to emit the import into every `g*.py` for consistency, and
  that regen belonged with the #1 generator pass rather than a standalone churn. (It was done there.)

## Verification

`ty check src`/`tests` clean, `ruff` clean, 141 tests pass.
