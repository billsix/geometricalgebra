# Make the `f(x) = m·x + b` connection explicit at call sites

**Created:** 2026-07-18 · **Completed:** 2026-07-18
**Requested by:** the maintainer, 2026-07-18: "I want to make a connection to `f(x) = m*x + b`,
and for the callers of translate and uniform scale to call them using the named
parameter, i.e. `translate(b=e_1 + 3*e_2)`"

## Outcome

The teaching-facing conversion was done. The docstrings of `translate`/`uniform_scale` state the
`f(x) = m*x + b` link; call sites were converted in gacalc `notebooks/` (19) and in mvp's
(github.com/billsix/modelviewprojection) `demos`/`notebooksrc`/`assignments` (139), plus 8 inline
`book/docs/*.rst` examples. Library internals were deliberately left positional, per the
maintainer's scope call. The `m`/`b` exception was recorded in both repos' `CLAUDE.md` so a
later naming pass does not "fix" it to `offset`/`factor`.

## The pedagogical point

Every student arrives knowing the equation of a line, `f(x) = m·x + b`: `m` scales, `b` shifts.
The library's two most basic transforms are exactly those two halves, so naming them `m` and `b`,
*and using those names at the call site*, turns an unfamiliar API into something already
understood.

## Not an API change

`src/gacalc/transforms.py` already had `translate(b: V)` and `uniform_scale(m: float)`. The work
was two smaller things:

1. **The docstrings were made explicit**: they had said "Translate by ``b``" / "Scale uniformly
   by ``m``" without the reason; they now say `b` is the intercept and `m` the slope of
   `f(x) = m·x + b`.
2. **Call sites were converted to keyword form**: `translate(b=e_1 + 3 * e_2)` rather than
   `translate(e_1 + 3 * e_2)`.

## Scope

Measured 2026-07-18, none of ~300 call sites used keywords: gacalc `src`/`tests`/`notebooks` 62
(23 in `notebooks/`); mvp `src`/`tests` 214 (25 in `notebooksrc/`), `assignments/` 26, and 6
inline `book/docs/*.rst` examples. Each repo's conversion went in its own commit, separate from
any behavioural change.

Decisions (the maintainer, 2026-07-18):

- **Teaching-facing only.** Demos, notebooks, assignments, docstrings and the `.rst` inline
  examples were converted; library internals (the Cayley-graph engine, `_pipeline`,
  `transforms.py`'s own plumbing) stayed positional, since `translate(b=...)` inside the engine
  adds noise without teaching anyone. This roughly halved the diff.
- **Notebooks and assignments were explicitly in scope** ("make it also look through the
  notebooks and the assignments, and make sure that the keyword arguments are used in the
  callers") as the highest-value sites: a student meets the API there first. The `.rst` inline
  examples are not caught by editing Python files, so they were grepped separately.

Two related points raised during the work:

- `scale_non_uniform(*factors)` is variadic, so there is no single `m` and `*args` cannot be
  passed by keyword; its docstring already wrote `scale_non_uniform(m_x, m_y)`. The
  recommendation was to leave it positional.
- `rotate` has no `m`/`b` analogue: rotation is not part of `f(x) = m·x + b`, which is why the
  book introduces it separately.

## Interaction with the coding standard

Both repos' standards say "descriptive over terse" and warn off single-letter names. `m` and `b`
are a deliberate, documented exception justified by the `f(x) = m·x + b` link, in the same
category as gacalc's `n` for dimension; hence the `CLAUDE.md` entries. ruff does not complain:
`N803` only requires lowercase.

## Verification

Both repos: `make format` clean and the full test suite green. Notebooks and assignments are
scripts, not imported modules, so a passing suite proves nothing about them; each was executed
after converting (mvp's notebooks headless with `MPLBACKEND=Agg`, the GL assignments and demos
under Xvfb, per the nested-container recipe in github.com/billsix/runClaudeInContainer
`entrypoint/dotfiles/.claude/CLAUDE.md`).
