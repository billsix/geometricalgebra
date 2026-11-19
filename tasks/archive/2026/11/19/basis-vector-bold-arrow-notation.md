# Write every basis vector bold with an arrow (`\vec{\mathbf{e}}_1`) wherever a reader sees math

**Status:** done (2026-11-19)
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/archive/2026/11/19/fill-placeholder-book-notebooks.md` (ran in the same batch;
its rewrite of `defining-g2.rst` removed one site listed here)

## What this did

The maintainer asked (William Emerison Six <billsix@gmail.com>, 2026-11-19) that the basis vectors
e₁, e₂, e₃ be written bold with an arrow, `\vec{\mathbf{e}}_1`, wherever a reader sees math, the way
the book already wrote general vectors. The rule was already in `CLAUDE.md` ("Math notation for
readers"), and `blade_latex` (`src/gacalc/base.py`) already rendered computed output that way. A
discovery pass found the book almost entirely converted, so the task fixed the hand-written
leftovers:

- `book/docs/proof-rotate-from-a-to-b.rst`: the rotation names
  `R_{\vec{a}}^{e_1}` / `R_{e_1}^{\vec{b}'}` became `\vec{\mathbf{a}}`, `\vec{\mathbf{e}}_1`,
  `\vec{\mathbf{b}}'`.
- `book/docs/rotation-from-vectors.rst`: the bivector `e_{12}` became `\mathbf{e}_{12}`. Higher blades
  stay bold without an arrow. Also `\hat{a} \wedge \hat{b}` and the angle-bisector sentence's
  `\vec{h}`, `\vec{a}`, `\vec{b}` were bolded.
- `book/docs/proof-reciprocal-frame.rst`: `\vec{a}^1, …, \vec{a}^n` was bolded.
- `notebooks/displaygraded.py` and `notebooks/displayvectorcalc.py`: Unicode `e₁`/`e₂`/`e₃` in
  Markdown became LaTeX.
- `book/docs/defining-g2.rst`'s Unicode `e₁ * e₂` went away when the fill task rewrote that page.

Unbolded general vectors were in scope, because they fall under the same rule. ePiX labels already
used `\vec{\mathbf{e}}_1`. Docstrings, comments and code are exempt; they are plain text and keep
`e_1`.

## Discovery (re-runnable)

From the repo root, inside `bash -c '…'`. Use `git grep` rather than `grep -r`, which also matches
`book/docs/_build/` output and untracked `.ipynb_checkpoints/` copies.

    git grep -nP '(?<!mathbf\{)\be_\{?[1-9]+\}?' -- 'book/docs/*.rst' | grep -v '``'
    git grep -nP '\\vec\{[a-z]\}|\\hat\{[a-z]\}' -- 'book/docs/*.rst' 'book/docs/notebooks/*.py' 'notebooks/*.py'
    git grep -nP '(?<!\\vec\{)\\mathbf\{e\}_\{?[1-9]\}?(?![0-9])' -- book notebooks
    git grep -n 'e[₁₂₃]' -- 'book/docs/*.rst'
    git grep -n '^#.*e[₁₂₃]' -- 'book/docs/notebooks/*.py' 'notebooks/*.py'

## Verification

After the fixes, all five discovery commands returned nothing. `tools/check_notebook_prose_width.py`
and `ruff` were clean on the two notebooks. The book gate (`docs.sh`) and `make format` ran once at
the end of the batch, over both tasks' changes.
