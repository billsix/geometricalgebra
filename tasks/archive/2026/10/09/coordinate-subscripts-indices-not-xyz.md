# Write coordinates as `a_1`, `a_2`, not `a_x`, `a_y` — and introduce the notation for high-school readers

**Status:** complete
**Completed:** 2026-10-09 (work committed by the maintainer as `7d6e873` after the squash; archived,
with the one-shot codemod removed, in its own commit)
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer's ask (2026-10-08, verbatim): *"Use things like `a_1` instead of `a_x`, introduce the
notation for students familiar with high school geometry. Bill will likely need to consult a high
school text book for more context of what they would know."* The task swept every axis-letter
coordinate subscript out of the book's pages, companion notebooks and figure labels (106 hits, now
0), wrote the "How we write coordinates" passage that bridges from the reader's `(x, y)` and
`⟨a, b⟩ = a i + b j` to `a_1 e_1 + a_2 e_2`, and put the rule in the outline. `make docs` passed.

## Context (still true of the repo)

- **The rule and its rationale** live in `tasks/reference/book-outline.md` › "Notation & prose
  conventions for proof pages" (coordinates are `a_1`, `a_2`, `a_3`; the subscript names the basis
  vector it multiplies and survives 3D and 𝒢ₙ; a coordinate is a scalar, so no arrow; primes carry
  over). The code and the proofs already used indices — generated docstrings `a₁b₂ − a₂b₁`, Lean
  getters `a.c1`/`a.c2`, basis constants `e_1`/`e_2` — the book had been the outlier.
- **What the reader arrives with** is recorded in `tasks/reference/openstax-math-pedagogy.md`
  ("Coordinates and vectors: the notation the reader arrives with"): ordered pairs `(x, y)` from
  *Algebra 1*, component form `⟨a, b⟩` and `a i + b j` from *Precalculus 2e* §8.8.
- **The passage** is `book/docs/relative-graph-paper.rst` › "How we write coordinates", behind a
  `.. note:: Draft` banner for the maintainer's voice pass; the rest of that page is still a
  placeholder.
- **Decision (William Emerison Six <billsix@gmail.com>, 2026-10-09): the public `Vector.x`/`.y`/`.z`
  attribute views stay.** Renaming them is a SemVer-breaking change; the book's math says `a_1`, its
  code cells say `.x`, and the passage names the mismatch once. No `.c1`/`.c2` aliases.
- **Prose axis names stayed by design** ("the x-axis", "keep the x-coordinate", figure alt text):
  the rule is about subscripts, and the axis is still called the x-axis.

## Chronology (from the pre-squash commits `master..HEAD` and the session, 2026-10-08 → 10-09)

1. **Filed** 2026-10-08 with the maintainer's ask, a discovery table (60 hits across four pages,
   one figure, one notebook), the "why indices" rationale, and a plan whose first step — the
   high-school-text consult — was marked maintainer-gated.
2. **API question decided** 2026-10-09 (the decision above) in the sibling-task answers commit.
3. **Go-ahead** 2026-10-09 ("start the coordinate-subscripts-indices not xyz task"). The consult was
   done by the agent from the OpenStax ports instead of waiting on the maintainer.
4. **The work** (`7d6e873`, "use a_1 instead of a_x"). By then the hit count had grown to 106 in
   12 files, because the coordinate-proofs task (archived 2026-10-09) had added typed notebooks in
   the old spelling.

## What was done (all in `7d6e873`)

**The consult.** The pinned OpenStax content was fetched with each book's `fetch.sh` into impo's
gitignored `checkout/` (network was available; nothing downloaded was executed). *Algebra 1* Unit 1,
"Find Coordinates" (module `m00040`): a point is an ordered pair `(x, y)` with an *x*-coordinate and
a *y*-coordinate. *Precalculus 2e* §8.8 "Vectors" (module `m49412`): component form `⟨a, b⟩`, unit
vectors **i**, **j** along the axes, and vectors "in terms of i and j", `a i + b j`. The bridge
sentence the plan guessed was therefore right as written.

**The passage and the rule.** `relative-graph-paper.rst` gained the section (two prior notations with
their sources, `a = a_1 e_1 + a_2 e_2`, the two reasons for indices, "no arrow on a coordinate", the
`.x`/`.y` wrinkle). The outline gained the convention bullet. Foreshadowing in
`vectors-as-number-lines`/`trigonometry` was left to their own prose passes (both placeholders).

**The sweep.** `tasks/adhoc/coordinate-subscripts-indices-not-xyz/discover.sh` logged 106 hits to
`data/hits-before.txt`; every hit was read — no false positives (an ePiX `Point(x=…)` keyword never
matched). `fix.py`, a content-matching codemod, rewrote `\vec{a}_x` → `a_1`, `\vec{b}'_y` → `b'_2`,
`\vec{b}_z` → `b_3`, and plain `a_x` → `a_1` in notebook code, markdown, `sympy.symbols("…")` strings
and the `sp4` figure labels; a second run changed nothing; `data/hits-after.txt` is empty. Two hand
edits followed: the `proof-projection` notebook's locals for the *aligned* vector's coordinates
became `a_aligned_1`/`a_aligned_2` (the mechanical rename would have shadowed the module-level
symbols), and the passage and outline spell the rejected form `a_{x}` so the sweep's zero stays
meaningful. **Ordering:** this ran before `tasks/archive/2026/10/09/math-notation-parens-star-named-angles.md` (still
proposed), which touches the same equations and can run on top.

**The codemod bug, caught by the gate.** The first `make docs` failed in the PDF step
(`! Paragraph ended before \split was complete`): the codemod's optional closing brace after a
subscript had swallowed the brace of an enclosing `\frac{…}` in four numerators. The regex was
fixed to consume a brace only when the subscript opened one (unit-tested on the four shapes in the
book), the two damaged pages were reverted by path, and the final codemod was run once more (then
again: 0 changes).

**Gates.** `make docs` (`make -o image docs`): exit 0 on the second run, every notebook executed,
HTML and PDF built; the proof-rotate derivation page (`a_1/r`, `a_2/r`) and the projection page
(`\cos = b_1/|b|`, `a'_1 e_1`) read correctly in the PDF, and the `sp4` labels are `a'_1`/`a'_2`.
Locally: `ruff check .` / `ruff format --check .` clean, `ty check book/docs/notebooks` and
`tools/check_epix_keywords.py` pass, the five content notebooks execute, `discover.sh` = 0.

## Found, not fixed

The rotate-from-a-to-b page's bold step headings wrap `:math:` roles, which reStructuredText cannot
nest, so their LaTeX prints literally in HTML and PDF. Filed as
`tasks/archive/2026/10/09/fix-bold-nested-math-step-headings.md` (proposed — needs go-ahead).

## Open questions

None.
