# Use `from __future__ import annotations` to drop forward-ref quotes

**Status:** complete (base.py) · 2026-06-06 · gn.py + generator deferred to #1
**Completed:** 2026-06-06

> **Completion note (2026-06-06):** applied to `base.py` only. Added `from __future__ import
> annotations` and dropped the forward-ref quotes on all annotation-position `"AbstractMultiVector"`
> (params, returns, the three `… | Sequence[…]` unions). The module-level alias
> `MultiVectorFn = Callable[["AbstractMultiVector"], "AbstractMultiVector"]` **keeps its quotes** —
> it's a runtime assignment evaluated before the class is defined, which PEP 563 doesn't affect
> (a PEP 695 `type` statement could drop those too, but that's out of scope). `ty check src`/`tests`
> clean, `ruff` clean, 141 tests pass.
>
> **`gn.py` + generated `g*.py` deferred** to `tasks/add-python-types.md` (#1): it already touches
> `gn.py` and `tools/gen_specialized.py`, and `Gn` is a `@dataclass(slots=True)` (string field
> annotations are fine for dataclasses, but the generator must emit the `__future__` import into every
> `g*.py` for consistency, and that regen belongs with the #1 generator pass — not a standalone churn).

## Goal

Add `from __future__ import annotations` to `base.py` (and evaluate `gn.py`) so that all annotations
become lazily-evaluated strings (PEP 563). That lets the many `"AbstractMultiVector"` / forward-ref
string annotations drop their quotes and read as plain types (`AbstractMultiVector`,
`AbstractMultiVector | Sequence[AbstractMultiVector]`), improving legibility. Split out of
`tasks/use-match-and-modern-python.md` (item G) because it changes annotation semantics module-wide
and deserves its own review.

## Background

- Surfaced while doing the match/modern-python pass: `project`/`reject`/`reflect` had
  `"AbstractMultiVector" | Sequence["AbstractMultiVector"]` (a string forward-ref `|`'d with a real
  type), which `ty` flagged once `requires-python = ">=3.13"` was declared. That instance was fixed
  with a fully-quoted union; `from __future__ import annotations` would make the whole class of
  forward-ref quoting unnecessary.
- Python floor is 3.13 (see `requires-python`), so PEP 563 is fully available.

## Plan

- [ ] Add `from __future__ import annotations` at the top of `base.py`.
- [ ] Remove now-unneeded quotes from forward-ref annotations (`"AbstractMultiVector"` →
      `AbstractMultiVector`, the quoted unions, etc.). **Annotations only** — leave runtime type
      args alone (e.g. `typing.cast(typing.Self, ...)`, `isinstance(...)`, `match ... case T():`
      patterns must stay real runtime values, NOT strings).
- [ ] Decide whether to also apply it to `gn.py`. **Caution:** `Gn` is a `@dataclass(slots=True)`.
      `from __future__ import annotations` makes field annotations strings; `dataclasses` handles
      string annotations fine for field detection, but double-check nothing introspects
      `__annotations__` expecting real types. The generated `g*.py` would need the import emitted by
      the generator if we want consistency there too.
- [ ] `ruff check`, `ty check src` + `tests`, full suite (124) green. Regenerate if the generator
      changes; notebooks still run headless.

## Notes / decisions

- Benefit is readability + uniformity (no mixed quoted/unquoted forward refs); no behavior change
  intended.
- Risk centers on anything that reads annotations at runtime (dataclasses, any reflection). `base.py`
  itself has no such reflection; `gn.py`'s dataclass is the one to vet.
- Keep the change annotation-only; do not convert `match`/`case` class patterns or `cast`/`isinstance`
  targets (those need live classes, not strings).

## Open questions

- Scope: `base.py` only, or also `gn.py` + the generated classes (via the generator)?
- Worth doing at all given the forward-ref quotes are already few and the one real bug is fixed?
