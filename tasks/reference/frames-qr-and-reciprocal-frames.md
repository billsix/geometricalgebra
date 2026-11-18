# Frames, the QR decomposition, and reciprocal frames

**Reference document.** This explains what the QR decomposition is, why orthonormalizing a frame and
recording its coefficients *is* QR, how that gives an inverse without row reduction, and how it relates to
Hestenes' reciprocal frame and to the SVD, and why gacalc's implementation works from the orthogonal
set rather than the orthonormal one. gacalc implements it as `gacalc.frame.Frame` (`src/gacalc/frame.py`, tests in
`tests/test_frame_class.py`); the build record is `tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md`.
The reciprocal frame's build record is `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`. The SVD study and the head-first peel are
`tasks/archive/2026/11/18/frame-svd-investigation.md` and
`tasks/archive/2026/11/18/frame-inverse-head-first-recursion.md`. The
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
a geometric reading of every piece. gacalc's `Frame` keeps the original vectors and computes the
orthogonal `w_j` and the coefficients `(w_j · v_i) / |w_j|²` on demand: the same decomposition with the
lengths factored out, so symbolic results stay free of square roots; see "Why gacalc's `Frame` uses the
orthogonal set, not the orthonormal one".

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

`Frame.to_invertible_function(inverse_method=InverseMethod.PEEL)` (`src/gacalc/frame.py`) inverts `f(x) = Σ_i x_i * v_i` with a `match`
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
coordinate. So the peel is back-substitution against QR's triangular `R`, and its natural recursion is
`[*earlier, last]`.

**A head-first version was tried and reverted (2026-11-18).** The peel was rewritten to match
`[(z, v), *later]` over a second orthogonal set, `z_i`, which was the frame orthogonalized from its last
vector (`reversed(make_orthogonal_frame(vectors[::-1]))`). It returned the same coordinates, but the
maintainer (William Emerison Six <billsix@gmail.com>) judged the code worse, for three reasons:
- the `z_i` exist nowhere else: not in `Frame`, the book's notebooks, this doc's QR story, or the Lean
  model;
- reversing, orthogonalizing and reversing back is the reversal moved into the data, not removed. It is
  the same last-first solve run on the reversed frame;
- it no longer mirrored the Lean `invPeel`, which peels from the last vector.

The tail-first peel over `orthogonal_vectors()` was restored
(`tasks/archive/2026/11/18/frame-peel-order-and-forward-reference.md`). Two other head-first options had
been rejected earlier (William Emerison Six <billsix@gmail.com>, 2026-11-04):
- **matching `[head, *tail]` on the reversed pairs**, which only rearranges the same computation;
- **storing the reversed orthogonalization in `Frame`**, which would break the `w_1 = v_1` convention,
  the below-diagonal zeros of `coefficients()`, and the prefix-blade volume relation.

The order-free version is the reciprocal frame: `x_i = vⁱ · y`, each coordinate one dot product (below,
and `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`).

## Why gacalc's `Frame` uses the orthogonal set, not the orthonormal one

`Frame` (`src/gacalc/frame.py`) stores the original `vectors` (a tuple) and computes their
**orthogonal** set `w_j` on demand (`Frame.orthogonal_vectors()`).
`Frame.coefficients()` computes `coefficients()[i][j] = (w_j · v_i) / |w_j|²`, so
`v_i = Σ_j coefficients()[i][j] * w_j`, and `Frame.orthonormal_vectors()` computes
`u_j = w_j / |w_j|`. Indexed as `coefficients()[original i][orthogonal j]`, the table is zero above its
diagonal and one on it (R transposed, rescaled). This is the same QR decomposition with the lengths
moved out of Q: R's entries are `coefficients()[i][j] * |w_j|`.

The coefficients were stored in `Frame`'s first version, and `__iter__` rebuilt the originals from them.
Once the inverse became the peel recursion (above), nothing read them, so `Frame` stores the originals
instead and computes the coefficients on demand (William Emerison Six <billsix@gmail.com>, 2026-11-04).
The orthogonal set itself was a stored field until 2026-11-09; it is now the method
`orthogonal_vectors()`, spelled like `orthonormal_vectors()` and `reciprocal_vectors()`, and `Frame`
takes its vectors as a tuple (`tasks/archive/2026/11/09/frame-derived-orthogonal-set-and-tuple-field.md`).

