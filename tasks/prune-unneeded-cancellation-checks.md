# Prune the cancellation checks that add nothing

**Status:** ready — decisions made, waiting for the go-ahead to execute
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book's notebooks show 171 "Terms with the same number cancel:" displays
(`show_difference` / `show_cancellation`), and the built PDF carries 185 of them over about
2,350 lines. Many prove an equality that is true by definition, undo a function with its own
inverse, or repeat a check an earlier cell or chapter already made. Remove the 38 listed below,
each with its lead-in sentence. Done = the
listed cells are gone, the prose around each still reads, and `make format`,
`make check-notebooks`, `make test` and `make docs` pass.

## The request (2026-11-22, the maintainer's words)

> take a look through the pdf, tell me, there's a lot of cancel stuff in there to prove stuff is
> equal that is really not necessary. take a look through, identify what you think should be
> pruned as it doesn't really add value, make a list of them to remove in the task, and when I
> tell you to do the task, remove them.

## Context

- Read first: `CLAUDE.md`, "Book: one name per operation…" (a companion notebook "shows both
  sides of each check before their difference", with `show_difference`, never a bare
  `simplify(left - right)`), and `tasks/reference/book-notebook-teaching-style.md` (the lines on
  `show_cancellation` / `show_difference`). That rule made every equality a cancellation cell;
  this task narrows it, and both docs get a sentence saying which checks are not shown.
- The helpers are in `src/gacalc/nbdisplay.py`. They stay; only calls are removed.
- How the list was made: every call was read with its lead-in
  (`tasks/adhoc/prune-unneeded-cancellation-checks/discover.sh` writes the 171 calls to
  `data/calls.txt`), and each rendered display was sized from `pdftotext` of
  `output/gacalc/geometry2.pdf` (631 pages, built 2026-11-22). The median display is 9 text
  lines; 13 run past 40.
- Line numbers are from 2026-11-22. `tasks/spell-out-basis-blades-as-vector-products.md` edits
  the same notebooks, so find each cell by the call's text.
