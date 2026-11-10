# Investigate the type errors Emacs (pyright) reports for reals and sympy times multivectors

**Status:** proposed — investigation first, fix after
**Priority:** 4
**Difficulty:** 5
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

In Emacs (lsp-pyright), the maintainer sees type errors around (a) real numbers combined with
multivectors in the geometric product and (b) sympy expressions combined with multivectors. Find
what pyright actually reports and why, then fix it in the code rather than by suppressing. One idea
from the maintainer: a **scalar constructor that takes a `Real`** (e.g. `Scalar.from_real(x)`, or a
`Scalar(x)` positional form) so `Scalar(x) * v` type-checks where `x * v` does not. Other options:
better `__rmul__`/`__mul__` overloads, sympy's own `__mul__` returning `Expr` (sympy wins the
dispatch before our `__rmul__` gets a say — the likely root cause of (b)), or casts at the call site.
Done means: the reproduction list (file, line, pyright message) is written here, each class of error
has a decided fix, the fixes are applied, and `pyright` over `src/` + `notebooks/` is clean or each
residue is explained.

## Context (read first)

- Emacs uses npm pyright (`tasks/reference/emacs-lsp-setup.md`); the CI type gate is `ty`
  (`make type-check`). The two disagree in places; this task is about what pyright shows.
- `make check-notebooks` already runs `pyright notebooks/` — start from its output.
- Related, parked: `tasks/typing-base-return-types-redesign.md` (base `Self` returns are false for
  graded types; 121 `ty: ignore` suppressions). A fix here must not conflict with it; if the right fix
  is that redesign, say so and stop.
- `Real = int | float | sympy.Expr` (`src/gacalc/base.py`); `from_real` already exists on the base.

## Plan

1. Run pyright (same version and config Emacs uses) over `src/`, `notebooks/`, `tests/`; bucket the
   errors by cause.
2. For each bucket, try the candidate fixes in a scratch file and record what pyright and ty say.
3. Recommend + apply; record rejected options with the reason.
