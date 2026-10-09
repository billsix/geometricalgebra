# Early in the book, show results in coordinates too — not only the coordinate-free statement

**Status:** complete
**Completed:** 2026-10-09 (work committed by the maintainer as `cc2ee40`; archived in its own
commit after the squash)
**Priority:** 5
**Difficulty:** 5
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer's rule (2026-10-08, verbatim): *"Especially early on in the book, proofs via
coordinates are desirable, rather than let's say, stating just that composition of 2D rotations
is commutative. You can absolutely state that and prove that, but also, show the equivalence by
way of coordinates. Obviously, as the book moves towards coordinate free, that should stop."*

So in **Part I** a result is presented twice: the coordinate-free statement (and its proof, where
the book proves it) **and** a coordinate verification the reader can check by hand or in the
companion notebook, tapering off as the book turns coordinate-free. The task wrote that principle
and its taper boundary into `tasks/reference/book-outline.md`, gave every Part I claim that lacked a
coordinate check one (prose, notebook, or both), added the two Lean theorems that state "2D
rotations commute" so the book can cite them by name, and — on a mid-task request — typed every
binding in the book's notebooks and made that a gated rule. `make docs` and `make lean` passed.

## Context (still true of the repo)

- **The rule sharpens an existing principle.** `book-outline.md` › "Coordinate-free is the
  destination; coordinates are scaffolding" already routed coordinate calculations to notebooks;
  the addition is that a coordinate-free *statement* alone is not enough early on, and the taper
  point is a decision rather than drift. Its sub-bullets now carry the rule, the boundary (through
  §D–F; dropped from `blade-square-sign`/`dual`/`defining-g2` and all of Part II), and the pattern.
- **The library-side rule is different and unchanged.** `CLAUDE.md` › "Coordinates only when
  needed" governs Lean statements and Python signatures (objects in, scalars only in the body); it is
  about the API's shape, not what the book shows a student. The two coexist.
- **Where a coordinate check lives:** in the prose when it is a few lines, otherwise in the page's
  companion notebook (sympy, symbolic coordinates, both sides simplified to equal), with the Lean
  theorem cited beside it — the three-forms rule of `CLAUDE.md` › "Every piece of math comes in
  three forms". `notebooks/levels-of-abstraction.py` is the pattern; `proof-rotate-from-a-to-b` and
  `proof-projection` are the proof-page instances.

## Chronology (harvested from the pre-squash quick-save commits, 2026-10-08 → 10-09; all five were squashed into `cc2ee40`, so the hashes below are no longer on a branch)

1. **Filed** (`e6e1643`, 2026-10-08) with "done" = principle in the outline, the four audit items
   below filled, `make docs` green. The audit came from
   `grep -niE "commut|compos|equivalent|the same"` over `book/docs/*.rst`.
2. **Sibling decisions that shaped this task** (`e5e829f`, 2026-10-08): the vector-addition page's
   prose is agent-drafted behind a `.. note:: Draft` banner (not left `TODO`), and the coordinate
   subscript convention (`a_1`/`a_2` instead of `a_x`/`a_y`) stayed a separate, still-proposed task.
3. **The three-forms rule** landed in `CLAUDE.md` (`257b40a`): every math result as Lean + symbolic
   Python + prose/LaTeX by default.
