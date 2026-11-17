# Notebook text writes vectors the way gacalc's output typesets them

Done 2026-11-17, in two commits: the main work (`cb74f2c`), then the follow-ups (figure labels and
a prose-width checker), done the same day after the task was reopened. Asked for by William Emerison Six <billsix@gmail.com>: "in the output … the vectors
are bold and have an arrow over them, but when I look at the text part of the notebooks, vectors
don't." The book's math now writes vectors and basis blades the way `blade_latex`
(`src/gacalc/base.py`) prints them, and the rule is in `CLAUDE.md` › "Math notation for readers".

## What the output did, and what the text did

- **The output:** every multivector's LaTeX goes through `blade_latex` / `blade_dict_latex`. A basis
  vector was `\mathbf{\vec{e}}_{1}`. A higher blade was its vectors side by side,
  `\mathbf{\vec{e}}_{1} \mathbf{\vec{e}}_{2}`. Coefficients come from `sympy.latex`, plain italic.
  The output never names a vector by letter.
- **The text:**
  - Notebook Markdown wrote plain `$a$` (`$a$` alone 137 times), `$e_1$`, `$e_{12}$`, `$e_1 e_2$`
    and `$\hat{a}$`.
  - Figure labels wrote `$\vec{a}$`, an arrow but no bold.
  - The `.rst` pages wrote `\vec{a}` (about 900 times) and plain `e_1`.
  - `tasks/reference/book-outline.md` convention 5 said basis vectors were written plain.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-17)

1. **Scope: everything a reader sees typeset.** That is the notebooks' Markdown, the figure labels
   (notebook code cells and `book/figures/epix/*.py`), and the `.rst` pages.
2. **A blade of grade 2 or more is one bold `\mathbf{e}_{12}`, with no arrow.** `blade_latex`
   changed to match, so the prose and the output agree. It matches the code's `e_12` and avoids a
   product written without `*`.
3. **Capital multivectors and rotors (`R`, `B`, `I`) stay plain.** The output never names them,
   and a plain `R` matches the function labels `R_{…}^{…}`.

Two smaller decisions came up along the way:

- **Spelled out, not a macro.** Jupyter does not see Sphinx's MathJax macro config.
- **No line-length check on the book's notebooks and figure scripts** (`pyproject.toml`
  per-file-ignores). A single `$...$` span or a heading can pass 88 columns once its vectors are
  bold, and it can't be broken. An inline `# noqa` would show in the student's view. `ruff format`
  still wraps their code, and prose paragraphs were rewrapped at 88.

## The PDF never drew the arrow, so the spelling is `\vec{\mathbf{a}}`

The first build after the rewrite printed 39 "Missing character: U+007F in FreeSerif/B" warnings.
Earlier builds printed none. Rendered at 250 dpi, the PDF showed every `\mathbf{\vec{x}}` as a bold
letter crossed by a garbled glyph, with no arrow. The output's own basis vectors had always looked
like that in the PDF (`y_1\mathbf{\vec{e}}_1` on page 176). Under fontspec, lualatex takes the
accent inside `\mathbf` from the bold text font, which has no arrow. MathJax (HTML, Jupyter) draws
it fine.

Redeclaring `\vec` with `\DeclareMathAccent` in the preamble did not help; a test document showed
the same garble. **`\vec{\mathbf{a}}`, with the accent outside the bold, draws a real arrow over
the bold letter**, with no warnings, and MathJax renders it the same as before. So every spelling
was switched to it: the library output (`\vec{\mathbf{e}}_{1}`, with the CHANGELOG entry), the
text, the docs, and `rewrite.py`. A one-line `perl` swap over 93 files made the switch; a fresh
run of the updated scripts on HEAD reproduces the result.

## What changed

- **`src/gacalc/base.py` `blade_latex`:**
  - A vector renders `\vec{\mathbf{e}}_{1}`.
  - A grade-≥2 blade renders `\mathbf{e}_{12}`. The indices are joined, with commas once an index
    has two digits (`\mathbf{e}_{1,10}`).
  - The doctests were updated, and `CHANGELOG.md` has two `[Unreleased]` › Changed entries.
