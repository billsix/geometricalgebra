# Write every basis vector bold with an arrow (`\vec{\mathbf{e}}_1`) wherever a reader sees math

**Status:** open — ready to implement
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/fill-placeholder-book-notebooks.md` (rewrites `defining-g2.rst`, which holds one
of the sites below)

## BLUF

The book writes general vectors bold with an arrow (`\vec{\mathbf{a}}`). The maintainer asked
(William Emerison Six <billsix@gmail.com>, 2026-11-19) for the basis vectors e₁, e₂, e₃, … to get the
same treatment everywhere a reader sees math: `\vec{\mathbf{e}}_1`. Higher blades stay one bold
`\mathbf{e}_{12}` with no arrow. The task is done when the discovery commands below find nothing
outside the exempt places, and `make docs` and `make format` pass.

## Context

- The rule is already written down in `CLAUDE.md` ("Math notation for readers", the "Typeset LaTeX
  writes vectors the way gacalc's output does" bullet). `blade_latex` in `src/gacalc/base.py`
  implements it for computed output, so every notebook *output* is already right. This task fixes
  only hand-written text.
- Where the rule applies: book pages (`book/docs/*.rst`), the Markdown cells of every notebook (both
  `book/docs/notebooks/*.py` and `notebooks/*.py`), and ePiX figure labels (`book/figures/epix/*.py`).
- Exempt: Python docstrings and comments, Lean doc comments, and code. These are plain text and keep
  `e_1` / `e₁`, for example `src/gacalc/nbplotutils.py`'s docstrings.
- Put the accent outside the bold: `\vec{\mathbf{e}}_1`. Written as `\mathbf{\vec{e}}`, lualatex draws
  the arrow as a garbled glyph.

## Current state (a discovery pass, 2026-11-19)

Most of the book already follows the rule. The pass found these remaining sites:

- `book/docs/proof-rotate-from-a-to-b.rst`, the `R_{\vec{a}}^{e_1}` / `R_{e_1}^{\vec{b}'}` paragraph
  (section "…the outer rotation and the inner rotation"): `e_1` → `\vec{\mathbf{e}}_1`. The `\vec{a}`
  and `\vec{b}'` on the same lines are not bold; fix them too (see the next bullet).
- Non-bold general vectors `\vec{a}` in `book/docs/*.rst`, 6 lines: `proof-reciprocal-frame.rst`
  (the reciprocal-frame introduction), `proof-rotate-from-a-to-b.rst` (above), and
  `rotation-from-vectors.rst` (the angle-bisector sentence). Change each to `\vec{\mathbf{a}}`. This
  is the same rule, so it is in scope.
- `book/docs/rotation-from-vectors.rst`, the "but we did not have to know θ" sentence: the bivector
  `e_{12}` → `\mathbf{e}_{12}`.
- `book/docs/defining-g2.rst`'s placeholder sentence uses Unicode `e₁ * e₂` in prose. The fill task
  rewrites that page, so fix it there, or here if this task runs first.
- Unicode `e₁`/`e₂`/`e₃` in notebook Markdown: `notebooks/displaygraded.py` (`I = e₁ * e₂ * e₃`, in
  the lazy-`g3.Bivector` cell) and `notebooks/displayvectorcalc.py` (the "vectors e₁/e₂/e₃ as
  **i**/**j**/**k**" line). Make each LaTeX (`$\vec{\mathbf{e}}_1$`). In the `I = …` case use
  `\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2 * \vec{\mathbf{e}}_3`.
- ePiX labels: none found. The labels already use `\vec{\mathbf{e}}_1` and `\mathbf{e}_{12}`.

## Discovery commands (re-run them; the list above is a snapshot)

Run these from the repo root inside `bash -c '…'`, because zsh mangles the patterns. They return
matches only.

    # plain e_1 / e_{1} in book math, outside ``code``
    grep -nP '(?<!mathbf\{)\be_\{?[1-9]\}?' book/docs/*.rst | grep -v '``'
    # \mathbf{e}_N with no \vec (a vector drawn without its arrow)
    grep -rnP '(?<!\\vec\{)\\mathbf\{e\}_\{?[1-9]\}?(?![0-9])' book/docs book/figures notebooks
    # \vec{x} with no bold
    grep -rnP '\\vec\{[a-z]\}|\\vec\{e\}' book/docs book/figures notebooks
    # Unicode subscripts in notebook Markdown and book prose
    grep -n '^#.*e[₁₂₃]' book/docs/notebooks/*.py notebooks/*.py
    grep -n 'e[₁₂₃]' book/docs/*.rst

These greps are a lead, not a proof. A basis vector in a figure label can also be assembled in an
f-string, so skim the label-building helpers in `book/figures/epix/_scene*.py` once.

## Plan

1. Re-run the discovery commands. Fix each site by hand; there are fewer than 15, so no codemod and no
   `tasks/adhoc/` script.
2. Check that a typo has not split a `\vec{\mathbf{…}}` brace: `make docs`, which builds HTML and the
   lualatex PDF and executes the notebooks. Then `make format`, which runs the prose-width check.
3. Re-run discovery: zero matches outside the exempt places.
4. Rewrite this doc as a done-record and stage it; the archive comes after the work commit.

## Open questions

None.
