# Named measures: `area`, `volume`, and the general `content`

**Created:** 2026-08-23 · **Completed:** 2026-08-24

Added named, high-school-legible measures to gacalc in `src/gacalc/measure.py`: `area(a, b)` (the
parallelogram), `volume(a, b, c)` (the parallelepiped) and `content([a_1, …, a_k])`, the k-dimensional
content (hypervolume) of the parallelotope the vectors span (`content([a])` is `|a|`). Then the codebase
and the book were swept for wedges that really mean a measure. Durable knowledge lives in
`tasks/reference/content-area-volume.md` and `tasks/reference/design-decisions.md`.

## Source and citations

The maintainer's copy of **Williamson & Trotter, *Multivariable Mathematics: Linear Algebra, Calculus,
Differential Equations*, 2nd ed., Prentice-Hall, 1979** (ISBN 0-13-604850-1), read 2026-08-23:
"content" → **p. 308**; the recursive height (= rejection) volume → **p. 146**; the parallelogram-area
and `sin` grounding → **pp. 144–145**.

## The math

For vectors `a_1, …, a_k`, two equal ways to compute the same unsigned scalar:
`content = |a_1 ∧ … ∧ a_k|` (`= √det(Gram)`) `= ∏_{j=1..k} |h_j|` (W&T p. 146, the product of heights,
`h_j` = `v_j` rejected from the span of the previous vectors). The heights are exactly gacalc's
`make_orthogonal_frame` (`h_j = w_j`; `tasks/define-frame.md`), so this is the high-school "base ×
height" generalized to k dimensions, and the two computations mirror the two orthogonalizations kept for
teaching.

**A wedge is not its content.** `a ∧ b ∧ c ∧ d` is an oriented grade-4 blade; `content([a,b,c,d])` is
its non-negative magnitude. Rewriting a wedge that needs the blade (orientation, duality, a
reciprocal-frame pseudoscalar, a rotation plane) as a measure would be a correctness bug, so the sweep's
job was telling the two apart.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-23)

1. **Citations** as above.
2. **Free functions** over `MultiVectorBase` are canonical.
3. **`area`/`volume` are aliases** for `content([a,b])` / `content([a,b,c])`, returning the **unsigned
   scalar magnitude**.
4. **The rewrite sweep was a follow-up subtask**, done after the definitions, with a site checklist
   first.
5. **Keep both** `content` (|wedge|) and `content_by_rejection` (∏ heights) public, with an
   equivalence test: the teaching pair, like the two orthogonalizations. `content_by_rejection` is the
   maintainer's name.
6. **Signed content, added on request:** `signed_content`/`signed_area`/`signed_volume`, only when the
   vectors span the full space (k = n). Then `a_1∧…∧a_n = (signed content)·I_n`, and the function returns
   that scalar (the determinant, sign-flipping on a swap, `abs(signed_content) == content`), read off the
   top blade `(1,…,n)`. That needs a fixed-`DIMENSION` type (`g2`/`g3`); `Gn` raises. Signed was not made
   the default or extended to all k: for k < n (two vectors in 3-space) the orientation is the bivector's
   attitude, not a scalar ±, and signed-by-default would restrict `area`/`volume` to full-space inputs.
7. **Pass-through methods for discoverability** (the maintainer's request; typing `v.` surfaces them):
   `a.area(b)`, `a.volume(b, c)`, `a.signed_area(b)`, `a.signed_volume(b, c)` on `MultiVectorBase`,
   inherited by every vector type rather than generated per algebra (the generator specializes
   arithmetic, not sugar). Each is one line delegating to the free function via a deferred import, so
   no import cycle. `content` / `content_by_rejection` and the frame functions stay free-function-only:
   they take a sequence, and `a.content([b, c])` reads awkwardly.

## What was done

- `measure.py`: `content(vectors) = |wedge|` (0 for a dependent set), `content_by_rejection(vectors) =
  ∏|w_j|` (reuses `make_orthogonal_frame`; raises on a non-frame), the `area`/`volume` aliases, and the
  three `signed_*` functions; the pass-through methods in `base.py`.
- Tests in `tests/test_measure.py`: unit measures, oblique area, the aliases, dependent → 0,
  non-vector/empty raise, and `content == content_by_rejection` symbolically (via the squared identity,
  since `sqrt` won't compare structurally) and numerically, in 2D and 3D; for the signed functions, the
  2D/3D determinant, the sign flip, `|signed| == unsigned`, dependent → 0, and the k < n / `Gn` raises;
  `a.area(b) == area(a, b)` and the like; explicit-formula symbolic tests and doctests throughout.
- `tasks/reference/content-area-volume.md` was created: the high-school-math-connection principle, the
  W&T source notes, and the `content = ∏ heights = |wedge| = √det(Gram)` link to the frame work. It
  doubles as the book-source notes the maintainer wanted for later book work.

## The wedge-rewrite sweep (2026-08-23): no rewrite sites

`src/gacalc/**`, `book/docs/**`, `notebooks/**` and `tools/**` were swept. Every wedge needed the
oriented blade, so nothing was rewritten:

- `transforms.py`: `a ^ b` builds the rotation plane, and wedge-is-zero is a parallel-vectors guard.
- `base.py` project/reject/reflect: `outer_product_of_vectors(*seq)` is the subspace's span blade.
- `frame.py`: the wedge is the frame's blade (dependence via `!= 0`) and the Hestenes `A_k`. Its one
  `blade.magnitude()` (in `are_linearly_independent`, float path) is `content`, but it is the primitive
  `content` builds on, and calling `content` there would make frame ← measure circular.
- `g2.py`/`g3.py`: the `coeff_e_1 * rhs.coeff_e_2 …` terms are generated product arithmetic, not a
  determinant to name.
- `notebooks/display*.py`: `a.wedge(b)` is displayed as the bivector to teach `ab = a·b + a∧b`.
- `book/docs/*.rst`: no wedge/area/parallelogram/determinant prose existed yet.

gacalc already kept every wedge as an oriented blade, so the named measures earn their keep in future
code and the book's teaching. An additive line in the teaching notebooks (`displayg2.py`,
`displaymv.py`: "its magnitude is the **area** of the parallelogram, `area(a, b)`") was left to the
maintainer as book authoring.

## Verification

`make test` green: 404 passing, with the generator run in the container.

## Related

Test-readability follow-ups: `tasks/archive/2026/08/25/explicit-symbolic-tests-and-helper-cleanup.md`.
mvp's angle-helper cleanup lived in mvp's own tasks (github.com/billsix/modelviewprojection).