- **The rewrite: 85 files** (all 30 book notebooks, the `.rst` pages, the figure scripts). The
  script `tasks/adhoc/notebook-text-vector-notation-matches-output/rewrite.py` rewrote, inside math
  only:
  - `\vec{a}` → `\vec{\mathbf{a}}` and `\hat{a}` → `\hat{\mathbf{a}}`;
  - `e_1` / `e_i` → `\vec{\mathbf{e}}_1`, `e_{12}` → `\mathbf{e}_{12}`, and the plane name
    `e_1 e_2` → `\mathbf{e}_{12}`;
  - in notebook Markdown, the bare letters the notebook binds to a vector.

  Which letters are vectors comes from the notebook's own bindings: a lowercase `Vector` or
  `MultiVectorBase`, following the Hestenes naming rule. A name bound with an index (`v_1`) makes
  `v_1`, `v_i` and `a^1` vectors. Otherwise a subscripted letter is a coordinate and stays plain.
- **Exceptions:**
  - **Letters the bindings miss**, set as overrides in the script: `v` in `proof-cross.py`
    (`in_plane`'s argument) and in `vector-addition.py` (`translate`'s input point), and the
    remainder vector `r` in `frame-qr-2d.py`, whose code uses `r` for a coordinate.
  - **`blade-square-sign.rst`** keeps `e_1 e_2` as two vectors, because its products are being
    slid apart, not naming a plane.
  - **The sliding diagrams** in that page are literal blocks, not math, and stay in plain `e_1`.
- **Reflow:** `reflow.py` rewrapped the Markdown paragraphs the rewrite pushed past 88 columns.
  Each paragraph was rewrapped whole, never inside a `$...$` or backticked span.
- **Docs:**
  - `CLAUDE.md` gets the new rule bullet, and its `*` examples use the new notation.
  - `tasks/reference/book-notebook-teaching-style.md`: the "Write the prose math as LaTeX" rule and
    the checklist.
  - `tasks/reference/book-outline.md`: convention 5 replaced, and its examples updated.
  - `tasks/reference/reduction-to-standard-position.md`: one formula.
  - `book/docs/relative-graph-paper.rst` now tells the reader a vector is written bold with an
    arrow, as gacalc prints it.

## Verification

- **Review of what stayed plain:** after the rewrite, every single letter still plain in a
  notebook's or page's math was listed and read. They were coordinates, angles, scalars like `k`
  and `m`, function names (`f`, `r(v; θ)`, `t`), or quotations of the reader's prior notation
  (`⟨a, b⟩`, `f(x) = m*x + b`). The three vectors found among them became the overrides above.
- **Both scripts are idempotent:** a second run changes nothing. Their result is also the same as
  one fresh run: the scripts plus `ruff format` were run on a `git archive HEAD` copy, and
  `diff -r` against the working tree was empty.
- **Every book notebook was checked:** ruff, `ty`, `tools/check_annotations.py`, every cell run and
  every figure rendered. All 30 passed.
- **Gates:**
  - `make test`'s suite (`-m "not slow"`): 1367 passed.
  - `ruff check` and `ruff format --check` over `src`, `book`, `tests` and `tools`, and `ty check src`.
  - The book build (HTML, PDF, ePiX figures): `docs.sh` exit 0.
- **The arrows were checked by eye** in the PDF (page 176, `frame-qr-3d`) and in a figure
  (`_static/epix/add2.png`).
- **The PDF build still prints 39 "Missing character: U+007F in FreeSerif/B" lines.** U+007F is the
  math font's skew character, which lualatex uses to position an accent over its letter, and it
  looks it up in the bold text font. The rendered arrows are correct; only that kerning lookup is
  missing.

## Follow-ups, done after reopening (William Emerison Six <billsix@gmail.com>, 2026-11-17)

### The rewrite had four bugs in notebook code, found by viewing every figure

All 48 book figures (`book/docs/_static/epix/`) and the notebooks' live figures were tiled into
contact sheets and read. Doing so turned up four bugs in `rewrite.py`, plus labels it could not see:

- **`ece₁` in labels.** `frame-qr-2d.py` and `frame-qr-3d.py` wrote some labels as plain
  (non-raw) strings, `"$e_1$"`. The rewrite put `\vec` into them, which Python reads as a
  vertical tab. The rewrite now adds an `r` prefix when it puts a backslash into a plain string.
  No plain-string label held a backslash before the rewrite; a `tokenize` scan of the pre-rewrite
  notebooks checked this.
