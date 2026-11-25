# One Dimension: teach plotting from scratch, then scale and translate on relative number lines

**Status:** question 1 answered 2026-11-25 (see Decisions); question 2 is still open and blocks the rest; not started
**Priority:** 3
**Difficulty:** 5
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## BLUF

The chapter *One Dimension: m·x + b* (`book/docs/one-dimension.rst`, `notebooks/one-dimension.py`) should teach a
reader how to plot, from nothing, so they can unlearn plotting at right angles and build it up again. Today it
opens with the formula split into a scale and a translate, shows graph paper first, and then draws a pair of
number lines with green and blue arrows whose point the maintainer could not see. The rewrite drops the blue
arrows, builds the plot from a table on number lines, ends by turning the output with `e_1 * e_2` to land on the
familiar graph, and only afterwards shows scale and translate the way `relative-graph-paper` shows a composition:
the origin moves, the relative number line scales, and a point can be counted on either line. Done = the page and
notebook read that way, the two open questions are answered, and `make format`, `make check-notebooks`,
`make test` and `make docs` pass.

## The request (2026-11-22, the maintainer's words)

> add a new task to talk about that one dimension part of the book. I don't understand what the blue arrows are.
> I just literally want it to be like teaching someone how to plot, so they can unlearn plotting perpendicularly,
> to build it up again. I thought the part about the rotation by multiplying by e_1 * e_2 would have gone at the
> end of this section, to bring it all home. Also, if the blue arrows are supposed to be about a translate/scale,
> it should be done afterwards, and more like the other composition thing we do, where the origin moves, and the
> relative number lines scale, so you can count on either number line.

## Context

- Read first: `CLAUDE.md` ("Book: one name per operation…", "Math notation for readers", the notebook rules);
  `tasks/reference/book-outline.md` and `tasks/reference/teaching-order-and-dependencies.md` (a construction may use
  only results taught before it; the dependency graph on the book's first page is
  `book/docs/proof-dependencies.dot`); `tasks/reference/book-notebook-teaching-style.md`.
- **What the chapter does today.** Three parts. (1) "Two pieces": the input is `x * e_1` on a number line; the
  uniform scale `S_m` stretches it by `m`, the translate `T_b` slides it by `b`; `f = T_b ∘ S_m`
  (`eq-mx-plus-b`, cited by both reference cards). (2) The notebook
  draws the familiar graph paper for `y = m * x + b`: families of slopes (`b = 0`) and intercepts (`m = 1`).
  (3) "Along one direction": for each input `x` a number line on the left shows `x * e_1` in black and a second
  number line on the right shows the output, with the **scale step** `m * x * e_1` as a green arrow and the
  **translate step** `b * e_1` as a **blue** arrow lifted above the line, landing on a purple dot; then all eleven
  rows are stacked and the reader is asked to tilt their head. The figures come from
  `src/gacalc/epixscene/line_scene.py` (`number_lines_scene`, `number_line`, `step`, `tip`; `graph_paper_scene`,
  `graph_line`).
- **Why the blue arrows lose the reader.** They show the second half of a composition before the reader has seen
  why the output sits on a second line at all. The arrow starts at the end of the green arrow on a line that is
  not the input's line, so it reads as a new, unexplained quantity, not as "the same point, counted from a moved
  origin". The page asks the reader to follow two functions and a plot at once.
- **The page this task relies on.** `book/docs/plotting-a-table.rst` and `notebooks/plotting-a-table.py` (committed
  2026-11-22, `tasks/archive/2026/11/22/book-plot-by-table-quarter-turn.md`) already take a table, draw each row on
  one line, multiply each output by `e_1 * e_2`, and put it at the input's tip: `p(x) = x * e_1 + f(x) * e_2`. It is
  placed right after `geometric-product` because it uses `e_2` and the product `e_1 * e_2`, which come later than
  `one-dimension` (decision 1 of that task).
- **The composition style the maintainer wants for scale and translate:** `book/docs/relative-graph-paper.rst` and
  `notebooks/relative-graph-paper.py` ("Two ways to read a composition"): a function carries the whole sheet, its
  origin and unit arrows included; a point keeps its coordinates on the carried sheet; read right to left (every step
  measured on the standard sheet) or left to right (every step measured on the relative sheet the earlier steps left
  behind). `vectors-as-number-lines.rst` already calls a vector "a relative number line".

## Proposed shape (a draft for the maintainer to correct)

1. **A table.** Fill in inputs and outputs for one concrete function (for example `f(x) = 2 * x + 1`, inputs
   `-3..3`), the way a child does. No axes yet, no formula split.
