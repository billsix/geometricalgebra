# Investigate the type errors Emacs (pyright) reports for reals and sympy times multivectors

**Status:** blocked — investigation done; the fix waits on the maintainer's choice of spelling (Findings)
**Priority:** 4
**Difficulty:** 5
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** the maintainer choosing option 1–4 in `tasks/reference/pyright-sympy-coefficient-typing.md` (how symbolic coefficients are written in teaching code).
**Recheck:** the task's Decisions section names an option.
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

## Findings (2026-11-10)

Full write-up: `tasks/reference/pyright-sympy-coefficient-typing.md`. In short: 159 of the 195 pyright
errors outside the generated modules are one cause. sympy's `Expr.__mul__` accepts any right operand
and returns `Expr`, so pyright types `s_1 * e_1` (and a `Real`-typed coefficient times a vector) as
`Expr` and never consults gacalc's `__rmul__`; ty types it `Any` and stays silent. The maintainer's idea
works: `Scalar(s_1) * e_1` (or `Gn.from_real(a_1) * e_1`) types as `Vector` (`Gn`) under both checkers,
as does `e_1 * s_1`. No code was changed: the fix rewrites how ~160 symbolic lines in the book, tests
and `src/` read, which is a teaching-style decision. The generated modules' 215 pyright errors (mostly
`reportOverlappingOverload` on the product overloads) are a separate matter, close to
`tasks/typing-base-return-types-redesign.md`.
