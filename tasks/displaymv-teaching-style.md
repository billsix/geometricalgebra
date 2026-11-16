# Bring `notebooks/displaymv.py` up to the teaching-style standard

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 6
**Difficulty:** 4
**Started:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)

## BLUF

The opening sections of `notebooks/displaymv.py` are the model in
`tasks/reference/book-notebook-teaching-style.md`, but the rest of the notebook is a scratchpad that
breaks that standard. Bring the whole notebook up to it. Done means: the notebook passes the
reference doc's checklist, `make check-notebooks` and `make format` pass, and the doc's "Known gaps
in the model" section no longer lists `displaymv.py`.

## Context

- **Read first:** `tasks/reference/book-notebook-teaching-style.md` ("The model", "What to avoid",
  the checklist). `notebooks/` notebooks are demos, not book pages, so the book's
  companion-notebook structure (`tasks/reference/book-outline.md`) does not apply; the teaching
  style does.
- **What is already right:** the sections from "How multiplication works in G_n" through "A longer
  example — and why grouping is about to matter". Keep their order and content; only the "What to
  avoid" items below touch them.
- **What breaks the standard (read 2026-11-16):**
  - After the associativity discussion, a long run of cells has no Markdown: `sym_vec2_*` dot and
    wedge, `MultiVector.i`, projections onto coordinate planes, `sym_vec3_*` products and the
    bivector inverse, basis-blade lists, grade parts, the `G2_1`/`G2_2`/`G2_3` associativity
    `show_mult` tables and difference, `a_1 * e_1 * e_2 * e_4`, the bivector `B` and its dual, the
    n=8 × n=9 `show_mult` table, two empty cells.
  - Off-subject material: `gram_fe_to_mol_fe` (a units conversion), the `T`/`S`/`R` transforms and
    `compose`/`inverse`, and four graph-paper plot sections, one heading used twice ("Draw relative
    graph paper").
  - Prose math is backticked code, not LaTeX.
  - 24 `# pyright: ignore[reportUnusedExpression]` trailers. `pyrightconfig.json` already sets
    `reportUnusedExpression` to `"warning"`, so check whether `make check-notebooks` still passes
    without them before deciding how to remove them.
  - Developer comments in the student's view: the `typing.cast` note on `dual()` and the six-line
    note on the type of `scale_non_uniform`.
  - `# -> 1`-style answers given before the cell runs.
  - `a_1 * e_1 * e_2 * e_4` writes a symbolic coefficient bare, against `CLAUDE.md`'s
    scalar-constructor rule (`Gn.from_real(a_1) * e_1`).
  - "see the associativity section / task" names nothing; the proof is
    `tasks/reference/geometric-product-associativity.md`.
- `make check-notebooks` runs pyright over `notebooks/`; `make format` runs ruff and ty.

## Plan

1. Decide the split (open question 1) and move the off-subject sections there.
2. Give every remaining code cell a Markdown lead-in, grouped into named sections (dot and wedge,
   projection onto coordinate planes, grade parts, associativity in 𝒢₂ as a proof, duals).
3. Rewrite the associativity tables' lead-in to say they compare the two groupings and that the zero
   difference, over general symbolic multivectors, proves associativity for all of 𝒢₂.
4. Convert prose math to `$…$` LaTeX per the `CLAUDE.md` notation rules; replace `# ->` answers
   with predict-then-run prompts; remove the developer comments and pyright trailers.
5. Shrink or explain the n=8 × n=9 table; delete the empty cells; fix the dangling pointer and the
   bare symbolic coefficient.
6. Run `make check-notebooks` and `make format`; open the notebook (`make notebooks-ipynb` or
   Jupyter) and read the rendered output once. Remove `displaymv.py` from the reference doc's
   "Known gaps in the model".

## Open questions

1. Where does the off-subject material go: a new `notebooks/displaytransforms.py` for the
   transforms and graph paper, with `gram_fe_to_mol_fe` deleted? Recommended: yes, and drop the
   units example unless you want it kept somewhere.
