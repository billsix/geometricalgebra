# The last three PDF overflows: 3D terms wider than their space

**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-20

After `tasks/archive/2026/11/20/pdf-long-math-overflow.md`, the PDF still cut off three places
(73 overfull boxes). Each had a single term wider than its space. Two were `show_mult` tables in
`notebooks/displaymv.py`, where every term of `B⁻¹` carried the 70-character denominator `|B|²`.
The third was the bare `volume(a_vec, b_vec, c_vec)` radical in `notebooks/displayg3measures.py`;
the task had first named a different cell. Now `make docs` reports 0 too wide and 0 too tall,
and fails the build if one comes back. How it works now: `tasks/reference/book-and-docs-pipeline.md`
("Notebook output in the PDF").

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-20:

1. The tables show `|B|²` as a named symbol rather than switching to a non-table layout.
2. Once the count is 0, `make docs` fails on a new overflow rather than only reporting it.

## What was done

- **`notebooks/displaymv.py`, "A bivector times its inverse":**
  - names `B_ab`;
  - shows `|B|² = B̃ * B`;
  - names it `sympy.Symbol("|B|^2", positive=True)` and builds `B⁻¹ = B̃ * (1/|B|²)`;
  - checks the name against `inverse()` with `show_difference(|B|² * B⁻¹, B̃)`;
  - shows the table;
  - puts the value back with `at_values` to show the product is 1.

  The check deliberately compares short forms. A `show_difference` of the long fractions would
  overflow again.
- **"A bivector and its dual":** the same pattern, ending at `e₁₂₃`. It uses
  `|B|² * (B*)⁻¹ = B*`, since a vector's inverse is itself over its squared size.
- **`notebooks/displayg3measures.py`:** the cell shows `sympy.simplify(sympy.sympify(volume(…)))`,
  which is `√(det²)`, 44 visible characters. Its text points to the signed volume in the next
  cell. This was simpler than the planned name-both-sides version.
- **`entrypoint/docs.sh`:** records the check's status, copies the PDF and log either way, then
  exits 1 on overflow.
- **Found while looking at the pages** (the check's 0 was not enough):
  1. **Bars split table cells.** The `|` in `|B|^{2}` ended the Markdown table cells, so the
     cells printed raw LaTeX and the check saw nothing wide. Added `nbdisplay._table_cell`, which
     writes `|` as `\vert` and `\|` as `\Vert` in every table cell (a CHANGELOG Fixed entry).
  2. **Tables ran off the page.** Each table was then about 1,100pt tall: a tabulary of fewer than
     30 rows cannot break across pages, and four rows were never printed (`Overfull \vbox
     (488.6pt too high)`). The cause was `base.latex_visible_length`, which counted a fraction's
     numerator plus its denominator. It now counts the wider of the two (a new `_brace_group`
     helper).
  3. **Undercounted commands.** That exposed an undercount the double count had hidden: every
     command counted 0, so `\cos(\theta)` counted 3, and six rotation-page equations overflowed
     (the new gate caught them). Now operator names count their letters, `\quad` 2, markup
     (`_LATEX_MARKUP`) and `\begin{…}` / `\end{…}` 0, and any other command 1
     (`_command_glyphs`). This is a CHANGELOG Changed entry.
  4. **Tall boxes now fail too.** `tools/check_math_overflow.py` also counts `Overfull \vbox`
     boxes over the tolerance as failures.
- Docs: `CLAUDE.md` (`make docs` bullet), the pipeline reference doc (four bullets: naming a
  long part, the bar, tall tables, the gate).

## Verification

- Final `make docs` run (the `docs.sh` `podman run`): 0 overfull boxes of every kind;
  `0 equations and tables more than 10pt too wide`, `0 boxes more than 10pt taller than the
  page`, exit 0. Before: 73 wide boxes. Four builds were needed, one per finding above.
- Looked at the PDF pages. Both tables show all nine rows within the margins on one page each;
  the volume radical fits.
- The "Missing character U+007F" lines the build prints predate this work and are harmless
  (`tasks/archive/2026/11/17/notebook-text-vector-notation-matches-output.md`).
- `pytest -m "not slow"`: 1407 passed, 3 skipped. `entrypoint/format.sh`: exit 0.
