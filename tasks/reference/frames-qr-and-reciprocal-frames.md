# Frames, the QR decomposition, and reciprocal frames

**Reference document.** This explains what the QR decomposition is, why orthonormalizing a frame and
recording its coefficients *is* QR, how that gives an inverse without row reduction, and how it relates to
Hestenes' reciprocal frame and to the SVD, and why gacalc's implementation stores the frame orthogonal
rather than orthonormal. gacalc implements it as `gacalc.frame.Frame` (`src/gacalc/frame.py`, tests in
`tests/test_frame_class.py`); the build record is `tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md`.
The reciprocal frame's build record is `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`. Open follow-ups: `tasks/frame-svd-investigation.md` and
`tasks/frame-inverse-head-first-recursion.md` (whether the peel can run first-element-first). The
book notebooks (`book/docs/frames-qr.rst`) are recorded in
`tasks/archive/2026/11/04/frame-notebooks-epix.md`. Created 2026-11-04 (William Emerison Six
<billsix@gmail.com>). Update in place.

## L0 — the capsule

Take a frame `v_1 … v_k` (linearly independent vectors). Gram–Schmidt orthonormalize it to `u_1 … u_k`,
and write each original vector in the new basis: `v_i = Σ_j c_ij u_j` with `c_ij = u_j · v_i`. Ordinary
linear algebra calls this pair the **QR decomposition** `V = Q R`. Q is the orthonormal vectors as
columns. R is the coefficients, and it is **upper triangular**: `v_i` needs only `u_1 … u_i`. To invert
the map `x ↦ Σ x_i v_i`, dot the output with each `u_j`, then undo the triangle from the last coordinate
backwards. That is the standard numerical way to solve linear systems and least-squares problems. GA adds
a geometric reading of every piece. gacalc's `Frame` keeps the original vectors and the orthogonal
`w_j`, and computes the coefficients `(w_j · v_i) / |w_j|²` on demand: the same decomposition with the
lengths factored out, so symbolic results stay free of square roots; see "Why gacalc's `Frame` is stored
orthogonal, not orthonormal".

## What "QR" means, plainly

The name is just the two factors. **Q** is an orthogonal matrix: columns of unit length, mutually
perpendicular, so `QᵀQ = I` and Q is a rotation, possibly composed with one reflection. **R** is
upper-**r**ight triangular. Any matrix V with independent columns factors as `V = Q R`, with a positive
diagonal in R.

The everyday way to compute it is Gram–Schmidt on the columns of V, from left to right:

- `w_1 = v_1`, `w_i = v_i` with `span(v_1 … v_{i-1})` rejected out. In gacalc this is `make_orthogonal_frame`
  in `src/gacalc/frame.py`.
- `u_i = w_i / |w_i|` gives the columns of Q.
- `c_ij = u_j · v_i` gives the entries of R. Write it as `R[j][i]` if you want the matrix layout:
  row = orthonormal index j, column = original index i.

Why triangular: `v_i` lies in `span(u_1 … u_i)` by construction, so its components on `u_{i+1}, …` are
zero.

Linear algebra courses often name QR without showing the geometry, because they introduce it as a matrix
factorization for numerics, usually alongside least squares. Inverses in those courses go through row
reduction (RREF / Gauss–Jordan) instead.

## The geometric meaning of the coefficients

- **Diagonal:** `c_ii = u_i · v_i = |w_i|`, the length of the part of `v_i` perpendicular to the earlier
  vectors. This is the "height" `v_i` adds.
- **Volume:** with Hestenes' prefix blades `A_i = v_1 ∧ … ∧ v_i` (H&S eq 3.1; gacalc `prefix_blades`),
  `A_i = A_{i-1} * w_i` (the wedge with a vector orthogonal to the blade is the geometric product), so
  `|A_i| = |A_{i-1}| * |w_i|`. Therefore **`c_ii = |A_i| / |A_{i-1}|`**: the ratio of successive span
  volumes (length, then area, then volume). The product of the diagonal is the frame's full volume,
  `c_11 * c_22 * … * c_kk = |v_1 ∧ … ∧ v_k|`, which is `|det V|` when `k = n`. Gram–Schmidt therefore
  computes the determinant as base times height times height….
