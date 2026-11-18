# Research: thread "float vs symbolic" through calls, or configure it some other way?

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)

## Outcome

The maintainer asked whether threading `float_close_to_zero` and `MatrixBackend` through the calls
was right, or whether a global setting or a Lisp-style dynamically scoped variable would be better.
The answer is `tasks/reference/numeric-symbolic-mode.md`. It contains:
- the three current mechanisms, counted: value-type dispatch; the threaded flag, 62 sites; the
  matrix backend, 32 uses;
- four options with sources (PEP 567 / `decimal`, NumPy 2.0's context-variable `errstate`, SymPy's
  `global_parameters` and its maintainer's advice, galgebra's `Ga.dual_mode`), with the same call
  written each way;
- the closure trap: a setting read when a returned `InvertibleFunction` is called, not when it is
  built.

**Recommendation:**
- decide float tolerance from the coefficients, keeping the keyword as an override (`bool | None =
  None`);
- keep `MatrixBackend` explicit;
- no global and no `ContextVar` for either.

The implementation is scaffolded as `tasks/tolerance-from-coefficient-type.md` (proposed).

## How

The inventory came from `tasks/adhoc/research-numeric-symbolic-mode-threading/discover.sh` and its
snapshot in `data/`, both deleted at archive as one-shot. The sources were checked with three web
searches on 2026-11-18 and galgebra's local checkout.
