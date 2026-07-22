# Add missing docstrings to base/gn, and ensure the generator copies all of them

**Status:** proposed — needs go-ahead. Created 2026-07-21. (Bill's batch item 11-second.)

## Goal

Generated methods are supposed to carry the same Hestenes-notation docstrings as their
`MultiVectorBase` counterparts — the generator copies them via `inspect.getdoc` so the
specialized classes never drift from the base. Bill's observation: **some are present, some are
missing.** Two coupled pieces of work, with the first as the primary:

1. **Author the missing docstrings on `base.py` (and `gn.py`) methods** — the source of truth the
   generator copies from. Where a base/Gn method has no docstring, it can't be copied, so the
   generated method is undocumented.
2. **Ensure the generator actually copies every method's docstring** — audit which generated
   methods get a copied docstring vs none, and close any gaps in the copy mechanism (e.g. methods
   built outside the path that calls `method_doc_stmts`/`inspect.getdoc`).

Bill framed #2 as a **subtask of #1** ("perhaps this should be a subtask to generating more
docstrings in base and gn").

## What's there now (to verify during the task)

- The generator copies docstrings via `inspect.getdoc(MultiVectorBase.<method>)` (see the "Code
  generation" note in CLAUDE.md and `method_doc_stmts`/`docstring_for` in
  `tools/gen_specialized.py`). Methods built by a different path (e.g. some hand-constructed ones,
  or the `@overload` stubs, or `__mul__`/`__radd__` wrappers) may not go through it.
- First step of the task: **audit** — for each generated method, does it have a docstring? For
  each base/Gn method, does it have one to copy? Produce the gap list, then fill it.

## Plan (sketch)

1. Audit: enumerate generated methods with/without docstrings, and base/Gn methods with/without.
2. Author the missing base/Gn docstrings (Hestenes notation, page/eq citations where they apply).
3. Fix any generated methods that *should* copy but don't (route them through the doc-copy path,
   or give the overload stubs/wrappers a sensible generated one-liner where there's no base method
   to copy — e.g. the `@overload` stubs have no base counterpart).
4. Regenerate; doctests still pass (`--doctest-modules`); `check-regions`/gates green.

## Open questions

1. For generated methods with **no base counterpart to copy** (the `@overload` stubs, the
   scalar-aware `__mul__`/`__radd__` wrappers) — leave them docstring-less, or emit a generated
   one-liner? (My lean: leave the `@overload` stubs bare; give the real wrappers a one-liner if
   base has nothing.)

## Relationships

- Touches both `base.py`/`gn.py` (hand-written docstrings) and the generator's doc-copy path
  (`tools/gen_specialized.py`); see `tasks/reference/code-generator-architecture.md`.
- Related in spirit to `docstrings-for-sphinx.md` (existing open task) — check for overlap before
  starting.
