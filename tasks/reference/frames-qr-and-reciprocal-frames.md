# Frames, the QR decomposition, and reciprocal frames

**Reference document.** This explains what the QR decomposition is, why orthonormalizing a frame and
recording its coefficients *is* QR, how that gives an inverse without row reduction, and how it relates to
Hestenes' reciprocal frame and to the SVD, and why gacalc's implementation stores the frame orthogonal
rather than orthonormal. gacalc implements it as `gacalc.frame.Frame` (`src/gacalc/frame.py`, tests in
`tests/test_frame_class.py`); the build record is `tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md`.
Open follow-ups: `tasks/reciprocal-frame-hestenes.md`, `tasks/frame-svd-investigation.md`,
`tasks/frame-notebooks-epix.md`. Created 2026-11-04 (William Emerison Six <billsix@gmail.com>). Update in
place.

## L0 — the capsule

Take a frame `v_1 … v_k` (linearly independent vectors). Gram–Schmidt orthonormalize it to `u_1 … u_k`,
and write each original vector in the new basis: `v_i = Σ_j c_ij u_j` with `c_ij = u_j · v_i`. Ordinary
linear algebra calls this pair the **QR decomposition** `V = Q R`. Q is the orthonormal vectors as
columns. R is the coefficients, and it is **upper triangular**: `v_i` needs only `u_1 … u_i`. To invert
the map `x ↦ Σ x_i v_i`, dot the output with each `u_j`, then undo the triangle from the last coordinate
backwards. That is the standard numerical way to solve linear systems and least-squares problems. GA adds
a geometric reading of every piece. gacalc's `Frame` stores the same decomposition with the lengths
factored out (orthogonal `w_j`, coefficients `(w_j · v_i) / |w_j|²`) so symbolic results stay free of
square roots; see "Why gacalc's `Frame` is stored orthogonal, not orthonormal".

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

With the orthogonal `w_j` in place of the `u_j`, the same two steps read: `(w_j · y) / |w_j|²` in step 1,
and a back-substitution whose diagonal is 1 in step 2. This is what `Frame.to_invertible_function()`
computes.

## Why gacalc's `Frame` is stored orthogonal, not orthonormal

`Frame` (`src/gacalc/frame.py`) stores the **orthogonal** `w_j` and the coefficients
`coefficients[i][j] = (w_j · v_i) / |w_j|²`, so `v_i = Σ_j coefficients[i][j] * w_j`. The orthonormal
`u_j = w_j / |w_j|` are available on demand through `Frame.orthonormal_vectors()`. Indexed as
`coefficients[original i][orthogonal j]`, the table is zero above its diagonal (it is R transposed,
rescaled). This is the same QR
decomposition with the lengths moved out of Q: R's entries are `coefficients[i][j] * |w_j|`, and the
stored table has ones on its diagonal.

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
divide by `|w_j|²` where the orthonormal design would rely on unit length. Every stored value is then a
**rational function** of the inputs, which sympy can decide exactly. The inverse is unchanged in shape:
dot `y` with each `w_j`, divide by `|w_j|²`, then back-substitute. Measured on a fully symbolic 3D frame:

| configuration | build | rebuild + both round trips |
|---|---|---|
| orthonormal, `Gn` | 9 s orthogonalization, then normalization never finished | did not finish |
| orthogonal, `g3.Vector` (lazy) | 0.08 s | `cancel` check did not finish in 280 s |
| **orthogonal, `Gn`, rejection** (chosen) | 79 s | passes; 151 s total |
| orthogonal, `Gn`, Hestenes `inverse(A_{k-1}) * A_k` | 60 s | passes; 103 s total |
| orthogonal, `Gn`, Hestenes `reverse(A_{k-1}) * A_k` | 15 s | round trip did not finish in 240 s |

The test suite (`tests/test_frame_class.py`) builds the 3D symbolic frame once per module and runs in
about 3.5 minutes. The maintainer prefers correctness to runtime (2026-11-04), so the fully symbolic 3D
tests stay in the default suite rather than being replaced by numeric spot checks.

**Why rejection rather than a Hestenes closed form.** Both Hestenes forms rest on `prefix_blades`,
which seeds `A_0` with `type(v).one()`. For the graded `g2`/`g3` `Vector` types that value is the
**zero vector** (a Vector type cannot hold a scalar), so both forms return zeros on graded input. That
is tracked in `tasks/frame-prefix-blades-graded-zero-seed.md`. Rejection (`make_orthogonal_frame`)
works on every representation, and it is the orthogonalization the maintainer wrote. The `inverse`
variant was slightly faster on `Gn`, but not enough to give that up.

## The relation to Hestenes' reciprocal frame

The reciprocal frame `v¹ … vᵏ` is defined by `vⁱ · v_j = δⁱ_j`. It gives coordinates in one step:
`x_i = vⁱ · y`. galgebra (and H&S) build it from the pseudoscalar `E = v_1 ∧ … ∧ v_n`:
`vⁱ = (−1)^(i−1) * (v_1 ∧ … ∧ v̌_i ∧ … ∧ v_n) · E⁻¹`, where `v̌_i` means "leave `v_i` out". With gacalc's
`inner_product` and `inverse`, this gave `[vⁱ · v_j]` = the identity on concrete 2D and 3D frames
(2026-11-04). The exact H&S page and equation are not yet confirmed; see
`tasks/reciprocal-frame-hestenes.md`, which also has a longer explainer.

QR connects to it directly:

- **The last reciprocal vector is the last rejection:** `vᵏ = w_k / |w_k|² = u_k / c_kk`. The reason:
  `w_k` is orthogonal to `v_1 … v_{k-1}`, and `w_k · v_k = |w_k|²`. Back-substitution's first step,
  `x_k = (u_k · y)/c_kk`, is exactly `vᵏ · y`.
- More generally, the reciprocal frame is the columns of `V⁻ᵀ = Q R⁻ᵀ`. Back-substitution builds the
  reciprocal frame one vector at a time, from the end backwards.
- A corollary: orthogonalizing with `v_i` placed **last** yields `vⁱ` directly as `w/|w|²`.

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
