# Bare-bones 2D book pages: rotation → projection → rotation → product → projection → rotation

**Status:** open — first iteration merged; the maintainer will iterate on it later
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-11-14 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book ends with "Part III — The 2D Bootstrap": six short pages that run the 2D arc end to end,
with minimal prose and every proof shown. Each page has a worked-example notebook, ePiX figures, and its
Lean theorems cited. The first iteration (2026-11-15) is complete, gate-green and merged. The
maintainer is content with it but it is "not exactly what I want". The task stays open for a
later iteration, whose changes the maintainer has not yet named.

## Context

- Pages: `book/docs/bootstrap-rotation.rst`, `bootstrap-projection.rst`,
  `bootstrap-rotation-from-projection.rst`, `bootstrap-product.rst`,
  `bootstrap-projection-from-product.rst`, `bootstrap-rotation-from-product.rst`. They form the
  captioned, numbered toctree "Part III — The 2D Bootstrap" at the end of `book/docs/index.rst`.
- Notebooks: `notebooks/bootstrap-*.py`, same names, jupytext percent format.
- Figures: `book/figures/epix/_bootstrap_scene.py`, `boot_*.py`. Step 2 uses `boot_sp2`–`boot_sp5`.
- Lean: `proofs/GacalcProofs/Bootstrap2D.lean`, plus the existing theorems each page cites.
- The current design rules, and the page → Lean table, are in
  `tasks/reference/reduction-to-standard-position.md` ("The 2D bootstrap in the book"). This doc
  holds the history: what was tried, kept and dropped.
- Gates: `make lean`, `make format`, `make docs`. Look at the PDF pages, not just the build status.
- `CLAUDE.md` rules that apply:
  - the three forms (Lean, symbolic Python, prose + LaTeX);
  - the notation rules (parentheses apply, `*` multiplies, every angle named);
  - `Scalar(s) * e_1`;
  - every binding typed;
  - every ePiX argument by keyword.

## The six steps as they stand

Updated 2026-11-16 after `tasks/archive/2026/11/16/bootstrap-dot-wedge-from-proj-rej.md`,
`quarter-turn-as-named-base-case.md` and `bootstrap-notebooks-show-derivations.md`.

1. **Rotation, from precalculus:** the base case first, the quarter turn
   `r(v; π/2) = (−v₂, v₁)` (`eq-bootstrap-quarter-turn`). Then `r(v; θ) = cos(θ) * v + sin(θ) * r(v; π/2)`
   from the angle-addition identities. It keeps length, angles add, and it is linear.
2. **Projection of `b` onto `a`, from rotation:** the base cases `proj_{e₁}(b) = b₁ * e₁` and
   `rej_{e₁}(b) = b₂ * e₂`, then `proj_a = (R_a^{e₁})⁻¹ ∘ proj_{e₁} ∘ R_a^{e₁}` (and `rej_a` the
   same way). These give `x = (a₁*b₁ + a₂*b₂)/|a|`, `y = (a₁*b₂ − a₂*b₁)/|a|`,
   `proj_a(b) = (a₁*b₁ + a₂*b₂)/(a₁² + a₂²) * a` and
   `rej_a(b) = (a₁*b₂ − a₂*b₁)/(a₁² + a₂²) * r(a; π/2)`.
3. **Rotation from `a` to `b`, from projection, for every `v`:** one right triangle drawn twice.
   - First, `b` measured against `a`: `cos(θ) = x/|b|`, `sin(θ) = y/|b|`.
   - Then the same triangle on `v`: `v' = cos(θ) * v + sin(θ) * r(v; π/2)`.
   - The page also shows:
     - the composition `(R_b^{e₁})⁻¹ ∘ R_a^{e₁}`;
     - that it is a rotation and linear;
     - that only directions matter;
     - `â ↦ b̂`.
4. **The geometric product, from projection:** `a * b = |a| * (x + y * e₁₂)`. It equals the
   product of the multiplication rules and splits as `a · b + a ∧ b`. The page also shows:
   - the quarter turn as a product, `r(v; π/2) = v * e₁₂`;
   - `a · b = a * proj_a(b)` and `a ∧ b = a * rej_a(b)`, stated as results, with the mirrors
     `b * proj_b(a) = a · b` and `b * rej_b(a) = −(a ∧ b)`;
   - `â * b̂ = cos(θ) + sin(θ) * e₁₂`.
5. **Projection through the product:** second versions `proj_a(b) = (b · a) * a⁻¹` and
   `rej_a(b) = (b ∧ a) * a⁻¹`, each shown equal to Step 2's.
6. **Rotation through the product:** the one-sided `v * (â * b̂)` (2D only), then the sandwich
   `R * v * R⁻¹` with `R = b * a + |a| * |b|`, and a proof that the two agree.

Each page's notebook is a worked example: set vectors, every step drawn with live ePiX, and one
check per cell, first on those values and then symbolically (`tasks/reference/book-outline.md`,
"Structural conventions").

## History: what we tried, what we kept, what we dropped

All decisions are William Emerison Six <billsix@gmail.com>, 2026-11-15, unless noted.

### First pass: the six pages

Before starting we settled four questions:
- **Placement:** a top-level part at the end of the book, not a separate document.
- **Projection through the product:** `(a · b) * b⁻¹`.
- **Rotation through the product:** both forms, the one-sided one first.
- **Figures, Lean, granularity:** ePiX rather than matplotlib; cite the existing Lean and add only
  what is missing; one page plus one notebook per step.

We built the six pages and notebooks and six ePiX figures. Step 2 reused Part I's `sp2`–`sp5`. Two
Lean theorems were added for steps that had none: projection through the product and "the
projection-built rotation is `v * (â * b̂)`". Steps 4–6 measured `b` against `a`
(`a * b = |a| * (x + y * e₁₂)`). Lean's `mul_eq_magnitude_smul_alignSP` states the mirror form,
`b * a`.

