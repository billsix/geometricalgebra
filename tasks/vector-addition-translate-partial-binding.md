# Vector addition page: show `translate`, partial binding, and the whole graph paper sliding

**Status:** proposed — needs go-ahead (voice question decided 2026-10-09: agent drafts with a
`Draft` banner)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

In the vector-addition section (`book/docs/vector-addition.rst`, prose still `TODO`), after
tip-to-tail addition, show **`translate`**: adding a fixed vector `b` to *every* point is a
function, `translate(b)`, which is "`+` with its second argument already filled in" (**partial
binding**), and applying it moves **the whole graph paper** by `b` — every point, the axes, the
grid — not just one arrow. Maintainer's ask, 2026-10-08: *"in the section on vector addition,
show translate and how it's like partial binding, and how it moves the whole graph paper."*
"Done" = a "Translate" subsection on the page (prose + one or two ePiX figures), the companion
notebook `book/docs/notebooks/vector-addition.py` demonstrating `translate(b=…)` on several
points, and `make docs` green.

## Context (read first)

- **The library object:** `translate(b)` in `src/gacalc/transforms.py` (doc regions
  `translate signature` / `translate body`) returns an `InvertibleFunction` with
  `f(x) = x + b`, inverse `x - b`, `Linearity.AFFINE`, and `interpolate = lambda t: translate(b * t)`
  (a slider from "not moved" to "moved by b" — usable for an animated/stepped figure later).
  The parameter is **named `b` on purpose** (`f(x) = m*x + b`, the intercept) and is called by
  keyword in teaching code: `translate(b=2 * e_1 + 1 * e_2)` — `CLAUDE.md` › "`m` and `b` are
  protected terse names". Full layer map: `tasks/reference/transform-and-composable-function-layer.md`.
- **The 1D precursor:** `book/docs/one-dimension.rst` (placeholder) is the `m·x + b` chapter —
  "input value on the left, output on the right, on overlaid graph paper". `translate` is the 2D
  `+ b` half of that line; the vector-addition page should say so explicitly and the 1D page, when
  written, should foreshadow it.
- **"Moves the whole graph paper":** `book/docs/relative-graph-paper.rst` (placeholder) introduces
  two vectors as relative graph paper. The translate figure is the first time that graph paper
  *moves* — a copy of the grid slid by `b`, with the same point labelled before and after. That is
  also the visual for "partial binding": one function, applied to everything at once.
- **"Partial binding"** appears nowhere in the repo yet (grep 2026-10-08) — the page must define
  it for a student: a two-blank formula `□ + □` with one blank filled by `b` becomes a one-blank
  machine `□ + b`; feed it any point. (The library's `translate(b)` *is* that machine; Python's
  `functools.partial(operator.add, b)` is the same idea if a code aside helps.)
- **Existing figures on the page:** `add1`–`add3`, `sub1`–`sub2` (`book/figures/epix/`, shared
  constants in `_addition_scene.py`). A translate figure fits the same scene: reuse `a`, `b` from
  `_addition_scene.py`; draw the grid (new helper, `_scene2d.py` has axes via
  `unit_circle_scene(disc=False)` but no grid yet) and its translated copy.
- The interactive-calculator page (`interactive-calculator.rst`, placeholder) lists "vector
  addition, rotate, translate" — this section is where translate gets its definition.

## Plan

1. **Prose** (`vector-addition.rst`, new subsection "Translate: adding the same vector to
   everything"): (a) `a + b` as a one-off; (b) fix `b`, vary `a` → a function; name it
   `translate(b)`; (c) partial binding in one paragraph; (d) apply it to every grid point → the
   graph paper slides; the picture; (e) its inverse is `translate(-b)` (sets up subtraction, which
   the page already covers). Tie to `m·x + b` in one sentence.
2. **Figures** (`book/figures/epix/`, keyword-args-everywhere + typed, per the house rules):
   `trans1` — the grid and a few labelled points; `trans2` — the same grid slid by `b`, old grid
   faint, each point's displacement arrow drawn. Add a `grid(...)` helper to `_scene2d.py`.
3. **Notebook** (`book/docs/notebooks/vector-addition.py`, currently the `1 + 1` stub): build
   `a`, `b` from basis constants (`2 * e_1 + 1 * e_2` form); `t = translate(b=b)`; apply `t` to
   `a`, to the basis vectors, to a list of grid points; show `t.inverse()(t(a)) == a`; show
   `t.interpolate(0.5)` as "half-way". Coordinates alongside each (per
   `tasks/coordinate-proofs-alongside-early-results.md`: `(a_1 + b_1, a_2 + b_2)`).
4. `make docs`; eyeball the two PNGs; note the new helper in
   `tasks/reference/book-and-docs-pipeline.md` ("Shared helpers").

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-09)

1. **Draft the prose in the agent's voice with a `.. note:: Draft` banner** for the maintainer's
   voice pass (the pattern of `tasks/levels-of-abstraction-book-voice-pass.md`), rather than leaving
   the prose `TODO`.

## Open questions

None.