- **Off-diagonal:** `c_ji` for `j < i` is the length of `v_i`'s shadow on the earlier direction `u_j`.
  These are the "lean" or shear of the frame.
- **The map factors as Q ∘ R:** R maps the standard basis `e_i` to the coefficient vectors, a
  shear-and-scale that keeps `e_1`'s line and then `span(e_1, e_2)`, and so on. Q then rotates (or
  reflects) `e_j` onto `u_j`. In GA, Q is a **versor**: a rotor when `det Q = +1`, otherwise a rotor times
  a reflection.

## Inverting without row reduction

The forward map `f(x) = Σ (x · e_i) v_i` (send `e_i ↦ v_i`) is multiplication by V. Given `y = f(x)`:

1. **Dot with the orthonormal set.** `u_j · y = Σ_i c_ij x_i`. This step is `Qᵀ y`, and it is trivial
   only because the `u_j` are orthonormal. With an oblique set, dot products mix every coordinate, and
   you would need the inverse Gram matrix.
2. **Undo the triangle by back-substitution**, last coordinate first:
   `x_k = (u_k · y) / c_kk`, then `x_{k-1} = (u_{k-1} · y − c_{k-1,k} * x_k) / c_{k-1,k-1}`, and so on.

Together these give `x = R⁻¹ Qᵀ y`. Step 1 on its own gives y's coordinates in the u-basis, not x.
Step 2 is still needed, but it costs only a few multiplications and divisions per coordinate and is exact.

If `y` is not in `span(v)` (only possible when `k < n`), the same two steps return the **least-squares**
x, the x whose `f(x)` is the projection of y onto the span. This is why QR is the standard least-squares
solver.

**gacalc's form** needs no coefficient table: `Frame.to_invertible_function()` peels the frame from its
last vector. It computes the same coordinates as the two steps above; the next section walks through it.

## The peel inverse, step by step

`Frame.to_invertible_function()` (`src/gacalc/frame.py`) inverts `f(x) = Σ_i x_i * v_i` with a `match`
recursion over the pairs `(w_i, v_i)`: `case []` returns no coordinates, `case [*earlier, (w, v)]` solves
the last one and recurses on `earlier`.

**One step.** Let `y = Σ_{i ≤ k} x_i * v_i`, and let `(w_k, v_k)` be the last pair.

1. **Read the last coordinate.** `w_k` is `v_k` with `span(v_1 … v_{k-1})` rejected out of it, so it is
   perpendicular to every earlier frame vector. Dotting `y` with it kills every earlier term:
   `w_k · y = x_k * (w_k · v_k)`. And `w_k · v_k = |w_k|²`, since `v_k` is `w_k` plus a part lying in the
   earlier span, which `w_k` is perpendicular to. So `x_k = (w_k · y) / |w_k|²`. Geometrically,
   `(w_k · y) / |w_k|²` is the length of `y`'s shadow on the `w_k` direction, measured in units of
   `|w_k|`: how far `y` sticks out of the plane (or line) of the earlier vectors, divided by how far
   `v_k` does.
2. **Remove that vector's contribution.** `y − x_k * v_k = Σ_{i < k} x_i * v_i`, which lies in
   `span(v_1 … v_{k-1})`. Geometrically, `y` slides along `v_k` until it lands in the earlier span.
3. **Repeat on the smaller frame.** For `v_1 … v_{k-1}`, the last orthogonal vector `w_{k-1}` is
   perpendicular to `v_1 … v_{k-2}`, so step 1 applies again. After `k` steps the remainder is the zero
   vector and every coordinate has been read.