Problems found and fixed on the way:
- black vectors drawn over the coloured segments along them;
- overlapping labels in three figures;
- `\v` read as an escape when generating text;
- E501 lines in the notebooks;
- `sympy.simplify` on a `Real` union (ty).

### Step 3, second attempt: a map on every vector

The maintainer's review: "the point is supposed to be that you define the rotation of anything in
the plane, where the rotation is the amount it would take to rotate from a to b, regardless of
their length. It's not just rotating vector a itself." The first Step 3 had computed a cosine and
sine from projection and spent its proof on where `a` lands.

We weighed three constructions of the same map:
- **(a)** lay `v`'s projection and rejection lengths on `a` along and across `b`:
  `x * b̂ + y * b̂⊥`;
- **(b)** the composition `(R_b^{e₁})⁻¹ ∘ R_a^{e₁}`;
- **(c)** keep the cosine-and-sine blend and reframe it.

We took (a) as the definition and showed (b) as the same map. Lean gained `rotateFromToProj` with
these theorems:
- `_eq_unalign_align` (the composition);
- `_eq_vec_mul` (`v * (â * b̂)`, a pure `ring` identity);
- `_preserves_dot`;
- `_smul_smul` (only directions matter);
- `_normalize` (`â ↦ b̂`).

The figure showed a third vector `v` with its parts rebuilt along `b`. Step 4 switched to taking its
numbers from Step 2 directly, and Step 6 compared against the new map. A bold span containing math
(`**… :math:`…`**`) rendered raw in the PDF and was fixed.

### Third pass: from `a` to `b` everywhere, and one triangle twice

The maintainer's review of the second attempt had two parts.

**Rotations always go from `a` to `b`.** Step 2 is not a rotation, but its names were backwards
relative to the rest. We flipped Step 2 to project `b` onto `a`, in its math, figures and notebook.
Everything that used it followed:
- Step 3 cites Step 2's coordinates directly;
- Step 4 cites them with no name swap;
- Step 5 became `(b · a) * a⁻¹`;
- Lean `proj_eq_dot_mul_inverse` was restated as `proj a b = (b·a)*a⁻¹`.

Part I's `sp*` figures are shared with `proof-projection.rst` and `product-from-projection.rst`.
Rather than flip them and rewrite Part I, we made Part-III-only copies, `boot_sp2`–`boot_sp5`.

**Step 3's figure.** The second triangle had been built on `b`'s line, and the maintainer's verdict
was: "The second triangle is supposed to show that the rotation is the same idea with the same
triangle. the first triangle shows the rotation and angles from a to b. the second is from v to
v', which is a combination of v and rot 90 v. wtf does b have to do with the second triangle?" So
Step 3 became one right triangle drawn twice:
- `b` measured against `a`, giving `cos(θ)`, `sin(θ)`;
- the same triangle on `v`: `cos(θ) * v` along, `sin(θ) * r(v; π/2)` across, hypotenuse `v'`.

`v` sits outside the angle from `a` to `b`, and `θ` is marked between `a` and `b` and between `v`
and `v'`. This made the two-triangle construction the page's definition. Construction (a),
`x * b̂ + y * b̂⊥`, left the page; it survives only in Lean, where
`rotPlane_fromTo_eq_rotateFromToProj` ties `rotateFromToProj` to the page's definition so all of
its theorems still apply. The composition (b) stayed on the page as the same map.

### What was kept and what was dropped

- **Kept:**
  - all six pages and notebooks;
  - the figures `boot_rotate`, `boot_rotate_from_projection` (two triangles), `boot_product`,
    `boot_project_product` (`a⁻¹`), `boot_rotate_onesided`, `boot_rotate_sandwich`,
    `boot_sp2`–`boot_sp5`;
  - every Lean theorem in `Bootstrap2D.lean`.
- **Dropped:**
  - Step 2's use of Part I's `sp*` figures;
  - the `a`-onto-`b` naming in Steps 2 and 5;
  - Step 3's first form (cosine and sine, then where `a` lands);
  - Step 3's second form (`x * b̂ + y * b̂⊥` as the definition, and its figure). Lean still has it
    as `rotateFromToProj`.
- **Process:** when the maintainer says "update the task", update the existing task. A follow-up
  task was once created instead. The three task records were merged back into this one before the
  squash.

## Verification (first iteration, final state)

- `make lean`: green, no `sorry`/`admit`. The axioms gate passed on 1065 declarations
  (`propext`, `Classical.choice`, `Quot.sound` only).
- `make format`: green (ruff, ty over `book/docs/notebooks`, `check_epix_keywords`, the changelog
  guard).
- Every notebook was run cell by cell, and each zero-check printed zero.
- `make docs`: green.
  - No Part III warnings, and no undefined references in the LaTeX log.
  - No literal `:math:` in the rendered HTML.
  - The remaining Sphinx warnings come from library docstrings and predate this work.
  - The Step 3 and Step 6 PDF pages and the Step 2 figures were checked visually.
- No `CHANGELOG.md` entry: no consumer-facing library change.

## Next iteration

The maintainer will say what to change. When work resumes, read this doc and the reference
section above, rebuild (`make docs`), look at the six pages in the PDF, and ask what to change
before editing.

The maintainer named the first changes on 2026-11-16, done the same day: name the projection and rejection
`proj_a(b)` and `rej_a(b)`, and define the dot and wedge as `a * proj_a(b)` and
`a * rej_a(b)`. That work is recorded in `tasks/archive/2026/11/16/bootstrap-dot-wedge-from-proj-rej.md`.