4. **Scope raised** (`bf026eb`, 2026-10-09): the maintainer added "the 2D-rotations-commute claim
   has a named Lean theorem the book cites" to the done-state, and `make lean` to the gates. The
   proofs held the *engine* (`rot_add`; `rotPlane_comp`, whose doc comment *said* "in particular
   rotPlane rotations commute") but no theorem *stated* commutation.
5. **Go-ahead and the work** (`76ac097`, 2026-10-09; now `cc2ee40`), including the mid-task request "all of these
   notebooks should have types just like everything else … and update the reference document, or
   claude.md, to ensure this happens going forward".

## What was done (all in `cc2ee40`)

**The principle.** `book-outline.md`: three sub-bullets under the coordinate-free principle (rule
verbatim, taper boundary, pattern/instances); one line under "Notation & prose conventions for proof
pages" (state → prove → verify in coordinates); the file-layout paragraph names the two proof pages'
companion notebooks and which notebooks have content.

**The four audit items.**

1. *"In 2D, rotations commute"* (`proof-rotate-from-a-to-b.rst` › "The collapse") — was asserted
   and used, never shown. The page now expands `r(r(v; θ₁); θ₂)` by hand with the angle-addition
   identities to `r(v; θ₁ + θ₂)`, which is symmetric in the two angles. A new companion notebook
   `book/docs/notebooks/proof-rotate-from-a-to-b.py` (linked from `rotate.rst`'s toctree) checks
   with symbolic coordinates: commutation in the angle form and in the `(cos, sin)` form, the
   three-turn sandwich collapsing to the single rotation, and that rotation carrying `a` to
   `(|a|/|b|) b` — every `symbolically_equal` is `True`. Lean: `rot_comm` in `Rotation2D.lean`
   (`rot_add` twice and `add_comm`) and `rotPlane_comm` in `RotateFromTo2D.lean` (`rotPlane_comp`
   twice and two `ring`-proved scalar rewrites; no unit constraint, any `v`) — house style, objects
   in, no `IsVector` needed since both sides read only `c1`/`c2`. `rotPlane_comp`'s and
   `rotPlane_conj_collapse`'s doc comments and the module header point at `rotPlane_comm`; the page
   cites both theorems; `lean-ga-proof-architecture.md` (inventory) and
   `reduction-to-standard-position.md` list them.
2. *"Either order lands on the same corner, so addition commutes"* (`vector-addition.rst`, the
   `add3` figure) — the `TODO` became a Draft-bannered paragraph with the one-line coordinate check;
   `notebooks/vector-addition.py` replaced its `1 + 1` stub with `a + b == b + a` and the two
   subtraction identities. `tasks/vector-addition-translate-partial-binding.md` records what landed
   so its translate section adds to the page rather than redrafting it.
3. *The full-angle rotor* (`geometric-product.rst`) — the page now multiplies
   `a (cos θ + sin θ e₁₂)` out component by component and matches `proof-rotate`'s formula, citing
   `vec_mul_fullAngleRotor`, and points the `e₁e₁₂ = e₂`, `e₂e₁₂ = −e₁` steps at `defining-g2`.
   **Finding:** the notebook's markdown promised a comparison with the coordinate formula but had
   no such cell; added (`full_angle_result == coordinate_formula` → `True`).
4. *Projection* — the coordinate equivalence was already in `notebooks/proof-projection.py` (fixed
   `b = 3e₁ + 4e₂`, general `a`); a fully symbolic `b` cell was added and sympy still simplifies the
   difference to `[0, 0]`.

**Typed notebooks (the mid-task request).** The six notebooks with content
(`levels-of-abstraction`, `rotate`, `geometric-product`, `proof-projection`, `vector-addition`,
`proof-rotate-from-a-to-b`) annotate every binding: `sympy.Symbol` declared above each `symbols`
unpack, `Vector`/`Versor`/`Scalar`/`Bivector`/`Real`/`MultiVectorBase` on values,
`Callable[[Real], InvertibleFunction[Vector]]` on the rotation factory, every `def` signature. The
other ten are `1 + 1` placeholders. Types came from `ty`'s `reveal_type` on annotated inputs — sympy
is untyped, so a `symbols` result is `Any` and the declared type carries the meaning. The rule is in
`CLAUDE.md` › "Coding standard (Python)" and `book-and-docs-pipeline.md`; enforcement is
`ty check book/docs/notebooks` in `entrypoint/format.sh` and `book/docs/notebooks` in
`tools/check_annotations.py`'s scope (verified by planting a one-line untyped file — reported as
`LOCAL`, then removed; the real notebooks report 0 rows).

**Decisions and non-changes.** New prose and notebooks use `a_x`/`a_y` to match the pages they sit
in (the subscript task will convert them with everything else). Book notebooks carry no license
header, matching the existing ones. No `CHANGELOG` entry: a book change plus two Lean corollaries,
nothing a consumer pins.

**Gates.** `make lean` (`make -o image lean`, no image rebuild): `[lean] OK`, the two edited modules
rebuilt without warnings, no `sorry`/`admit`. `make docs` (`make -o image docs`): exit 0 twice, before
and after the typing sweep; every notebook executed; the new notebook page renders and the proof page
cites `rotPlane_comm`. Locally: `ruff check .` and `ruff format --check .` clean,
`ty check book/docs/notebooks` and `ty check tools` pass.

## Found, not fixed

The annotation auditor's whole-tree total is 47 rows, not the 24 documented in
`tasks/reference/type-annotation-exemptions.md`: none are from the book notebooks. The drift is
recorded in that doc's "Current state" and the re-baseline is scaffolded as
`tasks/re-baseline-annotation-auditor.md` (proposed — needs go-ahead).

## Open questions

None.