**Worked example in 2D.** Frame `v_1 = 2 * e_1`, `v_2 = 1 * e_1 + 3 * e_2`; orthogonal set
`w_1 = 2 * e_1`, `w_2 = 3 * e_2`; `y = 3 * e_1 + 3 * e_2`.

- `x_2 = (w_2 · y) / |w_2|² = 9 / 9 = 1`: `y` is 3 units above the `e_1` line, and so is `v_2`.
- Remainder: `y − 1 * v_2 = 2 * e_1`. `y` slid down along `v_2` onto the line of `v_1`.
- `x_1 = (w_1 · 2 * e_1) / |w_1|² = 4 / 4 = 1`.
- So `x = 1 * e_1 + 1 * e_2`, and indeed `f(x) = 1 * v_1 + 1 * v_2 = y`.

**In 3D** the first step measures `y`'s height above the plane of `v_1, v_2` (along `w_3`), slides `y`
along `v_3` down into that plane, and the rest is the 2D example.

**Why the order is last-first.** The peel needs, at each step, a direction perpendicular to every frame
vector except the one being solved. Orthogonalizing in frame order (as `make_orthogonal_frame` and
Hestenes' prefix blades `A_k = v_1 ∧ … ∧ v_k` do) gives exactly one such direction, the last `w_k`. The
first vector's `w_1` is `v_1` itself, which is not perpendicular to the others, so `w_1 · y` mixes every
coordinate. Two head-first alternatives were considered and rejected (William Emerison Six
<billsix@gmail.com>, 2026-11-04):

- **Matching `[head, *tail]` on the reversed pairs.** This only rearranges the same last-first
  computation; it adds two reversals and changes no mathematics.
- **Solving `x_1` first.** Orthogonalize the reversed frame (`v_k` first) and reverse the result, so that
  `v_1`'s orthogonal vector is perpendicular to `v_2 … v_k`. A prototype recovered symbolic inputs
  exactly, but the stored set would no longer follow the frame order (breaking the `w_1 = v_1`
  convention, the below-diagonal zeros of `coefficients()`, and the prefix-blade volume relation), or
  `Frame` would need a second symbolic orthogonalization. It is the same QR solve applied to the reversed
  frame, so nothing is gained mathematically.

The order-free version is the reciprocal frame: `x_i = vⁱ · y`, each coordinate one dot product (below,
and `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`).

## Why gacalc's `Frame` is stored orthogonal, not orthonormal

`Frame` (`src/gacalc/frame.py`) stores the original `vectors` and their **orthogonal** set `w_j`.
`Frame.coefficients()` computes `coefficients()[i][j] = (w_j · v_i) / |w_j|²`, so
`v_i = Σ_j coefficients()[i][j] * w_j`, and `Frame.orthonormal_vectors()` computes
`u_j = w_j / |w_j|`. Indexed as `coefficients()[original i][orthogonal j]`, the table is zero above its
diagonal and one on it (R transposed, rescaled). This is the same QR decomposition with the lengths
moved out of Q: R's entries are `coefficients()[i][j] * |w_j|`.

The coefficients were stored in `Frame`'s first version, and `__iter__` rebuilt the originals from them.
Once the inverse became the peel recursion (above), nothing read them, so `Frame` stores the originals
instead and computes the coefficients on demand (William Emerison Six <billsix@gmail.com>, 2026-11-04).

**What was tried first, and why it failed (2026-11-04).** The first design followed the original
request: normalize in `__post_init__`, store `u_j`, and use `c_ij = u_j · v_i`. A prototype on fully
symbolic frames (every component its own symbol) gave:

- **2D:** about 1 s. Fine.
- **3D on `Gn`** (simplifies eagerly): rejection took 9 s, and `|w_3|²` was already a 121-operation
  expression. `normalize()` then puts a `sqrt` of each `|w_j|²` into every coefficient, and the
  rebuild check `Σ c_ij u_j == v_i` did not finish within 10 minutes.
- **3D on the generated `g3.Vector`** (simplifies lazily): building took 0.08 s, but deciding the
  `==` did not finish within 5 minutes, with either `sympy.simplify` (what `==` uses) or `sympy.cancel`.

The cause is the square roots. Symbols are not declared positive, so `sqrt(s)` of a large polynomial
`s` does not combine with other radicals in the expression, and sympy's equality check has to search
through a nest of radicals.

**What was done instead (the maintainer's suggestion, 2026-11-04).** Keep the orthogonal `w_j`, and
divide by `|w_j|²` where the orthonormal design would rely on unit length. The `w_j`, the coefficients,
and every step of the inverse are then **rational functions** of the inputs, which sympy can decide
exactly. The prototype measured below inverted by the coefficient back-substitution (dot `y` with each
`w_j`, divide by `|w_j|²`, back-substitute); the shipped inverse is the peel recursion described under
"Inverting without row reduction", which computes the same coordinates. Measured on a fully symbolic 3D
frame:

| configuration | build | rebuild + both round trips |
|---|---|---|
| orthonormal, `Gn` | 9 s orthogonalization, then normalization never finished | did not finish |
| orthogonal, `g3.Vector` (lazy) | 0.08 s | `cancel` check did not finish in 280 s |
| **orthogonal, `Gn`, rejection** (chosen) | 79 s | passes; 151 s total |
| orthogonal, `Gn`, Hestenes `inverse(A_{k-1}) * A_k` | 60 s | passes; 103 s total |
| orthogonal, `Gn`, Hestenes `reverse(A_{k-1}) * A_k` | 15 s | round trip did not finish in 240 s |

The test suite (`tests/test_frame_class.py`) builds the 3D symbolic frame once per module, shares one
`coefficients()` computation per frame (about 68 s for the 3D one) through module-scoped fixtures, and
runs in about 3.5 minutes. With the peel inverse, the 3D symbolic round-trip test takes about 60 s,
against about 50 s for the coefficient back-substitution. The maintainer prefers correctness to runtime (2026-11-04), so the fully symbolic 3D
tests stay in the default suite rather than being replaced by numeric spot checks.

**Why rejection rather than a Hestenes closed form.** Both Hestenes forms rest on `prefix_blades`,
which seeds `A_0` with `type(v).one()`. For the graded `g2`/`g3` `Vector` types that value is the
**zero vector** (a Vector type cannot hold a scalar), so both forms return zeros on graded input. That
is tracked in `tasks/frame-prefix-blades-graded-zero-seed.md`. Rejection (`make_orthogonal_frame`)
works on every representation, and it is the orthogonalization the maintainer wrote. The `inverse`
variant was slightly faster on `Gn`, but not enough to give that up.

## The relation to Hestenes' reciprocal frame

**The problem it solves.** In the standard basis a coordinate is a dot product, `x_1 = x · e_1`, but only
because the `e_i` are orthonormal. In an **oblique** frame, say `v_1 = 2 * e_1` and
`v_2 = 1 * e_1 + 3 * e_2`, with `y = x_1 * v_1 + x_2 * v_2`, dotting with a frame vector mixes the
coordinates: `y · v_1 = x_1 * (v_1 · v_1) + x_2 * (v_2 · v_1)`.

**The fix.** The reciprocal frame `v¹ … vⁿ` is defined by Hestenes & Sobczyk's **eq (3.5)**,
`vⁱ · v_j = δⁱ_j` (the Kronecker delta: 1 when `i = j`, 0 otherwise). Each `vⁱ` is perpendicular to every
frame vector except `v_i`, and its projection on `v_i` is 1. So coordinates are dot products again, one
per coordinate, with nothing to solve: `y = Σ_i (vⁱ · y) * v_i`. The upper index names the reciprocal;
it is not an exponent. In the example, `v¹ = 1/2 * e_1 − 1/6 * e_2` and `v² = 1/3 * e_2`.

**The 2D picture.** `v¹` must be perpendicular to `v_2`, so it lies along `v_2` turned 90°, with its length
set so its shadow on `v_1` is 1. A long, thin parallelogram (frame vectors nearly parallel) therefore gives
long reciprocal vectors: **`|vⁱ|` is 1 divided by the height of `v_i` above the span of the other frame
vectors.** Why a dot product with that vector gives the coordinate, as proportional right triangles, is
"Why one dot product reads off an oblique coordinate: similar right triangles" below.

**The formula, H&S p. 28.** In the book's notation (frame `a_1 … a_n`):

```
A_n = a_1 ∧ a_2 ∧ … ∧ a_n                                (eq 3.6)
a^k = (−1)^(k−1) (a_1 ∧ … ∧ ǎ_k ∧ … ∧ a_n) A_n⁻¹          (eq 3.7)
```

`ǎ_k` means "leave `a_k` out", and the product with `A_n⁻¹` is the geometric product. Read it in three
pieces:

1. The wedge of the others is the **face** of the parallelotope opposite `a_k`.
2. Multiplying by `A_n⁻¹` takes the face's dual inside the frame's space. That is a vector perpendicular to
   the face, so perpendicular to every `a_j` with `j ≠ k`, and dividing by the volume sets its length to
   face / volume = 1 / height.
3. `(−1)^(k−1)` fixes the orientation, so that `a^k · a_k` is `+1` rather than `−1`.

The face lies inside the space of `A_n`, so the geometric product is a pure vector, and it equals the
inner product with `A_n⁻¹`.

**In gacalc** (2026-11-07): `gacalc.frame.reciprocal_frame(vectors) -> list`, with `result[k - 1] = a^k`,
and `Frame.reciprocal_vectors()`. It is built literally from eq 3.7, with `enumerate(start=1)` so the loop
variable is the book's `k`, and the face is `all_wedged_except_the_kth(vectors, k)` (slice out `a_k`, fold
the rest with `functools.reduce(operator.xor, …)`). `itertools.combinations(vectors, n - 1)` was rejected:
it emits the faces in lexicographic order, which leaves out the *last* vector first, so pairing them with
`a_k` would rest on an unobvious emission order. `tests/test_frame.py` checks, on general symbolic 2D and
3D frames:

- eq 3.5 as the identity matrix `[a^k · a_j]`;
- that each `a^k` has grade 1 only;
- the reconstruction `y = Σ (a^k · y) * a_k`;
- `a^n = w_n / |w_n|²`.

**Both inverses, chosen by keyword** (2026-11-07, `tasks/archive/2026/11/07/frame-to-invertible-function-reciprocal-inverse.md`).
`Frame.to_invertible_function(*, inverse_method=...)` takes `"reciprocal"` (the default) or `"peel"`.

- **Reciprocal:** computes the reciprocal vectors once, when the map is built, and its inverse is a plain
  map, `x = Σ_i (vⁱ · y) * e_i`.
- **Peel:** the back-substitution above.

They agree because `vⁱ · y = Σ_j x_j (vⁱ · v_j) = x_i` (eq 3.5), and a frame's coordinates are unique.
`tests/test_frame_class.py` runs every round trip under both methods and checks that the two inverses are
equal on a general symbolic vector, for general 2D and 3D frames.

QR connects to it directly:

- **The last reciprocal vector is the last rejection:** `vᵏ = w_k / |w_k|² = u_k / c_kk`. The reason:
  `w_k` is orthogonal to `v_1 … v_{k-1}`, and `w_k · v_k = |w_k|²`. Back-substitution's first step,
  `x_k = (u_k · y)/c_kk`, is exactly `vᵏ · y`.
- More generally, the reciprocal frame is the columns of `V⁻ᵀ = Q R⁻ᵀ`. Back-substitution builds the
  reciprocal frame one vector at a time, from the end backwards.
- A corollary: orthogonalizing with `v_i` placed **last** yields `vⁱ` directly as `w/|w|²`.

## Why one dot product reads off an oblique coordinate: similar right triangles

The maintainer asked for this section (William Emerison Six <billsix@gmail.com>, 2026-11-07). It explains
why `x_i = vⁱ · y` works, which is what `Frame.to_invertible_function(inverse_method="reciprocal")` and
`reciprocal_frame` in `src/gacalc/frame.py` rely on. The argument is proportional right triangles. The
one thing to get right is **which** right angle.

**Setup.** Take a frame `v_1 … v_n` and `y = x_1 * v_1 + … + x_n * v_n`. Fix one coordinate `x_i`. Call
`H_i` the span of every frame vector except `v_i`: the face of the parallelotope opposite `v_i` (a line in
2D, a plane in 3D). Let `n̂` be a unit vector perpendicular to `H_i`.

**1. Orthonormal frame.** Drop a perpendicular from the tip of `y` to the line of `e_i`. The leg along
`e_i` has length `e_i · y`, and that is the coordinate. This is the familiar right triangle with `y` as the
hypotenuse.

**2. Orthogonal frame, not unit length.** The same triangle, against the line of `v_i`. The shadow of
`y` on that line is `(v_i · y) / |v_i|` long. `v_i`'s shadow on its own line is `|v_i|`. The coordinate
is the ratio of the two shadows, `x_i = (v_i · y) / |v_i|²`. This is already a proportional-triangles
argument: `x_i * v_i` is `v_i` scaled by `x_i`, so every length in its triangle is scaled by `x_i` too.

**3. Oblique frame: the right angle is against the face, not against `v_i`.** Dotting with `v_i` stops
working, because the other frame vectors are no longer perpendicular to `v_i` and their shadows leak in
(`y · v_1 = x_1 * (v_1 · v_1) + x_2 * (v_2 · v_1)` in the example below). Measure **heights above
the face `H_i`** instead, along `n̂`:

- Every term `x_j * v_j` with `j ≠ i` lies inside `H_i`, so it adds no height. The height of `y` is
  the height of `x_i * v_i` alone: `n̂ · y = x_i * (n̂ · v_i)`.
- Draw two right triangles, each with its right angle on the face `H_i`. One has `v_i` as its
  hypotenuse, with leg `n̂ · v_i` (the height of `v_i`). The other has `x_i * v_i` as its hypotenuse, with
  leg `n̂ · y` (the height of `y`). The two hypotenuses lie on one line, so the angle between hypotenuse
  and normal is the same in both triangles. The triangles are therefore similar, with ratio `x_i`.
- So `x_i = (n̂ · y) / (n̂ · v_i)`: **the height of `y` above the face, divided by the height of `v_i`
  above the face.**

Case 2 is the special case where the face is perpendicular to `v_i`, so `n̂` points along `v_i`. The
maintainer's intuition, "right triangles are proportional", is correct. In an oblique frame, though, the
triangles stand on the face of the other vectors, not on `v_i`'s own line.

**4. Fold the division into the vector.** Set `vⁱ = n̂ / (n̂ · v_i)`, the unit normal divided by the height
of `v_i`. Then `vⁱ · y = (n̂ · y) / (n̂ · v_i) = x_i`, a single dot product. The same construction gives
`vⁱ · v_i = 1`, and `vⁱ · v_j = 0` for `j ≠ i` (because `v_j` lies in the face). That is eq 3.5,
`vⁱ · v_j = δⁱ_j`. The length `|vⁱ| = 1 / (n̂ · v_i)` is one divided by the height, the "long, thin
parallelogram gives long reciprocal vectors" fact in "The relation to Hestenes' reciprocal frame".

**5. Where eq 3.7 does each step.** In `a^k = (−1)^(k−1) (a_1 ∧ … ∧ ǎ_k ∧ … ∧ a_n) A_n⁻¹`, the wedge of
the others is the face `H_k` as a blade. Its dual (the product with the pseudoscalar) is the normal
direction `n̂`, so no explicit perpendicular has to be found. Its length divided by `|A_n|` is
`face / volume = 1 / height`, because a parallelotope's volume is its face times its height. The sign makes
the height positive. So eq 3.7 builds `n̂ / (n̂ · v_k)` in one product.

**Worked example** (the frame used throughout this doc): `v_1 = 2 * e_1`, `v_2 = 1 * e_1 + 3 * e_2`,
`y = 3 * e_1 + 3 * e_2`, so `x_1 = x_2 = 1`.

- `x_1`: the face `H_1` is the line of `v_2`, and `3 * e_1 − 1 * e_2` is perpendicular to it (take it
  unnormalized, since the length cancels in the ratio). The height of `y` is `9 − 3 = 6`, and the height
  of `v_1` is `6 − 0 = 6`. So `x_1 = 6 / 6 = 1`, and `v¹ = (3 * e_1 − 1 * e_2) / 6 = 1/2 * e_1 − 1/6 * e_2`,
  as eq 3.7 gives.
- `x_2`: the face `H_2` is the line of `v_1`, the `e_1` axis, with normal `e_2`. The height of `y` is 3,
  and the height of `v_2` is 3. So `x_2 = 1` and `v² = 1/3 * e_2`.

**The peel is the same triangle, for the last vector.** For `v_k`, the face is `span(v_1 … v_{k-1})`. Its
unit normal is `w_k / |w_k|`, and the height of `v_k` above it is `|w_k|`. So
`x_k = (w_k · y) / |w_k|²`, which is the peel's step 1 ("The peel inverse, step by step"). The peel finds
one face normal by rejection and then shrinks the frame. The reciprocal frame finds every face normal at
once, so no coordinate waits on another.

## Floating point

Classical Gram–Schmidt loses orthogonality on nearly-dependent frames. Modified Gram–Schmidt and
Householder reflections (themselves versors) are the stable variants. gacalc is mainly used symbolically,
where this does not arise. For floats, small inexactness is accepted (the maintainer, 2026-11-04).

## Does this give the SVD?

Not from a single QR. The SVD `V = U Σ Wᵀ` is rotation ∘ axis scaling ∘ rotation. Its axes are the
eigenvectors of `VᵀV`, which one orthogonalization does not find. Routes that do reach the SVD from
frames:

- **The QR algorithm:** factor `A = QR`, form `RQ`, and repeat. Applied to `VᵀV`, it converges to the
  eigen-decomposition, so the SVD comes as a limit of repeated frame orthonormalizations.
- **Closed form in 2D**, written as rotor ∘ `scale_non_uniform` ∘ rotor. 3D needs a cubic's roots.

These are investigated in `tasks/frame-svd-investigation.md`.

## Sources

- [Stanford EE263, QR factorization](https://web.stanford.edu/class/archive/ee/ee263/ee263.1082/lectures/qr.pdf): Gram–Schmidt = QR, triangular R, least squares
- [QR decomposition](https://kaweah.freedombox.rocks/kiwix/wikipedia_en_all_maxi_2023-10/QRD): solving with QR; Gram–Schmidt stability vs Householder/Givens
- [Singular value decomposition](https://en.wikipedia.org/wiki/Singular_value_decomposition): rotation · scaling · rotation
- [Doran, GA2015 Lecture 4](https://geometry.mrao.cam.ac.uk/wp-content/uploads/2015/10/GA2015_Lecture4.pdf): linear functions in GA (outermorphism); mentions SVD as a representation
- `tasks/define-frame.md`: the H&S p. 27 frame definition and the `c_k = |A_{k-1}|² w_k` equivalence
- `tasks/reference/galgebra-comparison.md`: galgebra's `ReciprocalFrame`