- A cell with a Lean twin (`# twin: GacalcProofs.…` in the notebook's header) states a result
  and is kept. That rule moved two candidates off the list: `geometry-from-vectors.py`
  `(b - a) + (c - b)` against `c - a` (`triangle_sides_sum_zero`) and
  `projection-rejection-3d.py` `a * b - along` against `across`
  (`mul_eq_proj_dot_add_reject_wedge`).
- The four book pages with hand-written `\underbrace` marks (`book/docs/blade-square-sign.rst`,
  `proof-rotate.rst`, `proof-rotate-from-a-to-b.rst`, `reflection.rst`) are steps inside a
  derivation, not after-the-fact checks. They stay.

## What counts as unneeded

(The four reasons are this task's own grouping.)

- **D, by definition:** the two sides are the same computation, or one is a name for the
  other. Nothing could differ.
- **I, inverse round trip:** `f.inverse(f(x))` against `x`. The inverse was built to do that.
- **R, repeat:** the same equality was shown earlier, in this notebook or an earlier chapter.
- **P, property restated:** linearity or length-preservation proved again for each new way of
  writing the same rotation or reflection.

A check stays when it is the page's result, when it ties a hand construction to gacalc's own
method for the first time, or when it has a Lean twin.

## The list: remove (38)

Each row is one call; "lines" is the size of its display in the PDF where it is large.

| file:line | call | reason |
|---|---|---|
| `notebooks/vector-addition.py:105` | `show_difference(a + b, b + a)` | D: the prose above already says each coordinate is the same two numbers; 26 lines |
| `notebooks/vector-addition.py:149` | `show_difference((a - b) + b, a)` | D |
| `notebooks/vector-addition.py:161` | `show_difference(a - b, a + (-b))` | D: the definition of subtraction |
| `notebooks/vector-addition.py:207` | `show_difference(t(a), a + b)` | D: `t` is "add `b`" |
| `notebooks/vector-addition.py:255` | `show_difference(t.inverse(t(a)), a)` | I |
| `notebooks/vector-addition.py:273` | `show_difference(t.at(0.5)(a), a + b * 0.5)` | D |
| `notebooks/geometry-from-vectors.py:124` | `show_difference(at_values(segment_point, [(t, 0)]), a)` | D: substituting `t = 0` |
| `notebooks/geometry-from-vectors.py:136` | `show_difference(at_values(segment_point, [(t, 1)]), b)` | D: substituting `t = 1` |
| `notebooks/canonical-form.py:102` | `show_difference(sympy.sqrt(8), 4 / sympy.sqrt(2))` | R: both were just shown as `2√2` |
| `notebooks/geometric-product.py:222` | `show_difference((a + b) * R, a * R + b * R)` | P: distributivity of the product |
| `notebooks/relative-graph-paper.py:285` | `show_difference(f.inverse(f(p)), p)` | I |
| `notebooks/reflection.py:272` | `show_difference(a.reflected_across(b), reflection)` | R: `reflected_across` is projection minus rejection, shown equal one cell earlier; 23 lines |
| `notebooks/reflection.py:341` | `show_difference(reflection.magnitude_squared(), a.magnitude_squared())` | P |
| `notebooks/reflection-3d.py:117` | `show_difference(v.reflected_across(a), across_a)` | D: gacalc's method against its own formula; 51 lines |
| `notebooks/reflection-3d.py:207` | `show_difference(v.reflected_across(B), mirror)` | D |
| `notebooks/dual-3d.py:320` | `show_difference(b.projected_onto(a) + r, b)` | R: shown in `projection.py`, `projection-rejection-3d.py` and `proof-projection-3d.py` |
| `notebooks/defining-g2.py:406` | `show_difference(A.r_vector_part(0) + A.r_vector_part(1) + A.r_vector_part(2), A)` | D: the parts of `A` are `A` |
| `notebooks/displayg2.py:86` | `show_difference(e_12, e_1 * e_2)` | D: a name against the product it names |
| `notebooks/displayg2.py:194` | `show_cancellation((G2_1 * G2_2) * G2_3, …)` | R: the same associativity display is in `displaymv.py`, which carries the Lean twin |
| `notebooks/displayg3.py:90` | `show_difference(e_123, e_1 * e_2 * e_3)` | D |
| `notebooks/displayg2areas.py:213` | `show_difference(area(a, b), abs(signed_area(a, b)))` | D |
| `notebooks/displayg3measures.py:75` | `show_difference(area(a_vec, b_vec), area(b_vec, a_vec))` | D: the prose says an area has no direction |
| `notebooks/displaymv.py:360` | `show_difference(MultiVector.i(…), (… ^ …).normalize())` | D: `i(a, b)` is the normalized wedge |
| `notebooks/bootstrap-rotation.py:322` | `show_difference(v.rotate(theta).rotate(-theta), v)` | R: the case `φ = -θ` of the cell before it |
| `notebooks/bootstrap-rotation-from-projection.py:386` | `show_difference(rotated.magnitude_squared(), v.magnitude_squared())` | P: shown in `bootstrap-rotation.py` |
| `notebooks/bootstrap-rotation-from-projection.py:418` | `show_difference(rotated_sum, sum_of_rotated)` | P; the largest display in the book, 104 lines |
| `notebooks/bootstrap-rotation-from-projection.py:440` | `show_difference(rotated_multiple, Scalar(k) * rotated)` | P; 46 lines |
| `notebooks/bootstrap-projection-from-product.py:307` | `show_difference(projection + rejection, b)` | R: shown in `bootstrap-projection.py` |
| `notebooks/bootstrap-projection-from-product.py:321` | `show_difference(projection, b.projected_onto(a))` | R: follows from the two cells above it and `bootstrap-projection.py` |
| `notebooks/bootstrap-projection-from-product.py:333` | `show_difference(rejection, b.rejected_away_from(a))` | R: the same |
| `notebooks/frame-qr-2d.py:826` | `show_difference(g(x), y)` | I: the cell before it showed `g.inverse(y)` is `x` |
| `notebooks/frame-qr-3d.py:572` | `show_difference(f(x), y)` | I |
| `notebooks/proof-reciprocal-frame.py:442` | `show_difference(by_peel.inverse(by_peel(x)), x)` | I: the two inverses are shown equal below, and the reciprocal one keeps its round trip |
| `notebooks/proof-reciprocal-frame.py:466` | `show_difference(by_peel(by_peel.inverse(y)), y)` | I |
| `notebooks/proof-reciprocal-frame.py:682` | `show_difference(space_by_peel.inverse(space_by_peel(z)), z)` | I |
| `notebooks/proof-reciprocal-frame.py:706` | `show_difference(space_by_peel(space_by_peel.inverse(z)), z)` | I |
| `notebooks/bootstrap-rotation-from-product.py:289` | `show_difference(unit_product * v, rotation_by_projection(b, a, v))` | R: close to the cell at 269, and 46 lines (decision 1) |
| `notebooks/dual-3d.py:296` | `show_difference(product_r, swapped_r)` | too long to follow term by term, 84 lines (decision 1); the prose states the swap |

Where a notebook loses its last call, its `show_difference` import goes too. Removing
`displayg2.py:86` and `displayg3.py:90` changes two "keep" rows in the code table of
`tasks/spell-out-basis-blades-as-vector-products.md`; the sentence that the class names the
product `e_12` stays.

## Borderline: kept (23)

| file:line | call | why it might go | why it is kept |
|---|---|---|---|
| `notebooks/bootstrap-product.py:257` | `a * b` against `a.dot(b) + a.wedge(b)` | cells at 317 and 337 show each part | it is the page's headline identity |
| `notebooks/product-from-projection.py:251`, `:264` | `dot` against `|b| * x`; `wedge` against `|b| * y * e_12` | restate 185 and 198 | they name the parts |
| `notebooks/displaymv.py:455`, `:699` | an inverse times its value is `1` / the unit volume | I | the notebook is teaching the inverse |
| `notebooks/levels-of-abstraction.py:236` | the product against its grade-0 plus grade-2 parts | D | it shows there is no other grade |
| `notebooks/one-dimension.py:284` | `f(x)` against `m * x + b` | D | the prose is built around it |
| `notebooks/bootstrap-projection.py:318`, `:337` | the base cases onto `e_1` | D | first step of the from-scratch chain |
| `notebooks/proof-reciprocal-frame.py:430`, `:454`, `:670`, `:694` | the reciprocal inverse's round trips | I | one round trip per inverse per dimension |
| `notebooks/geometric-product.py:189`, `:239` | against `a.rotate(theta)`; against the basis decomposition | R | the first ties the page to gacalc |
| `notebooks/dual-3d.py:253` | regrouping inside a derivation | a step, not a result | it is a step of the argument, and short |
| `notebooks/three-dimensions.py:152`, `:170` | grade parts against `inner_product` / `outer_product` | D in gacalc | the page's claim in space |
| `notebooks/geometry-from-vectors.py:163`, `:235` | the half-way point against `m`; a length against a distance | D | each introduces a name |
| `notebooks/frame-qr-2d.py:221` | `v_2` against the rebuilt `v_2`; 40 lines | long | it is the QR statement |
| `notebooks/rotate.py:169` | the rotation for `a → b` against the one for `p * a → q * b` | minor | it is the scale-independence claim |

## Plan

1. Re-run `discover.sh`; find each listed call by its text.
2. Remove each cell together with its lead-in Markdown ("Their difference:", "Its difference
   from …"). Where the cells above showed both sides, they stay; where the lead-in sentence
   carried the claim, fold the claim into the prose as a plain statement.
3. Drop unused imports and names that only fed a removed cell.
4. Add the sentence on which checks are not shown (by definition, round trip, repeat, property
   restated) to `CLAUDE.md` and `tasks/reference/book-notebook-teaching-style.md`.
5. Gates: `make format`, `make check-notebooks`, `make test`, `make docs`.
6. Re-run `discover.sh`: 133 calls remain.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22, on the agent's recommendation:

1. **The borderline checks stay, except two removed for their length:**
   `notebooks/bootstrap-rotation-from-product.py:289` (46 lines, and close to the check before
   it) and `notebooks/dual-3d.py:296` (84 lines). Why the rest stay: each is a page's headline
   identity, names a part, ties a page to gacalc for the first time, or is a short step of an
   argument.

## History

All on 2026-11-22 (William Emerison Six <billsix@gmail.com>).

1. Asked for after reading the PDF. All 171 calls were read with their lead-ins and each
   display was sized from the PDF's text; 36 went on the removal list and 25 on a borderline
   list. Two first candidates came off because they have Lean twins.
2. The maintainer took the recommendation on the borderline list: all stay except the two
   longest, which moved to the removal list (38 to remove, 23 borderline, 133 remaining).
