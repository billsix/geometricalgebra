# Spell out basis blades as products of basis vectors (`e_12` → `1 * e_1 * e_2`)

**Status:** ready — decisions made, waiting for the go-ahead to execute
**Priority:** 5
**Difficulty:** 5
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book and notebooks name the unit plane by a compound index, `\mathbf{e}_{12}` / `e_12`
(and `e_13`, `e_23`, `e_123` in space). For a student, the product `1 * e_1 * e_2` says what
the thing is. Rewrite every occurrence that can be rewritten, in the plane and in space, and
leave the ones that cannot with a reason. The research is done: 278 lines in 40 files, listed
and classified below. Done = each line in the list is converted or is in the explained residue,
and `make format`, `make check-notebooks`, `make test` and `make docs` pass.

## The request (2026-11-22, the maintainer's words)

> since this codebase is for teaching, I think there are many cases where instead of writing say
> e_12, writing 1 * e_1 * e_2 would be more clear for the reader. obviously this can't work for
> all, but may as well do it whenever we can, and for the 3d case. research, find all places in
> the book and notebooks where that is the case, make a list. when I tell you to do the task,
> execute it.

## Context

- Read first: `CLAUDE.md`, "Math notation for readers" (the bullet that says a blade of grade 2
  or more is typeset as one bold `\mathbf{e}_{12}`; this task changes that rule, so the bullet
  is rewritten in the same change) and "Conventions the agent must obey" (unit coefficients are
  written explicitly; a blade used as a *direction* stays bare; no local aliases).
- Scope is what the maintainer named: `book/docs/*.rst`, `book/figures/`, `notebooks/*.py`.
  Not in scope: Python docstrings (`src/gacalc/base.py` has 36 such lines), the generator
  (`tools/gen_specialized.py`, 187), `README.md` (8), Lean comments. They keep `e_12`.
- The two reference cards (`book/docs/cheat-sheet-2d.rst`, `cheat-sheet-3d.rst`, 24 lines each)
  are also being restructured by `tasks/cheat-sheet-gn-section-and-explicit-names.md`. Whichever
  task runs second writes the cards in the form this task settles.
- The worklog is `tasks/adhoc/spell-out-basis-blades-as-vector-products/data/matches.txt`,
  written by `discover.sh` beside it. Line numbers below are from 2026-11-22; fix by content.

## Findings that limit the rewrite

1. **gacalc prints `\mathbf{e}_{12}`.** Every computed cell shows the compound name
   (`blade_latex` in `src/gacalc/base.py`), and the class fields are `coeff_e_12`. The reader
   therefore still has to learn the name once. The pages that introduce it keep it (class N
   below); changing what gacalc prints is a library change and is not part of this task.
2. **In the graded modules the product has a different type from the constant.** Measured in
   the sandbox, 2026-11-22:

   | expression | value | runtime type |
   |---|---|---|
   | `g2.e_12`, `2 * g2.e_12`, `g2.e_1 ^ g2.e_2` | the unit plane | `Bivector` |
   | `1 * g2.e_1 * g2.e_2` | equal to `g2.e_12` under `==` | `Versor` |
   | `g3.e_1 * g3.e_2` | equal to `g3.e_12` | `Versor` |
   | `1 * g3.e_1 * g3.e_2 * g3.e_3` | equal to `g3.e_123` | `Odd` |
   | `g3.e_1 ^ g3.e_2 ^ g3.e_3` | the unit volume | `Trivector` |
   | `(1 * g2.e_1 * g2.e_2).inverse()` | | `Versor` |

   So `B: Bivector = 2 * e_1 * e_2` fails `ty`, as does `I_inverse: Bivector = …`. A vector
   times the product is still a `Vector` at runtime, and `a.projected_onto(1 * e_1 * e_2)`
   returns the right vector. In the full-class notebooks (`G`) and the `Gn` notebook the type is
   the same either way. Decision 2 leaves those lines on the constant.
3. **A subscript or a plane name gets long.** `proj_{\mathbf{e}_{12}}(v)` and "the
   `\mathbf{e}_{12}` plane" use the blade as a direction, which today's rule leaves bare. Spelled
   out they are `proj_{\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2}(v)` and "the
   `\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` plane". One real gain there: the book's `e_31`
   against gacalc's `e_13 = -e_31` becomes `e_3 * e_1 = -e_1 * e_3`, which needs no footnote.
   Decision 1 keeps the blade there, except for that note.
4. **Longer equations can run past the PDF margin.** `make docs` ends with
   `tools/check_math_overflow.py`; a hand-written `.. math::` block that overflows gets a `\\`.
   Notebook prose is re-wrapped with `python tools/check_notebook_prose_width.py --fix`.

## The rewrite rules

