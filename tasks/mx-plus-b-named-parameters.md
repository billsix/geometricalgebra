# Make the `f(x) = m·x + b` connection explicit at call sites

**Status:** proposed — needs go-ahead
**Created:** 2026-07-18
**Requested by:** Bill, 2026-07-18 — "I want to make a connection to `f(x) = m*x + b`,
and for the callers of translate and uniform scale to call them using the named
parameter, i.e. `translate(b=e_1 + 3*e_2)`"

## The pedagogical point

Every student arrives already knowing the equation of a line, `f(x) = m·x + b`: `m`
scales, `b` shifts. This library's two most basic transforms are exactly those two
halves — so naming them `m` and `b`, *and using those names at the call site*, turns an
unfamiliar API into something already understood.

## Good news: the parameters are already named that way

`src/gacalc/transforms.py` already reads:

```python
def translate(b: V) -> InvertibleFunction[V]: ...
def uniform_scale(m: float) -> InvertibleFunction: ...
```

So this task is **not** an API change. It is two smaller things:

1. **Make the connection explicit in the docstrings.** Right now they say "Translate by
   ``b``" and "Scale uniformly by ``m``" — the names are there but the *reason* is not.
   Say outright that `b` is the intercept and `m` the slope of `f(x) = m·x + b`, so a
   reader meeting `b` knows why it is called that and doesn't "improve" it to `offset`.
2. **Convert call sites to keyword form**, so the teaching lands where the code is read:
   `translate(b=e_1 + 3 * e_2)` rather than `translate(e_1 + 3 * e_2)`.

## Scope (measured 2026-07-18)

| repo / area | call sites | already keyword |
|---|---|---|
| geometricalgebra — `src`, `tests`, `notebooks` | 62 | 0 |
| ...of which **`notebooks/`** | **23** | 0 |
| modelviewprojection — `src`, `tests` | 214 | 0 |
| ...of which **`notebooksrc/`** | **25** | 0 |
| modelviewprojection — **`assignments/`** | **26** | 0 |
| modelviewprojection — `book/docs/*.rst` inline examples | 6 | 0 |

**~300 call sites**, none currently keyword. Purely mechanical, easy to land and noisy to
review, so: its own commit per repo, separate from any behavioural change.

### Notebooks and assignments are explicitly in scope (Bill, 2026-07-18)

"make it also look through the notebooks and the assignments, and make sure that the
keyword arguments are used in the callers." These are the **highest-value** sites, not an
afterthought — a notebook or an assignment is read by a student who is meeting the API
for the first time, which is exactly the moment the `m`/`b` link should land. Do not skip
them because they are not `src/`:

- gacalc `notebooks/` — 23 sites (jupytext percent-format `.py` files).
- mvp `src/modelviewprojection/notebooksrc/` — 25 sites.
- mvp `assignments/` — 26 sites, student-facing exercises.
- mvp `book/docs/*.rst` — 6 sites written inline in prose rather than excerpted from
  source; these are **not** caught by editing Python files, so grep the `.rst` too.

**Verification for these areas is different from `src/`:** notebooks and assignments are
scripts, not imported modules, so a passing test suite proves nothing about them. Execute
each notebook and assignment after converting (mvp's notebooks run headless with
`MPLBACKEND=Agg`; the GL assignments need Xvfb — see the recipe in
`~/.claude/CLAUDE.md` › nested containers).

## Open questions to settle before starting

- ~~Does this apply to every call site, or only teaching-facing ones?~~ **SETTLED
  (Bill, 2026-07-18): teaching-facing only.** Convert the places a student reads —
  **demos, notebooks, assignments, docstrings, and the `.rst` inline examples** — and
  leave library internals positional (the Cayley-graph engine, `_pipeline`,
  `transforms.py`'s own plumbing). `translate(b=...)` inside the engine adds noise
  without teaching anyone. This roughly halves the diff and puts all of it where it
  earns something.
- **What about `scale_non_uniform(*factors)`?** It is variadic, so there is no single `m`
  to name; its docstring already writes `scale_non_uniform(m_x, m_y)`. Either leave it
  positional (recommended — you cannot pass `*args` by keyword) or document the `m_x`,
  `m_y` naming as the per-axis slopes.
- **`rotate` has no `m`/`b` analogue.** Worth a sentence in the docs saying so, so the
  pattern is not over-generalized: rotation is not part of `f(x) = m·x + b`, which is
  precisely why the book introduces it separately.

## Interaction with the coding standard

Both repos' standards say "descriptive over terse" and warn off single-letter names.
`m` and `b` are a **deliberate, documented exception** justified by the `f(x) = m·x + b`
link — the same category as gacalc's `n` for dimension. **Record the exception in both
`CLAUDE.md`s** when this lands, or a future naming pass will "fix" it back to
`offset`/`factor`. (Note ruff will not complain: `N803` only requires lowercase, which
`m` and `b` already are.)

## Gates

Both repos: `make format` clean, full test suite green. In mvp additionally run the demos
under Xvfb — the call-site conversion touches demo code that only a real run exercises.