The code reads each coefficient as a projection: `coordinate_along(v.projected_onto(w), along=w)`
(`src/gacalc/transforms.py`), "how many copies of `w` the projection of `v` onto `w` is", which raises if
its input is off the line. In coordinates that is `(w · v) / |w|²`; the two are equal. The inverses are
described in "The code form: one line-to-line projection" below. The projection forms are slower on symbolic
`Gn` input, because `Gn` simplifies after each inverse and product; the timings are in that section. The
maintainer prefers the form a student reads over the faster one (CLAUDE.md, "Write the named geometric
operation"; records: `tasks/archive/2026/11/07/name-the-geometric-operation-over-its-formula.md`,
`tasks/archive/2026/11/07/line-to-line-projection-invertible-function.md`).

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

**Why rejection rather than a Hestenes closed form.** When `Frame` was built, both Hestenes forms
returned zeros on the graded `g2`/`g3` types (`prefix_blades` seeded `A_0` with a graded `Vector`'s
`one()`, the zero vector; fixed 2026-11-07, `tasks/archive/2026/11/07/frame-prefix-blades-graded-zero-seed.md`). Rejection (`make_orthogonal_frame`) is the
orthogonalization the maintainer wrote and needs no prefix blades. The `inverse` variant was slightly
faster on `Gn`, but not enough to switch.

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
`Frame.to_invertible_function(*, inverse_method=...)` takes the enum `frame.InverseMethod`: `RECIPROCAL` (the default) or `PEEL`.

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
why `x_i = vⁱ · y` works, which is what `Frame.to_invertible_function(inverse_method=InverseMethod.RECIPROCAL)` and
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

### The code form: one line-to-line projection

Steps 3–4 say: for an `n` perpendicular to every frame vector but `v_i`, `P_n(y) = x_i * P_n(v_i)`. So
`x_i * v_i` is the point on `v_i`'s line whose projection onto `n` is `P_n(y)`. Projection restricted to
the line of `v_i` is a bijection onto the line of `P_n(v_i)` whenever `v_i · n ≠ 0`, so it has an
inverse, and `transforms.line_to_line_projection(from_vector=v_i, to_vector=n)` is that
`InvertibleFunction` (each direction raises `ValueError` on input off its line). Both of
`Frame.to_invertible_function`'s inverses are this one statement:

    x_i * v_i = line_to_line_projection(from_vector=v_i, to_vector=n).inverse(P_n(y))
    x_i       = coordinate_along(x_i * v_i, along=v_i)

with `n = vⁱ` for the reciprocal inverse and `n = w_k` for the peel's last vector (then subtract the term
and recurse). On the worked example, `n = w_2`, `v²` and `v¹` each give `x = 1`; `n = w_1`, which is not
perpendicular to `v_2`, gives `3/2`.

**Cost (measured 2026-11-07, symbolic `Gn`).** The full `pytest` suite took 6:19 with the dot-product
forms, 12:15 once the coefficients were read as projections, and 26:38 with both inverses written as
above. The 3D symbolic tests carry all of it: `test_inverse_methods_are_equivalent_symbolic[3d]` 38 s → 151 s
→ 475 s, `test_composed_round_trip_is_identity_symbolic[3d-peel]` 64 s → 200 s → 415 s, and `[3d-reciprocal]`
under 20 s → 282 s. Each inverse call now runs the on-the-line checks (`is_orthogonal_to`,
`is_parallel_to`) and an extra projection, and `Gn` simplifies after each.

## Hestenes' orthogonalization equals rejection, up to a positive scale

`frame.py` keeps three orthogonalizations side by side for teaching:
- `make_orthogonal_frame`: sequential rejection, the maintainer's Gram–Schmidt;
- `make_orthogonal_frame_hestenes`: H&S p. 27 eq 3.2, `c_k = Ã_{k-1} * A_k`, where
  `A_k = v_1 ∧ … ∧ v_k` and `A_0 = 1` (eq 3.1, `prefix_blades`);
- `make_orthogonal_frame_hestenes_inverse`: the same formula with `A_{k-1}⁻¹` in place of the reverse.

**Theorem.** For a frame `v_1 … v_k`, let `w_1 … w_k` be its rejection orthogonalization: `w_j` is
`v_j` with the span of `v_1 … v_{j-1}` rejected out of it. Then

    A_k = w_1 * w_2 * … * w_k,
    c_k = Ã_{k-1} * A_k = |A_{k-1}|² * w_k,   |A_{k-1}|² = |w_1|² * … * |w_{k-1}|² > 0,
    A_{k-1}⁻¹ * A_k = w_k.

**Proof**, by induction on `k`. For `k = 0`, `A_0 = 1` is the empty product. Assume
`A_{k-1} = w_1 * … * w_{k-1}`.
1. Split `v_k = p + w_k`, where `p` lies in the span of `v_1 … v_{k-1}` (the subspace of `A_{k-1}`)
   and `w_k` is perpendicular to it.
