# Research: thread "float vs symbolic" through calls, or configure it some other way?

**Status:** proposed — needs go-ahead (research only; no code changes until the findings are reviewed)
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)

## BLUF

gacalc runs the same code on floats and on sympy expressions. Where the two need different
treatment, the choice is passed down explicitly: the `float_close_to_zero` flag is threaded through
`base.py`, `frame.py`, `transforms.py` and the generator (~60 uses), and a `backend: MatrixBackend`
parameter is threaded through `to_matrix`. The maintainer (2026-11-16) wants it studied whether
that threading is right, or whether something else is better:
- a global setting that configures the library;
- something like Common Lisp's dynamically scoped special variables (`(let ((*x* …)) …)`, visible
  to every call made inside the binding and restored on exit).

Done means a reference doc, `tasks/reference/numeric-symbolic-mode.md`, with:
- the current mechanisms, inventoried;
- the options, researched online with sources;
- a recommendation;
- a follow-on implementation task if the recommendation is to change anything, scaffolded as
  proposed.

## Context

### How float vs symbolic is chosen today (inventory 2026-11-16, to be completed)

Three different mechanisms:

1. **Dispatch on the value's type, no parameter.** The code looks at what it was given:
   - `MultiVectorBase.exp` (`src/gacalc/base.py`): `numeric = isinstance(θ, float)` picks
     `math.cos` or `sympy.cos`;
   - `magnitude` / `inverse` keep a float a float (`CLAUDE.md`, "`magnitude`/`inverse` preserve
     numeric input"; `tests/test_numeric_magnitude.py`);
   - `src/gacalc/frame.py` `_has_float(vectors)` decides whether a frame's checks need tolerance.

   Nothing is threaded, and mixed inputs follow whatever the code checks.
2. **An explicit flag threaded through the calls.** `float_close_to_zero: bool = False` on
   `is_orthogonal_to` / `is_parallel_to` (`base.py`), `are_linearly_independent` / `is_frame` /
   `require_frame` (`frame.py`), many factories in `transforms.py` (28 uses), and the generated
   classes (`tools/gen_specialized.py`, 7 uses). Every layer between the caller and the test has to
   accept and pass it on. `frame.py` sometimes derives it from the values (`_has_float`), which
   mixes mechanisms 1 and 2.
3. **An explicit choice of output representation.** `backend: MatrixBackend = MatrixBackend.NUMPY`
   (`src/gacalc/functions.py`, `transforms.to_matrix` / `ComposableFunction.to_matrix`; 18 call
   sites). This is a different kind of choice (what to build, not how to compare), but it is
   threaded the same way.

**A precedent for session-wide state:** `base.py` `set_blade_symbols` sets a module-level map
(`_blade_display_symbols`) once per kernel, because Jupyter calls `_repr_latex_()` with no
arguments. It covers display only.

### What to research (online, with sources cited in the reference doc)

- **Dynamic scoping in Python:**
  - `contextvars.ContextVar` (PEP 567) with a context manager that sets and resets a token. This is
    the closest analogue of a Lisp special variable that also works correctly with threads and
    asyncio.
  - Plain module globals: the `set_blade_symbols` style.
  - `threading.local`.
- **Precedents in the libraries gacalc already uses or resembles:**
  - `decimal.localcontext()` (the standard library's model of a dynamically scoped arithmetic
    context);
  - sympy's `evaluate(False)` context manager and its global parameters;
  - `numpy.errstate` / `np.printoptions`, and how numpy implements them (contextvars);
  - `mpmath.workdps`;
  - any GA library (clifford, galgebra, kingdon) that faces the numeric/symbolic split.
- **Trade-offs to weigh for gacalc specifically:**
  - explicitness and readability for students (the code is read as teaching material:
    `CLAUDE.md`, "Write the named geometric operation where the code means it");
  - type-checkability (`ty`, pyright);
  - testability and test isolation (pytest runs and `--doctest-modules`);
  - Jupyter usage (a setup cell vs per-call arguments);
  - the generated classes (`tools/gen_specialized.py` emits the flag today);
  - whether dispatching on the value's type (mechanism 1) could replace the flag entirely, with a
    context variable only as an override;
  - interaction with the `InvertibleFunction` / `ComposableFunction` closures, which capture
    arguments when built and run later. A dynamically scoped setting would be read at call time,
    not build time, and that difference must be shown with an example.
- **Python's own guidance:** what the language docs and PEPs say about context variables vs
  globals vs explicit parameters, and what well-regarded style guides say about hidden
  configuration.

## Plan

1. Complete the inventory with `git grep`: every `float_close_to_zero`, `MatrixBackend`, and
   `isinstance(…, float)` site, grouped by mechanism, with counts. Save the discovery command as
   `tasks/adhoc/research-numeric-symbolic-mode-threading/discover.sh`.
2. Research the options above online and record each with a source link and a short gacalc-shaped
   example: the same `is_parallel_to` call under (a) the threaded flag, (b) a module global, (c) a
   `ContextVar` with a context manager, (d) dispatch on the value's type alone.
3. Write `tasks/reference/numeric-symbolic-mode.md`: the inventory, the options with trade-offs, and
   a recommendation, possibly different for the tolerance flag and for the matrix backend.
4. If it recommends a change, scaffold the implementation task (`proposed — needs go-ahead`),
   cross-linked. Archive this task.

## Open questions

None yet. The research may raise some for the reference doc's recommendation.
