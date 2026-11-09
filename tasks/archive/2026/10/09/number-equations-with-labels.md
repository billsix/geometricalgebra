# Number the book's displayed equations, LaTeX-style, and reference them by number

**Created:** 2026-10-08 · **Completed:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

The maintainer wanted displayed equations numbered "like TeX" and citable by number. Done:
`book/docs/conf.py` now numbers every `.. math::` block (and notebook `$$ … $$`) in HTML and PDF,
the rotation formula of `proof-rotate.rst` carries a `:label:` and is cited with `:eq:` from the two
pages that point at it, and the convention is recorded in `tasks/reference/book-outline.md`. The
numbers ran straight through (`(3)`, `(4)`, …) until the companion
`tasks/archive/2026/10/09/pdf-section-and-page-numbers-for-print.md` added `:numbered:` to the
toctree later the same session, which made them per-chapter (`(10.1)`) — the two tasks share that
switch.

## What was done

- **`conf.py`:** `math_number_all = True` (numbers every displayed equation, the "like TeX"
  behaviour), `math_numfig = True` + `numfig = True` + `numfig_secnum_depth = 1` (per-chapter
  numbering, which also needs numbered sections — see the dependency below). A comment explains the
  mechanism and the `:numbered:` dependency.
- **`proof-rotate.rst`:** gave the chapter's result equation `\vec{r}(\vec{a};\theta) = …` the label
  `:label: eq-rotate-formula` — the formula cited from elsewhere.
- **Cited it with `:eq:`** where prose points at it: `geometric-product.rst` ("… in Proof: Rotate,
  equation (N)") and `proof-rotate-from-a-to-b.rst` (two spots: "the formula (N) of …", "the rotation
  (N) of …"). `:eq:` renders the number as a cross-document hyperlink in both builders.
- **`tasks/reference/book-outline.md`:** added a "Displayed equations are numbered, TeX-style" bullet
  under the proof-page notation conventions (label only what prose cites, `eq-<page>-<what>`,
  one `aligned` block = one number).

## Decision: labelling

`math_number_all` already numbers every equation, so the reader can point at any line; a `:label:` is
added **only** to an equation the prose refers back to (per the task's "every equation a proof refers to"). Only `eq-rotate-formula` met that bar across the current pages — the
other cross-references were prose/`:doc:` pointers to a whole page, not to a specific displayed
equation. The multi-line derivations are single `\begin{aligned}` blocks, so each takes one number
(not one per `&=` line).

## Dependency on the page/section-number task

Per-chapter equation numbers (`(2.3)`) need numbered sections, i.e. `:numbered:` on `index.rst`'s
toctree. That switch is owned by `tasks/archive/2026/10/09/pdf-section-and-page-numbers-for-print.md` (its plan step 2),
so it was added there, not here, to avoid a duplicate edit. Until it landed the equations numbered
straight through (`(3)`, `(4)`); the numbering infrastructure and the `:eq:` references were correct
either way. That task verified the per-chapter rendering (`(10.1)`/`(10.2)` on `proof-rotate`).

## Verification

- Built the book against the existing full image (`entrypoint/docs.sh`, nested podman): HTML + PDF
  both succeed ("build succeeded"; "Book built"). 24 equations carry numbers in the HTML.
- `eq-rotate-formula` resolves as a cross-document link in HTML
  (`geometric-product.html` → `proof-rotate.html#equation-eq-rotate-formula`) and in the PDF (final
  LaTeX pass has no undefined references).
- Pre-existing, unrelated warnings seen and left alone: a docutils "Undefined substitution: A" from
  the `exp` docstring's `|A|` (predates this work — `base.py` is unchanged on this branch), and the
  known missing-glyph `𝒢` fallback in FreeMono.