2. Wedging a blade with a vector in its own subspace gives zero, so `A_{k-1} ∧ p = 0`. Then
   `A_k = A_{k-1} ∧ v_k = A_{k-1} ∧ w_k`.
3. The `w_1 … w_k` are mutually perpendicular. For perpendicular vectors the geometric product is the
   wedge (each dot product is zero), so `w_1 * … * w_k = w_1 ∧ … ∧ w_k`. By the hypothesis this is
   `A_{k-1} ∧ w_k`, which step 2 showed is `A_k`.
4. Reversing a product of vectors reverses their order, so
   `Ã_{k-1} * A_{k-1} = w_{k-1} * … * w_1 * w_1 * … * w_{k-1}`. Each `w_j * w_j = |w_j|²` is a
   scalar, so the middle collapses pair by pair to the positive scalar `∏_{j<k} |w_j|² = |A_{k-1}|²`.
5. Hence `c_k = Ã_{k-1} * A_{k-1} * w_k = |A_{k-1}|² * w_k`. Since
   `A_{k-1}⁻¹ = Ã_{k-1} / |A_{k-1}|²`, also `A_{k-1}⁻¹ * A_k = w_k`. ∎

What follows:
- The Hestenes vectors point the same way as the rejection vectors (a positive factor keeps
  direction and sign), and `c_1 = w_1` exactly. After normalization the two frames are identical.
- The inverse form is *exactly* the rejection.
- `|A_k|² = ∏_{j≤k} |w_j|²`: the squared volume of the parallelotope is the product of its squared
  orthogonal heights. This is the GA form of the Gram determinant, and the reason
  `measure.content_by_rejection` agrees with `measure.content`.

The two methods compute differently. Each Hestenes `c_k` comes straight from the original prefix
`v_1 … v_k` (closed form, independent of the other `c_j`), while each `w_k` is built from the
already-orthogonalized `w_1 … w_{k-1}` (sequential). The theorem is the bridge between them.

**Where it is checked.** `tests/test_frame.py`:
- the reverse form is *parallel* to the rejection (`c_k ∥ w_k`, through `is_parallel_to`) in 2D and
  3D, symbolic, concrete and numeric;
- the inverse form *equals* the rejection.

A symbolic cross-construction check must test that `c_k − w_k` (or the scaled difference) is the
zero multivector, not `c_k == w_k`. `Gn.__eq__` is structural, and two constructions of the same
vector give structurally different sympy expressions. Subtraction simplifies to exact zero, `==` does
not. There is no Lean version yet: frames in Lean are `tasks/lean-frame-coverage.md`, which is
parked.

## Design facts about `frame.py` (from `tasks/archive/2026/11/18/define-frame.md`)

- **Frame (H&S p. 27):** a set of vectors whose wedge is nonzero, which means linearly independent,
  not orthogonal. `are_linearly_independent` tests the wedge, and `is_frame` passes through to it.
  - A zero or non-vector member raises `ValueError`: a category error, not "a dependent frame".
  - An empty sequence is not a frame.
- **`make_orthogonal_frame` rejects one earlier vector at a time**, not the span blade. When it was
  written, `reject` handled only grade-1 and grade-2 spans
  (`tasks/generalize-reject-reflect-higher-grade.md`). The earlier `w_j` are mutually perpendicular,
  so the two give the same result.
- **Free functions over `MultiVectorBase`, not generated methods.** The generator compiles closed-form
  arithmetic on single values. These functions are algorithms over a sequence of vectors, built from
  primitives every representation already has, so one implementation serves `Gn`, `g2` and `g3`.
- **The rest of the library already accepts a `Frame`** (the 2026-11-18 sweep):
  - `v.projected_onto(frame.vectors)`, `rejected_away_from` and `reflect` take the vector tuple,
    because they accept a sequence and wedge it;
  - `to_matrix(frame.to_invertible_function(), cls)` gives the frame matrix, since the function is
    `Linearity.LINEAR`;
  - `measure.content_by_rejection` uses `make_orthogonal_frame` on a plain sequence, which is the
    right shape for it.

  No `Frame.standard(n)` was added: `Frame((1 * e_1, 1 * e_2))` already says it, and nothing needs
  one.

## Floating point

Classical Gram–Schmidt loses orthogonality on nearly-dependent frames. Modified Gram–Schmidt and
Householder reflections (themselves versors) are the stable variants. gacalc is mainly used symbolically,
where this does not arise. For floats, small inexactness is accepted (the maintainer, 2026-11-04).

