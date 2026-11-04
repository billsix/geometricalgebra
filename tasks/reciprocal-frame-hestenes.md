# Reciprocal frame, implemented as Hestenes & Sobczyk write it

**Status:** on hold — the maintainer said "hold off on that for now" about open question 1 (William Emerison Six <billsix@gmail.com>, 2026-11-04);
not started.
**Priority:** 8 (on hold)
**Difficulty:** 5
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>)
**Depends on:** `tasks/frame-class-orthonormal-invertible-function.md` (the `Frame` class it attaches to;
that task's inverse should agree with this one, and a test will check that).

## BLUF

Implement the **reciprocal frame** `v¹ … vⁿ` of a frame `v_1 … v_n`: the vectors with
`vⁱ · v_j = δⁱ_j`, i.e. 1 when `i = j` and 0 otherwise. Follow the formula exactly as Hestenes & Sobczyk
(*Clifford Algebra to Geometric Calculus*, ch. 1) give it, with the page and equation cited in the
docstring. The maintainer has not yet worked through this material, so the task includes the explainer
below; turning it into a book page is part of "done". Done = a `reciprocal_frame` function (and/or a
`Frame` method) with symbolic 2D and 3D tests, its agreement with `Frame.to_invertible_function()`'s
inverse checked, and the explainer folded into
`tasks/reference/frames-qr-and-reciprocal-frames.md`.

## Context (read first)

- `tasks/reference/frames-qr-and-reciprocal-frames.md`, section "The relation to Hestenes' reciprocal
  frame".
- `src/gacalc/frame.py`: `prefix_blades` (H&S eq 3.1). Its docstring already names the reciprocal frame
  as a natural next consumer.
- `tasks/reference/galgebra-comparison.md`: galgebra's `ReciprocalFrame(basis, mode='norm'|'append')`,
  a design reference only, not code to lift.
- `tasks/reference/contraction-and-dot-definitions.md`: gacalc's `inner_product` (Hestenes' dot) versus
  the contractions. The H&S formula uses Hestenes' inner product, so use the one the book uses.

## Explainer: what a reciprocal frame is and why you want it

**The problem it solves.** In the standard basis, a vector's coordinate is a dot product:
`x_1 = x · e_1`. That works only because the `e_i` are orthonormal. Take an **oblique** frame instead,
say `v_1 = 2 * e_1` and `v_2 = 1 * e_1 + 3 * e_2`, and write `y = x_1 * v_1 + x_2 * v_2`. Then
`y · v_1 = x_1 * (v_1 · v_1) + x_2 * (v_2 · v_1)`, which mixes both coordinates, so dotting with the
frame vectors does not read off coordinates.

**The fix.** Find a second set of vectors, the reciprocal frame `v¹, v²`, built so that each `vⁱ` is
**perpendicular to every frame vector except `v_i`**, and its length makes `vⁱ · v_i = 1`. Then
`y · v¹ = x_1 * 1 + x_2 * 0 = x_1`, and coordinates are dot products again, one dot per coordinate,
with no solving:

```
y = Σ_i (vⁱ · y) * v_i
```

The upper index is the convention for the reciprocal; it is not an exponent.

**The 2D picture.** `v¹` must be perpendicular to `v_2`, so it lies along `v_2` turned 90°. Its length
is set so that its shadow on `v_1` has length 1. A long, thin parallelogram (frame vectors nearly
parallel) therefore gives long reciprocal vectors. Geometrically, **`|vⁱ|` is 1 divided by the height
of `v_i` above the line, plane, or hyperplane spanned by the other frame vectors.** In the example:
`v¹ = 1/2 * e_1 − 1/6 * e_2` and `v² = 1/3 * e_2`. Check: `v¹ · v_1 = 1`, `v¹ · v_2 = 1/2 − 1/2 = 0`,
`v² · v_1 = 0`, and `v² · v_2 = 1`.

**The GA formula (shape as in H&S and galgebra; confirm the exact form against the book).** Let
`E = v_1 ∧ v_2 ∧ … ∧ v_n`, the frame's pseudoscalar (its signed volume). Then

```
vⁱ = (−1)^(i−1) * (v_1 ∧ … ∧ v̌_i ∧ … ∧ v_n) · E⁻¹
```

where `v̌_i` means "leave `v_i` out". Read it in three pieces:

1. `v_1 ∧ … v̌_i … ∧ v_n` is the **face** of the parallelotope opposite `v_i`: the (n−1)-blade of all the
   other vectors.
2. Dotting that face with `E⁻¹` takes its **dual** inside the frame's space. The result is a vector
   perpendicular to the face, so it is perpendicular to every `v_j` with `j ≠ i`. Dividing by the volume
   `E` sets the length to face-area / volume = 1 / height.
3. `(−1)^(i−1)` fixes the orientation, so that `vⁱ · v_i` comes out as `+1` rather than `−1`.

A gacalc check on the 2D and 3D example frames above returned the identity matrix for `[vⁱ · v_j]`
(2026-11-04), with gacalc's `inner_product` and `inverse`. The symbolic tests will repeat it in
general.

**Its relation to the `Frame` task (QR).** The last reciprocal vector is the last rejection divided by
its length squared, `vⁿ = w_n / |w_n|²`, because `w_n` is the part of `v_n` perpendicular to all the
others. The `Frame` inverse's back-substitution builds the same coordinates one at a time from the end.
The reciprocal frame gets them all at once, from the pseudoscalar.

**Why it matters later.** A linear map is fixed by where it sends a frame:
`f(x) = Σ (vⁱ · x) * f(v_i)`. That is the doorway to outermorphisms, the adjoint, and
`det = f(I) / I` (see `tasks/define-frame.md`, "Future directions").

## Plan

1. **The maintainer reads H&S** (the frames section, near the p. 27 frame definition) and confirms the
   page, the equation number, and the exact formula, including the sign convention and whether H&S write
   `· E⁻¹` or `E⁻¹ ·` on the left. This decides the code shape (open question 1).
2. Implement `reciprocal_frame(vectors)` in `src/gacalc/frame.py` as a free function, matching the
   module's style, with the H&S page in the docstring. Optionally add a `Frame.reciprocal()` pass-through.
3. Symbolic tests in 2D and 3D:
   - `vⁱ · v_j == δⁱ_j`;
   - the reconstruction `y == Σ (vⁱ · y) * v_i`;
   - `vⁿ == w_n / |w_n|²`;
   - the coordinates agree with `Frame.to_invertible_function()`'s inverse;
   - a non-frame raises `ValueError`.
4. Fold the explainer into `tasks/reference/frames-qr-and-reciprocal-frames.md`, and add a reciprocal
   figure to the frames book notebooks if it isn't there already. Write a `CHANGELOG.md` entry.
5. Per `CLAUDE.md`'s three-forms rule, ask whether this also wants Lean and a book page, or (like the
   `Frame` task) sympy first.

## Open questions (block implementation)

1. **Page, equation, and exact formula in H&S.** Which page and equation define the reciprocal frame,
   and does the book's formula match the shape above (sign `(−1)^(i−1)`, dot with `E⁻¹` on the right)?
   This is yours to read off the book; I won't cite a page I haven't seen. **On hold (William Emerison Six <billsix@gmail.com>, 2026-11-04):
   "hold off on that for now".**