(The classes are this task's own grouping.)

- **S, spell out (typeset math):** a coefficient times the blade, or the bare blade used as a
  value. `y * \mathbf{e}_{12}` → `y * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2`; a bare
  `\mathbf{e}_{12}` → `1 * \vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` (parenthesized where it is
  a factor on the right of something that does not associate visibly, and without the `1` where
  a coefficient is already there); `\mathbf{e}_{123}` → three factors. Several identities then
  show their own reason: `e_1 * e_12 = e_2` becomes `e_1 * e_1 * e_2 = e_2`.
- **N, keep (naming):** a sentence or cell whose subject is the name itself: "call it
  `e_12`", `e_1 * e_2 = e_12` in a list of product rules, `show_difference(e_12, e_1 * e_2)`,
  the list of the four basis blades. Converting one produces `x = x`. Where a product rule list
  has `e_2 * e_1 = -e_12`, it becomes `e_2 * e_1 = -e_1 * e_2`.
- **P, plane name or subscript:** kept as `\mathbf{e}_{12}` (decision 1), except the `e_31`
  note, which is spelled out.
- **C, Python code:** `C-same` where the static type cannot change (a `G` or `Gn` value, or an
  annotation the product still satisfies, such as `MultiVectorBase` or `Versor`); `C-typed`
  where the annotation is `Bivector`/`Trivector` or the value is passed as a plane. `C-typed` lines keep
  the constant (decision 2).
- **X, cannot:** file names (`proj3d-e12.png`), string keys (`plane3(plane="e_12")`), field
  names, and prose that points at gacalc's printed output.

## The list

### Book pages

| file | S | N | P / X |
|---|---|---|---|
| `book/docs/geometric-product.rst` | 30, 34, 37, 40, 41, 48, 49, 56, 66, 71, 107, 111, 119 | 29 ("call it") | |
| `book/docs/bootstrap-product.rst` | 47, 52, 53, 56, 74, 90, 99, 104, 105, 107, 126, 132, 167, 171 | 66, 67 (product rules) | |
| `book/docs/bootstrap-rotation-from-product.rst` | 27, 35, 56, 88, 89, 93, 94, 95, 129 | | |
| `book/docs/bootstrap-projection-from-product.rst` | 75, 76 | | |
| `book/docs/product-from-projection.rst` | 21, 72, 78, 79, 90, 105, 152 | 83 (product rules) | |
| `book/docs/defining-g2.rst` | 31, 45, 75, 78 | 34, 69, 89 (the blade list, the rules, blade ↔ picture) | |
| `book/docs/blade-square-sign.rst` | 19, 87, 252 | 20 (already `e_12 = e_1 * e_2`) | |
| `book/docs/rotation-from-vectors.rst` | 39, 42, 101, 103 | | |
| `book/docs/dual.rst` | 19, 21, 41, 42 | | |
| `book/docs/dual-3d.rst` | 21, 22 (`e_123`) | | |
| `book/docs/projection.rst` | 51 | | |
| `book/docs/projection-rejection-3d.rst` | | | P: 25, 48, 49 (the `e_31` note); X: 6 figure file names |
| `book/docs/proof-cross.rst` | | | P: 35, 47, 59 |
| `book/docs/cheat-sheet-2d.rst` | 35–38, 49–53, 57, 71, 85, 87, 113, 114, 148, 168, 218, 222, 253, 256, 305, 307, 308 | | |
| `book/docs/cheat-sheet-3d.rst` | 35–40, 52, 58–60, 88, 89, 116, 150, 151, 154, 156, 270–272 | 51, 53 (the generic `e_{ij}` rules) | P: 213, 232, 249 ("onto / in `e_12`") |

### Notebooks: Markdown cells and figure labels

| file | S | N | P / X |
|---|---|---|---|
| `notebooks/bootstrap-product.py` | 36, 103, 104, 175, 176, 199 (label), 282, 380 | 160 | |
| `notebooks/bootstrap-projection-from-product.py` | 136 | | |
| `notebooks/bootstrap-rotation-from-product.py` | 103, 113 | | |
| `notebooks/defining-g2.py` | 61, 72, 184, 236, 356, 425 | 92, 170, 383 | P: 436 (label on the unit square) |
| `notebooks/displayg2.py` | 284 | 40, 82, 83 | |
| `notebooks/displayg3.py` | 282 | 39, 40, 86, 87 | |
| `notebooks/displaymv.py` | 127, 238, 655, 747 | 84 ("written `e_12`") | X: 675, 696 (name gacalc's output) |
| `notebooks/displaygraded.py` | | | P: 238 (label); X: 143, 396 |
| `notebooks/displayrotations.py` | | | P: 230 (`P_{e_{23}}` label; its code is already `e_2 ^ e_3`) |
| `notebooks/dual.py` | 28, 80, 81, 151, 152, 254, 255 | | |
| `notebooks/dual-3d.py` | 164 | | |
| `notebooks/geometric-product.py` | 36, 80, 99, 143 (label) | | |
| `notebooks/levels-of-abstraction.py` | 108, 116, 248 | | |
| `notebooks/product-from-projection.py` | 32, 204, 254, 261 | | |
| `notebooks/projection.py` | 173, 184, 196 | | |
| `notebooks/rotation-from-vectors.py` | 94, 102 | | |
| `notebooks/projection-rejection-3d.py` | | | P: 78, 91, 103, 104 |
| `notebooks/proof-cross.py` | | | P: 30, 124, 136, 145, 213, 215, 228, 244 |
| `notebooks/proof-projection-3d.py` | | | P: 112, 127, 137 |
| `notebooks/reflection-3d.py` | | | P: 211 |
| `notebooks/frame-qr-3d.py` | | | P: 72 |

### Notebooks: code

| file | C-same | C-typed | keep |
|---|---|---|---|
| `notebooks/bootstrap-product.py` | 110, 179, 384 | | 59 (import, dropped if unused) |
| `notebooks/defining-g2.py` | 241 (`e_12 * e_12`), 315 (`R: Versor`), 352 | 307 (`B: Bivector = 2 * e_12`) | 54 (import) |
| `notebooks/displayg2.py` | | | 60 (`e_12: G = G.e_12`), 86 (the equality check) |
| `notebooks/displayg3.py` | | | 63–66, 90 (the equality check), 97, 103, 109 (cells that show each blade) |
| `notebooks/displayrotations.py` | | 277 (`i: g2.Bivector = g2.Bivector.e_12`) | |
| `notebooks/dual.py` | 91 | 84 (`I_inverse: Bivector`) | 62 (import) |
| `notebooks/dual-3d.py` | | 150 (`I_inverse: Trivector`) | 58 (import) |
| `notebooks/geometric-product.py` | 94 (`R: Versor`) | 85 (`quarter_turn: Vector = a * Bivector.e_12`; check with `ty`) | |
| `notebooks/levels-of-abstraction.py` | | 183 (`wedge_coordinate: g2.Bivector`) | |
| `notebooks/product-from-projection.py` | 208, 264 | | |
| `notebooks/projection-rejection-3d.py` | | 82, 88, 94, 100, 108, 114 (plane arguments) | 61 (import) |

`displayg2.py` 86 and `displayg3.py` 90 are on the removal list of
`tasks/prune-unneeded-cancellation-checks.md`; if that task runs first they are gone.

`C-same` rows are a prediction from the annotations; `make format` (`ty`) and `make
check-notebooks` (pyright) decide each one. A row that fails moves to `C-typed`.

### Figures (`book/figures/epix/`)

`proj3d_e12.py`, `proj3d_e23.py`, `proj3d_e31.py`, `proj3d_overview.py`: every line is P (the
header comments and the `proj_{e_12}` / `rej_{e_12}` labels) or X (`plane3(plane="e_12")`,
`project_onto(plane="e_12")`, the output file names). `proj3d_e31.py` lines 19–20 carry the
`e_31` / `e_13` note of finding 3.

## Plan

1. Rewrite the `CLAUDE.md` notation bullet first, so the rule and the pages agree: a blade
   of grade 2 or more is written as the product of its basis vectors where it is a value, and
   as one bold `\mathbf{e}_{12}` where it names a plane, is a subscript, or is being introduced.
2. Class S, a file at a time, bottom-up within a file; class N product-rule lists as described.
3. Class `C-same` code; a line that then fails `ty` or pyright goes back to the constant.
4. The `e_31` note: `book/docs/projection-rejection-3d.rst` (48, 49),
   `notebooks/projection-rejection-3d.py` (103, 104), `book/figures/epix/proj3d_e31.py` (19, 20).
5. Gates: `make format`, `make check-notebooks`, `make test`, `make docs` (the overflow check).
6. Re-run `discover.sh`; the remaining matches must each be an N, P, X or `C-typed` row above.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22, each on the agent's recommendation:

1. **A blade used as a plane's name or as a subscript keeps `\mathbf{e}_{12}`** (class P: "the
   `e_12` plane", `proj_{e_12}`, figure labels), as the "a direction stays bare" rule already
   does. The one exception is the `e_31` / `e_13` note, written `e_3 * e_1 = -e_1 * e_3`. Why:
   a product inside a subscript or a label is long and reads worse than the name.
2. **`C-typed` code keeps the `e_12` constant.** Only math, prose and `C-same` code are
   converted. Rejected: `1 * (e_1 ^ e_2)`, which uses the wedge on pages that come before it is
   taught, and retyping `Vector * Vector` in the generator, which is a typing redesign.
3. **"Execute it":** on go-ahead, run the Plan above. (The request's last word was first
   written "iter-empty", a typo for "it".)

## History

All on 2026-11-22 (William Emerison Six <billsix@gmail.com>).

1. Asked for; the book, figures and notebooks were searched and the 278 lines classified. Two
   limits turned up while classifying: gacalc prints `e_12`, and in the graded modules the
   product `1 * e_1 * e_2` is a `Versor`, not a `Bivector`.
2. Three questions went to the maintainer: what "iter-empty" meant (a typo for "it"), whether
   plane names and subscripts are spelled out, and what to do with the typed code lines. The
   answers are the Decisions above; the rules, list and plan were rewritten to match.
3. `displayg2.py` 86 and `displayg3.py` 90 were noted as also on the removal list of
   `tasks/prune-unneeded-cancellation-checks.md`.