- **Vector names in figure labels stayed plain.** The labels got only the mechanical swaps, so
  `$v_2$`, `$w_1$` and `$y$` in the frame notebooks were not bolded. Labels now use the notebook's
  own vector letters, as its prose does.
- **f-strings.** Once labels were rewritten, f-string labels broke: the inserted braces read as
  format fields. `rewrite_label` now parses the f-string (`split_fstring`: `{{` and `}}` are
  literal, `{…}` is a field), rewrites the text, doubles the new braces, and puts the fields back.
  A string the rewrite does not change is left alone.
- **`b''_2` was bolded as a vector.** The primes hid the subscript that marks a coordinate. The
  check now skips primes first.
- **Missed by hand:**
  - Six label pieces in the frame notebooks split one `$...$` span across two string literals
    (`r"$x_2 = \frac{w_2 \cdot y}…" rf"…$"`), so the regex never saw a whole span.
    `rewrite_math` was applied to those six lines by hand.
  - `proj3.py`'s two-piece title label was fixed the same way.

The four notebooks these bugs touch (`frame-qr-2d.py`, `frame-qr-3d.py`, `proof-cross.py`,
`proof-reciprocal-frame.py`) were regenerated by running the fixed scripts and `ruff format` on
their pre-rewrite versions (`cb74f2c~1`), then copied in. That diff was read line by line before the
copy.

### Labels moved off arrows and lines

The bold labels are wider, and some were already tight. Each move was checked by rendering:

- **Book figures:**
  - `add2`: `b` moved to the middle of the dashed arrow.
  - `add3`: `a + b` lifted off the tip.
  - `sub2`: `a − b` moved off the dashed line.
  - `boot_sp4` and `sp4`: the coordinate labels moved under the middle of their arrows, and `a'_2`
    moved off its line.
  - `sp5` and `proj2`: `proj` moved below-right of the foot; in `proj2`, `rej` moved right of its
    line.
  - `rotate_ab_step3`: the result label moved right of its tip, away from `y`.
  - `trans2`: `O'` moved below its point, away from `P`.
- **Notebooks:**
  - `frame-qr-3d.py`, four figures: `v₁ = w₁`, `w₂`; `|w₃| = 2` and the base area, now in the open
    corners; the three `f(eᵢ)` labels; `−x₂ * v₂`.
  - `proof-rotate-from-a-to-b.py` (`b'`, `b`), `rotate.py` (`b`): moved off the purple arrow that
    continues them.
  - `rotation-from-vectors.py`: `v` below its arrow, which lies on `a`'s; `R(v)` left of its tip.
  - `proof-reciprocal-frame.py`: the three short reciprocal vectors each get their own label
    placement.

### `tools/check_notebook_prose_width.py`

`reflow.py` was promoted to a checker, because E501 no longer covers the book's notebooks and
figure scripts:

- **What it reports:** a Markdown paragraph with a line over 88 columns that rewrapping would
  change. A paragraph whose only long line is an unbreakable `$...$` or backticked span is already
  as narrow as it can be, and is not reported.
- **`--fix`** rewraps such a paragraph whole.
- **Where it runs:** `entrypoint/format.sh` runs it, which makes it a `make format` step. It is
  documented in `tasks/reference/book-and-docs-pipeline.md`, `CLAUDE.md`, the teaching-style doc
  and the `pyproject.toml` comment.
- **Checked against `reflow.py`:** it passes on the tree. On a fresh rewrite without `reflow.py`, it
  reported 195 paragraphs, and `--fix` produced output byte-identical to `reflow.py`'s.

### Verification of the follow-ups

- **Each changed notebook passed**: ruff, `ty`, `tools/check_annotations.py`, every cell, and every
  figure rendered and viewed.
- **Final gates:**
  - `entrypoint/format.sh` passed, including the new checker.
  - The test suite (`-m "not slow"`): 1367 passed.
  - `pyright notebooks/` (`make check-notebooks`): 0 errors.
  - The book build: `docs.sh` exit 0, with the same 39 harmless skew-character lines as before.