2. **Draw each row on number lines.** The input on one number line, the output on a second, both pointing the same
   way, a dot at each. One row, then a few, then all rows stacked. Say plainly what each picture is: "this input goes
   to this output". No arrows other than the input and output positions.
3. **Look at the stack.** The dots are no more a graph yet than a list of numbers is. This is the point to say why
   plotting needs a second direction, so the reader meets the right-angle habit as a choice, not a given.
4. **Bring it home.** Turn each output with `e_1 * e_2` and put it at the tip of its input: the familiar graph, built
   from the rows (this is `plotting-a-table`; see question 1 for where it lives).
5. **Afterwards, scale and translate.** `f = T_b ∘ S_m` shown as two relative number lines: the output line is the
   input line with its origin moved to `b` and its unit stretched by `m`, so the same point reads `x` on one line and
   `m * x + b` on the other. Count on either. Drawn the way `relative-graph-paper` draws a carried sheet. No blue
   arrow.

## Open questions (Q1 answered 2026-11-25, Q2 still open)

1. **Where does the turn by `e_1 * e_2` go?** The maintainer expected it at the end of this chapter. It is now its own
   page after `geometric-product` because the turn needs `e_2` and the product, taught later (a construction may use
   only results taught before it), and the one-dimension chapter works in 𝒢₁, where there is no `e_2`. Three
   positions: **(a)** keep the turn on `plotting-a-table` and make the one-dimension chapter end by naming the
   missing second direction and pointing forward to it, so the two pages read as one story; **(b)** move the turn
   into the end of the one-dimension chapter and introduce `e_2` and `e_1 * e_2` there, before
   `geometric-product`, which breaks the teaching-order rule and the dependency graph; **(c)** split the story into
   two chapters at the same point in the book, "Plotting, part 1" in 𝒢₁ and "Plotting, part 2" in the plane, with
   `geometric-product` between them. I recommend (a): it keeps the rule, costs the least, and the forward pointer
   is the "bring it all home" line the maintainer wants. Which one?
2. **Where do scale and translate on relative number lines go, given the answer to 1?** The maintainer wants them
   after the plot. With (a) the plot is two pages later, so the section would sit on `plotting-a-table`, after the
   turn, where it can reuse `relative-graph-paper`'s language; the one-dimension chapter would then no longer mention
   `S_m` and `T_b` at all, and `eq-mx-plus-b` (cited by `cheat-sheet-2d.rst` and
   `cheat-sheet-3d.rst`) would move with it. The alternative is to keep the section on `one-dimension` after the
   stacked number lines (before the turn), which keeps `eq-mx-plus-b` where it is. I recommend the section follow
   the plot, on `plotting-a-table`, and that `eq-mx-plus-b` move there with the cards' citations updated. Is that the
   order you want?

## Plan

1. Settle questions 1 and 2.
2. Rewrite `notebooks/one-dimension.py` and `book/docs/one-dimension.rst` per steps 1 to 3 (and the end-of-chapter
   pointer of answer 1(a)). Remove the blue and green step arrows and the translate/scale pictures from the chapter.
3. Write the relative-number-line scale and translate section (step 5) in the notebook and page it lands on; new
   helpers in `src/gacalc/epixscene/line_scene.py` for a number line whose origin and unit are those of a function
   (`number_line` takes `origin` today; it needs a unit), with every argument by keyword.
4. Update what cites the old chapter: `eq-mx-plus-b` in `book/docs/cheat-sheet-2d.rst` and `cheat-sheet-3d.rst`; `book/docs/proof-dependencies.dot`; `tasks/reference/book-outline.md`;
   `tasks/reference/teaching-order-and-dependencies.md`; `notebooks/README.md`; the forward pointer at the end of
   `one-dimension.rst` to `plotting-a-table`.
5. Three forms: the Lean twin of the turn already exists (`plotted_point_eq`); the relative-number-line section needs
   a check in the notebook (`f(x)` counted on the input line and on the output line agree, with symbols), and a Lean
   theorem only if the maintainer wants one (the content is the definition of `T_b ∘ S_m`).
6. Gates: `make format`, `make check-notebooks`, `make test`, `make docs`.

## History

1. 2026-11-22 (William Emerison Six <billsix@gmail.com>): asked for after reading the chapter and the new
   `plotting-a-table` page. Two questions are open; the shape above is a draft.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-25)

1. Position (a): keep the turn on `plotting-a-table`, and make the one-dimension chapter end by naming the missing second direction and pointing forward to it, so the two pages read as one story. This keeps the teaching-order rule and costs the least.

Question 2 (where scale and translate on relative number lines go, given 1) was not asked and is still open; it blocks the remaining work.
