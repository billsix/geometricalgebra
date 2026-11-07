# Reciprocal frame, implemented as Hestenes & Sobczyk write it

**Status:** proposed — formula and property confirmed from the book, H&S p. 28 eqs (3.5)-(3.7), no open
questions (William Emerison Six <billsix@gmail.com>, 2026-11-07); not started.
**Priority:** 5
**Blocks:** `tasks/frame-inverse-head-first-recursion.md` (whether the frame map's inverse can run
first-element-first; its option (B) is the reciprocal-frame map). The maintainer put that task on hold
until this one is done (William Emerison Six <billsix@gmail.com>, 2026-11-06).
**Difficulty:** 5
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>)
**Depends on:** `tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md` (the `Frame` class it attaches to;
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

## The formula, as H&S write it (read off the book by the maintainer, 2026-11-07)

Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*, **p. 28**, in the book's notation (frame
vectors `a_1 … a_n`; use these names in the code and docstring):

- **eq (3.6):** `A_n = a_1 ∧ a_2 ∧ … ∧ a_n`, the wedge of the `n` frame vectors in order.
- **eq (3.7):** `a^k = (−1)^(k−1) (a_1 ∧ … ∧ ǎ_k ∧ … ∧ a_n) A_n⁻¹`, where `ǎ_k` means "leave `a_k`
  out", and the product with `A_n⁻¹` is written by juxtaposition, i.e. the **geometric product**. Because
  the (n−1)-blade lies inside the space of `A_n`, that geometric product is a pure vector and equals the
  inner product (the explainer below writes it as `· E⁻¹`). A test should assert the result has only a
  grade-1 part, which pins this down instead of assuming it.
- **The reciprocal frame is the set `{a^1, a^2, …, a^n}`.** The maintainer reads this, like the frame
  `{a_1, a_2, …, a_n}`, as a Python **list**: `reciprocal_frame(vectors: Sequence[...]) -> list[...]`,
  with `result[k-1]` being `a^k`.
- **eq (3.5), the defining property:** `a^k · a_j = δ^k_j`, the **Kronecker delta**: `δ^k_j = 1` when
  `j = k`, and `δ^k_j = 0` when `j ≠ k`. Each reciprocal vector has unit projection on its own frame
  vector and is perpendicular to every other one. This is the property the tests cite (maintainer,
  2026-11-07: "that's the only property I was thinking of").

### Implementation shape: pair each `a_k` with "all the others" (researched 2026-11-07)

The Python standard library has no single "leave-one-out" function. Two candidates, both checked:

- **`itertools.combinations(vectors, n - 1)`** does produce every (n−1)-subset with each tuple in input
  order. But it emits them in lexicographic order of positions, so it drops the **last** vector first:
  for `[a1, a2, a3, a4]` it yields `(a1,a2,a3)`, `(a1,a2,a4)`, `(a1,a3,a4)`, `(a2,a3,a4)`, i.e. the k-th
  tuple omits `a_(n+1−k)`. Pairing it with `a_k` therefore needs `reversed(...)`, and correctness would
  rest on a documented-but-unobvious emission order. Rejected for that reason.
- **`enumerate` + slicing (recommended):** `others = vectors[:k-1] + vectors[k:]` for
  `k, a_k in enumerate(vectors, start=1)`. Each face reads as exactly what eq 3.7 says, and `start=1`
  makes the loop variable the book's `k`, so the sign is literally `(−1)^(k−1)` with no off-by-one
  translation. (Verified: for `[a1, a2, a3, a4]` it pairs `a1` with `[a2, a3, a4]`, …, `a4` with
  `[a1, a2, a3]`.)

The two wedges follow the module's existing fold style (`prefix_blades` uses `accumulate(vectors,
operator.xor, initial=type(vectors[0]).one())`):

```python
one = type(vectors[0]).one()
a_n_inverse = functools.reduce(operator.xor, vectors, one).inverse()      # A_n⁻¹, eq 3.6
return [
    (-1) ** (k - 1) * functools.reduce(operator.xor, vectors[: k - 1] + vectors[k:], one) * a_n_inverse
    for k, _ in enumerate(vectors, start=1)                                  # eq 3.7
]
```

(A sketch for the shape only: `inverse()` is `MultiVectorBase.inverse` in `src/gacalc/base.py`. Check
how `Sequence` slices concatenate for the actual argument type, or take `list(vectors)` first. Keep the
`is_frame` check up front so a dependent set raises `ValueError`.)

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

1. ~~The maintainer reads H&S~~ Done 2026-11-07: p. 28, eqs 3.6 and 3.7 (section above).
2. Implement `reciprocal_frame(vectors) -> list` in `src/gacalc/frame.py` as a free function, matching
   the module's style, citing "H&S p. 28, eqs 3.6-3.7" in the docstring, built with the enumerate+slice
   shape above. Optionally add a `Frame.reciprocal()` pass-through.
3. Symbolic tests in 2D and 3D (general symbolic frames, not just the numeric example):
   - **the book's property, H&S p. 28 eq (3.5):** `a^k · a_j == δ^k_j` for every pair, i.e. `1` on
     the diagonal (`j = k`) and `0` off it (`j ≠ k`), checked as an n×n matrix equal to the identity;
   - each `a^k` is a pure vector (grade 1 only), which justifies reading eq 3.7's product as the dot;
   - the reconstruction `y == Σ (vⁱ · y) * v_i`;
   - `vⁿ == w_n / |w_n|²`;
   - the coordinates agree with `Frame.to_invertible_function()`'s inverse;
   - a non-frame raises `ValueError`.
4. Fold the explainer into `tasks/reference/frames-qr-and-reciprocal-frames.md`, and add a reciprocal
   figure to the frames book notebooks if it isn't there already. Write a `CHANGELOG.md` entry.
5. Per `CLAUDE.md`'s three-forms rule, ask whether this also wants Lean and a book page, or (like the
   `Frame` task) sympy first.

## Open questions (block implementation)

1. ~~Page, equation, and exact formula in H&S~~ **Answered (William Emerison Six <billsix@gmail.com>,
   2026-11-07):** p. 28, eq (3.6) `A_n = a_1 ∧ … ∧ a_n`; eq (3.7)
   `a^k = (−1)^(k−1) (a_1 ∧ … ǎ_k … ∧ a_n) A_n⁻¹`; the reciprocal frame `{a^1, …, a^n}` is a list.
2. ~~Which p. 28 property should the tests cite?~~ **Answered (William Emerison Six
   <billsix@gmail.com>, 2026-11-07):** eq (3.5), `a^k · a_j = δ^k_j` (Kronecker delta: 1 if `j = k`,
   0 otherwise), the only property in scope. The other checks in the plan (reconstruction, last
   rejection, agreement with `Frame`'s inverse) are gacalc's own consistency tests and cite no page.