## Does this give the SVD?

Not from a single QR. The SVD `V = U Σ Wᵀ` is rotation ∘ axis scaling ∘ rotation. Its axes are the
eigenvectors of `VᵀV`, which one orthogonalization does not find. Three routes were tried in
`tests/test_frame_svd.py` (2026-11-18), each written with gacalc's own transforms. All three work.

1. **`f = Q ∘ R`, the same rotate-after-deform shape.** Since
   `v_i = Σ_j (coefficients()[i][j] * |w_j|) * u_j`:
   - R sends `e_i` to `Σ_j coefficients()[i][j] * |w_j| * e_j`. That is a triangular frame, so
     `Frame` builds it too.
   - Q sends `e_j` to `u_j`. It is a chain of rotations from vectors: each turns the image of the
     next basis vector onto the next `u_j`, in a plane perpendicular to the `u`'s already placed. A
     left-handed frame adds an axis flip, `scale_non_uniform(1, …, −1)`, run first.

   `compose([*Q, R])` equals `Frame.to_invertible_function()` in 2D and 3D, right- and left-handed.
   This is not the SVD: R shears.
2. **The QR algorithm reaches the SVD numerically.** Take the Gram matrix `M_ij = v_i · v_j`. Factor
   `M = QR` with a `Frame` (Q from `orthonormal_vectors()`, `R_ij = u_i · m_j`), form `RQ`, and
   repeat. `M` converges to `diag(σ_i²)`, and the accumulated `Q` columns are the right singular
   vectors `w_i`. The images `f(w_i)` are then mutually perpendicular with lengths `σ_i`. 200
   iterations on a 3D float frame give the lengths to a relative 1e-9 and perpendicularity to 1e-7. It needs distinct singular values and is linear in
   their ratios: Gram–Schmidt QR with no shifts.
3. **The closed-form 2D SVD is exact.** The squared singular values are the eigenvalues of the
   Gram matrix: their sum is `|v_1|² + |v_2|²`, and their product is `|v_1 ∧ v_2|²` (the area
   squared). The eigenvector for the larger one is `w_1 ∝ (g_12, λ_1 − g_11)`, with
   `w_2 = w_1.rotate_90_degrees()`. Then `u_i = f(w_i) / σ_i`, and
   `f = U ∘ scale_non_uniform(σ_1, σ_2) ∘ W⁻¹`, where W is
   `versor_rotation(from_vector=e_1, to_vector=w_1)` and U is the route-1 Q of the `u_i`. A frame
   built as `U Σ Wᵀ` from Pythagorean rotations with `σ = 5, 2` is taken apart and rebuilt exactly
   in sympy rationals. 3D would need a cubic's roots: possible, but not done.

What to take from this: the SVD in GA is two chains of rotations from vectors around a
`scale_non_uniform`, and only the axes need a numerical method beyond 2D.

**Not added to the library.** Nothing needs an `svd()` yet, so the routes stay as tests. A
library version would be the 2D closed form plus the QR iteration for 3D, returning
`(U parts, σ, W)` as transforms.

**Bug found on the way, and fixed:** `inverse()` rejected a float 𝒢₃ versor because `Ã * A`
carried a 1e-16 bivector residue, so `versor_rotation` crashed on ordinary 3D float vectors. It now
tolerates rounding residue on inexact input
(`tasks/archive/2026/11/18/inverse-float-versor-rounding.md`), and route 1 uses `versor_rotation`.

## Sources

- [Stanford EE263, QR factorization](https://web.stanford.edu/class/archive/ee/ee263/ee263.1082/lectures/qr.pdf): Gram–Schmidt = QR, triangular R, least squares
- [QR decomposition](https://kaweah.freedombox.rocks/kiwix/wikipedia_en_all_maxi_2023-10/QRD): solving with QR; Gram–Schmidt stability vs Householder/Givens
- [Singular value decomposition](https://en.wikipedia.org/wiki/Singular_value_decomposition): rotation · scaling · rotation
- [Doran, GA2015 Lecture 4](https://geometry.mrao.cam.ac.uk/wp-content/uploads/2015/10/GA2015_Lecture4.pdf): linear functions in GA (outermorphism); mentions SVD as a representation
- `tasks/archive/2026/11/18/define-frame.md`: the task that built frames; its proof and design facts are
  above ("Hestenes' orthogonalization equals rejection")
- `tasks/reference/galgebra-comparison.md`: galgebra's `ReciprocalFrame`
