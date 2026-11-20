# Show every "these terms cancel" check with numbered underbraces

**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-11-20

The maintainer liked how `notebooks/displaymv.py` showed a cancellation: each pair of cancelling
terms under an `\underbrace{…}_{k}` with the same number `k`, so a reader matches the pairs on
screen, or crosses them off on a printout. The sweep found every place in the book (notebooks and
`.rst` pages) that showed or checked that something cancels and rewrote it that way. The rule is
in `CLAUDE.md` ("Book: one name per operation…": a check's difference is shown with
`show_difference`, never a bare `simplify(left - right)`).

## Decisions

(William Emerison Six <billsix@gmail.com>, 2026-11-20.)

1. `blade-square-sign.rst`'s ASCII `\__/` brackets became numbered `\underbrace`s, with the rule
   (Rule 1, Rule 2) kept as text beside each line. With the diagrams out of ASCII, the page's
   "we leave out the `*` so the columns line up" note and `CLAUDE.md`'s matching juxtaposition
   exemption were removed: the diagrams now write every `*`.
2. Scalar cancellations that are not a left-vs-right identity got the same numbered
   `\underbrace` on each cancelling factor (`proof-rotate.rst`'s `r`'s).

## What changed

- **`src/gacalc/nbdisplay.py`.** `cancellation_latex` / `show_cancellation` accept numbers as
  well as multivectors. New `show_difference(left, right)` shows just the numbered cancellation,
  for a check whose sides the notebook has already shown (the common "Their difference:" cell).
  Each side is simplified first, then expanded into monomials; equal monomials (equal after
  expansion, so `1.0*x` pairs with `x`) are paired. Sides that only cancel over a common
  denominator are multiplied by it, and the line says so. A blade that is 0 on both sides is
  skipped. A line longer than `LONGEST_CANCELLATION_LINE` (3000 LaTeX characters) shows only
  `left - right = <simplified>`. `product_table_markdown` (so `show_mult`) numbers the
  monomials of the table's products that cancel in the sum (a term and its negative of the same
  blade), and `show_mult` then says "Terms with the same number cancel in the sum".
- **Notebooks: 152 check cells converted.** The one-shot codemod `convert_difference_cells.py` (in 5ecae03, removed at archive)
  rewrote 149 cells: each code cell after a Markdown cell mentioning a difference whose body was
  `sympy.simplify(sympy.sympify(L - R))`, `sympy.simplify(L - R)`, `(L - R).simplified()`,
  `(L - R).expanded()` or bare `L - R` became `show_difference(L, R)`, with the import added.
  Its second run changed nothing. Three multi-line cells were converted by hand
  (`displayg3.py` associativity, `displaymv.py` plane projection, `displayrotations.py`
  exponential rotor).
- **Pages.** `blade-square-sign.rst` (grades 1–3 and the worked `e₁ * e₂ * e₁`),
  `proof-rotate.rst` (an added step with the four `r` pairs numbered),
  `proof-rotate-from-a-to-b.rst` (the second coordinate of `R(a)` written out with its pair
  numbered, and the sandwich's inverse pair), `reflection.rst` (the `b … b⁻¹` pair, now a
  display).

## Opted out, with reasons

- `defining-g2.py`'s `a - b`: the markdown's "difference" is the vector `a - b` itself, not a
  check. `proof-reciprocal-frame.py`'s `delta_table - sympy.eye(2|3)`: matrices; the table of
  dots is shown entry by entry already. Both are in the codemod's `SKIP` list.
- Single-quantity "is 0" checks (`a.dot(r)`, `d.cosine(a)` …): sympy combines like terms when it
  builds the value, so there are no terms left to number. They stay `simplify(…)`.
- Prose that mentions cancelling but shows no terms (`rotation-from-vectors.rst`'s magnitudes,
  the `displayg3.py`/`displaymv.py` "predict…" prompts): nothing to mark; where the terms appear
  in a following `show_mult`, its table now numbers them.
- Checks whose sides cancel only through a square-root or trigonometric identity show no pairs:
  `rotate.py`'s `v.rotate(θ)` against `rotate_a_to_b(v)` (atan2 forms) lists the terms and the
  residual's simplification to 0; `bootstrap-rotation-from-product.py`'s sandwich against the
  one-sided product and `reflection-3d.py`'s large 3D checks pass the length limit and show
  `left - right = 0`.
- `canonical-form.py`'s decimal against `5/6` is meant to be nonzero; it now shows the two
  fractions and their difference `1/27021597764222976`.

## Verification

- `execute_notebooks.sh` (`tasks/adhoc/cancellation-underbrace-everywhere/` in 5ecae03) ran all 43 notebooks in
  the image: all executed; `scan_outputs.py` listed 319 cancellation lines, 14 flagged, which
  led to the simplify-first step (a 3D round trip in `proof-reciprocal-frame.py` had stalled
  expanding unsimplified sides), the length limit (two 38k-character lines), the zero-blade skip
  and the float-tolerant pairing. A re-run of the flagged notebooks left only the opt-outs above.
- `format.sh` (ruff, ty) clean; `pytest -m "not slow"` 1396 passed.
- `make docs`: see the PDF task's verification (`tasks/archive/2026/11/20/pdf-matplotlib-figure-repr-text.md`),
  one build for both.

The discovery snapshot (`data/discover.txt`, from `discover.sh`) and the codemod's
`data/unmatched.txt` are the worklog; the scripts are one-shot and are removed at archive.
