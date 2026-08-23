# Named measures: `area`, `volume`, and the general `content`

**Status:** complete
**Completed:** 2026-08-24 — all delivered and `make test`-green (404 passing, generator run in-container):
`area`/`volume`/`content` + `content_by_rejection` (teaching pair, equivalence tested) + the SIGNED
`signed_area`/`signed_volume`/`signed_content` (k = n determinant) in `src/gacalc/measure.py`, with the
fixed-arity ones also as pass-through **methods** on `MultiVectorBase`; explicit-formula symbolic tests
and doctests; the **wedge-rewrite sweep** run (result: **no rewrite sites** — every wedge in the code
needs the oriented blade). Durable knowledge in `tasks/reference/content-area-volume.md` and
`tasks/reference/design-decisions.md`. (Test-readability follow-ups live in
`tasks/explicit-symbolic-tests-and-helper-cleanup.md`; mvp's angle-helper cleanup in mvp's own tasks.)
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-08-23 (William Emerison Six <billsix@gmail.com>)

**Source + citations (Bill's copy, read 2026-08-23):** **Williamson & Trotter, *Multivariable
Mathematics: Linear Algebra, Calculus, Differential Equations*, 2nd ed., Prentice-Hall, 1979**
(ISBN 0-13-604850-1). Full source notes in **`tasks/reference/content-area-volume.md`**. Cite:
**"content" → p. 308**; the recursive **height (= rejection) volume** construction → **p. 146**;
the parallelogram-area-and-`sin` grounding → **pp. 144–145**. Design settled: `area`/`volume`/
`content` return the **unsigned scalar magnitude**.

## Goal

Add named, high-school-legible measures to gacalc:

- **`area(a, b)`** — the area of the parallelogram on `a`, `b`.
- **`volume(a, b, c)`** — the volume of the parallelepiped on `a`, `b`, `c`.
- **`content([a_1, …, a_k])`** — the higher-level generalization: the k-dimensional **content**
  (hypervolume) of the parallelotope spanned by the vectors. `area` and `volume` are the k=2 and k=3
  cases; `content([a])` is length `|a|`.

Then **sweep the codebase and the book** for places where a wedge (or the magnitude of one) is really
"an area / volume / content," and re-express them in these named terms where it improves clarity.

## The GA definitions (confirmed against Williamson & Trotter — see `tasks/reference/content-area-volume.md`)

For vectors `a_1, …, a_k`, **two equal ways to compute the same unsigned scalar**:

>   `content([a_1, …, a_k]) = |a_1 ∧ … ∧ a_k|`   (magnitude of the wedge, `= √det(Gram)`)
>                           = `∏_{j=1..k} |h_j|`   (W&T p. 146: product of heights, `h_j` = rejections)

So `area(a,b) = |a ∧ b|`, `volume(a,b,c) = |a ∧ b ∧ c|`, and these are `content` at k = 2, 3.
**W&T p. 146 defines volume recursively by heights** — `h_j` = `v_j` rejected from the span of the
previous — which **is exactly gacalc's `make_orthogonal_frame`** (`h_j = w_j`; `tasks/define-frame.md`).
So `content = ∏ |w_j| = |wedge| = √det(Gram)`: the high-school "base × height" (area), "base-area ×
height" (volume), generalized to k dimensions. The two ways to compute it mirror the two
orthogonalizations we keep for teaching — see the implementation open question (Q5).

## The load-bearing caveat for the rewrite sweep — a wedge is NOT its content

`a ∧ b ∧ c ∧ d` is an **oriented blade** (a multivector, grade 4); `content([a,b,c,d])` is its
**magnitude** (a non-negative scalar). They are NOT interchangeable. So the sweep must only rewrite a
wedge → `content`/`area`/`volume` where the code/book actually wants the **scalar measure**, not the
oriented blade. Rewriting a site that needs the blade (orientation, duality, a reciprocal-frame
pseudoscalar, a rotation plane) would be a correctness bug. Bill's `a^b^c^d → content([a,b,c,d])`
example holds only at magnitude-wanting sites; the sweep's real work is telling the two apart.
## Pass-through methods on the base (added 2026-08-23, Bill's request — discoverability)

For learning/discoverability (typing `v.` on a vector surfaces the operation), thin **pass-through
methods** are added on **`MultiVectorBase`** (base.py) — **inherited by every vector type, NOT
generated per-algebra** (one method serves `g2`/`g3`/`Gn`; the generator specializes closed-form
arithmetic, not sugar). Each is one line delegating to the free function via a **deferred import**
(the pattern base.py already uses for `Gn`), so no import cycle:

- `a.area(b)`, `a.volume(b, c)`, `a.signed_area(b)`, `a.signed_volume(b, c)`.

Only the **fixed-arity** measures get methods; **`content` / `content_by_rejection` and the frame
functions stay free-function-only** — they take a *sequence*, so `a.content([b, c])` reads awkwardly.
The free functions remain canonical; methods are sugar over them. Tests assert `a.area(b) == area(a, b)`
etc.; the methods carry their own doctests.

## Signed content (added 2026-08-23, Bill's request)

`content`/`area`/`volume` are the **unsigned** magnitude `|a_1∧…∧a_k|` — always defined, any k ≤ n, any
dimension (W&T's measure). The **signed (oriented) determinant** is available separately as
**`signed_content`/`signed_area`/`signed_volume`**, but **only when the vectors span the full space
(k = n)**: then `a_1∧…∧a_n = (signed content)·I_n` and `signed_content` returns that scalar — the
determinant, sign-flipping on a swap, with `abs(signed_content) == content`. Implemented by reading the
coefficient of the top blade `(1,…,n)` off the wedge (needs a fixed-`DIMENSION` graded type — `g2`/`g3`;
`Gn` has no dimension). **Why not signed by default / for all k:** for **k < n** (e.g. the area of two
vectors in 3-space) the orientation is the wedge *bivector's* attitude, not a scalar ±, so there is no
signed scalar — and making `area`/`volume` signed-by-default would restrict them to full-space inputs.
Keeping unsigned general + `signed_*` for k = n gives the sign where it exists without crippling the
general functions. Tests cover the 2D/3D determinant, the sign flip, `|signed| == unsigned`, dependent
→ 0, and the k < n / `Gn` raises.

## Plan

1. **[DONE] Book + citations** — Williamson & Trotter, *Multivariable Mathematics*, 2nd ed. (1979):
   "content" p. 308, recursive-height volume p. 146, parallelogram/sin pp. 144–145. Source notes in
   `tasks/reference/content-area-volume.md`. Design: **unsigned scalar magnitude**.
2. **[DONE] Define the named measures** — `src/gacalc/measure.py` (free functions over
   `MultiVectorBase`): `content(vectors) = |wedge|` (W&T p. 308; unsigned scalar; 0 for a dependent
   set), `content_by_rejection(vectors) = ∏|w_j|` (W&T p. 146, reuses `make_orthogonal_frame`; raises on
   a non-frame), and `area(a,b)` / `volume(a,b,c)` as **aliases** for `content`. `tests/test_measure.py`
   (8 tests): unit measures, oblique area, the aliases, dependent→0, non-vector/empty raise, and
   `content == content_by_rejection` symbolic (via the squared identity — `sqrt` won't compare
   structurally) + numeric, 2D & 3D.
3. **[FOLLOW-UP SUBTASK] Codebase + book sweep** — see "Subtask — wedge-rewrite sweep" below.
4. **[DONE] Reference doc** — `tasks/reference/content-area-volume.md` created 2026-08-23: the
   high-school-math-connection principle, the W&T source notes (bibliography + pp. 144–146, 308), and
   the `content = ∏ heights = |wedge| = √det(Gram)` connection to the frame work. It doubles as the
   pedagogical-principle doc (this task's planned deliverable) and the book-source notes Bill wanted for
   the book work later.

## Subtask — wedge-rewrite sweep — DONE 2026-08-23: **no rewrite sites found**

Swept `src/gacalc/**`, `book/docs/**`, `notebooks/**`, `tools/**`. **Result: nothing to rewrite** —
every wedge / `outer_product_of_vectors` use in the codebase genuinely needs the **oriented blade**,
not the scalar magnitude, so the caveat below says leave them all:

- **`transforms.py`** — `a ^ b` builds the rotation **plane** (a normalized bivector), and the
  wedge-is-zero test is a parallel-vectors guard. Blade, not area. Keep.
- **`base.py` project/reject/reflect** — `outer_product_of_vectors(*seq)` is the **span blade** of the
  subspace. Keep.
- **`frame.py`** — the wedge is the frame's blade (dependence via `!= 0`) / the Hestenes `A_k`; the one
  `blade.magnitude()` (in `are_linearly_independent`, float path) **is** `content`, but it's the
  primitive `content` is built on and can't call it (frame ← measure would be circular). Keep.
- **`g2.py`/`g3.py`** — the `coeff_e_1 * rhs.coeff_e_2 …` terms are **generated** closed-form product
  arithmetic, not a determinant computation to name. Keep.
- **`notebooks/display*.py`** — `a.wedge(b)` is **displayed as the bivector** to teach `ab = a·b + a∧b`.
  Keep (see additive opportunity below).
- **`book/docs/*.rst`** — no wedge / area / parallelogram / determinant prose exists yet. Nothing to
  rewrite.

**Why zero sites:** gacalc already keeps every wedge as an oriented blade (correct), so there were no
magnitude-of-wedge computations to consolidate. `area`/`volume`/`content` earn their keep in **future**
code and the **book's teaching**, not by retrofitting existing code.

**Additive opportunity (NOT a rewrite; Bill's book/notebook call):** the teaching notebooks
(`displayg2.py` shows `a∧b`; `displaymv.py`) could gain a line — "…and its magnitude is the **area** of
the parallelogram, `area(a, b)`" — connecting the wedge to the high-school concept, per
`tasks/reference/content-area-volume.md`. Left for Bill (book authoring).

## Subtask — wedge-rewrite sweep (original plan; superseded by the DONE result above)

Now that `area`/`volume`/`content` exist, sweep the **codebase** and the **book** for places where a
wedge (or `|wedge|`) really means a scalar **area / volume / content**, and re-express them in the named
terms. **Report a checklist first** (site → keep-as-blade vs rewrite-as-measure, with reason) and get
Bill's go-ahead before editing — because the oriented-blade-vs-magnitude caveat means many wedge sites
must NOT be rewritten (orientation, duality, reciprocal-frame pseudoscalar, rotation plane).

- **Codebase candidates:** `outer_product_of_vectors` callers; any `(a ^ b).magnitude()` /
  `.magnitude()` of a blade; the frame volume relation (`|A_k|`); plot/notebook code that labels an
  area or volume.
- **Book:** `book/docs/*.rst` discussing wedge / area / volume / hypervolume that could speak in these
  named terms — respect the doc-region markers; a listing change follows the `literalinclude` rules.
- Deliverable: the checklist, then (after approval) the rewrites, then re-run the gate.

## Open questions — resolved 2026-08-23

All resolved by Bill, 2026-08-23:

1. **Citation** → W&T 2nd ed. (1979) **p. 308** ("content"); **p. 146** (recursive-height volume). Cited.
2. **Free functions** (not methods). ✓
3. **`area`/`volume` are aliases** for `content([a,b])` / `content([a,b,c])`. ✓
4. **Rewrite sweep = a follow-up subtask** (do after the definitions; report the checklist first). ✓
5. **Keep BOTH** `content` (|wedge|) and `content_by_rejection` (∏ heights) public, with the equivalence
   test — the teaching pair, like the two orthogonalizations. ✓ (Second function named
   `content_by_rejection` — Bill's chosen name.)
6. **Signed content?** — added on request: unsigned general functions + `signed_*` for k = n (see
   "Signed content" above). ✓
