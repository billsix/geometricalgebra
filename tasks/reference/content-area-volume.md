# Content, area, volume — the Williamson–Trotter grounding + the high-school-math connection

**What this is:** source notes on the definitions of area / volume / **content** from Williamson &
Trotter, *Multivariable Mathematics* (2nd ed., 1979) — the book gacalc's planned `area`/`volume`/
`content` measures are named after (`tasks/area-volume-content.md`) — plus the standing pedagogical
principle that gacalc and its book should connect back to high-school math as much as possible.
Recorded 2026-08-23 from Bill's reading of his own copy (William Emerison Six <billsix@gmail.com>).

## The pedagogical principle (why this doc exists)

**Everything in gacalc / the book should connect back to high-school math — length, area, volume, and
their k-dimensional generalization "content" — as much as possible.** A student meets `a ∧ b` and
should hear *"the area of the parallelogram on a and b"*; `a ∧ b ∧ c` is *"the volume"*; the general
wedge magnitude is *"content"* (k-dimensional volume). Prefer the named measure (`area`/`volume`/
`content`) over a bare `|wedge|` in teaching-facing code and prose, and state the high-school anchor
when introducing a GA construct. This is the gacalc sibling of mvp's "speak in edges/paths/inverses,
not matrices" pedagogy.

## Source (bibliography — cite this form)

> Richard E. Williamson and Hale F. Trotter. *Multivariable Mathematics: Linear Algebra, Calculus,
> Differential Equations.* 2nd ed. Prentice-Hall, Englewood Cliffs, NJ, 1979. ISBN 0-13-604850-1.

Bill's copy is the **2nd ed. (1979)**; the 1974 1st ed. orders the subtitle words differently, so cite
the 2nd ed. Internet Archive (borrow): `archive.org/details/multivariablemat02edwill`.

## The relevant pages (Bill's reading, 2026-08-23)

- **pp. 144–145 — geometric properties of vectors.** Connects the geometric interpretation of vectors,
  parallelograms, and **sin**: the area of the parallelogram on two vectors is `|v₁| |v₂| sin θ`. Good
  grounding to reference when writing the book's vector chapters (Bill flagged it for that).
- **p. 145 — the k-dimensional parallelepiped.** Defines the parallelepiped spanned by k vectors — the
  k-dimensional generalization of the parallelogram (k = 2) and the parallelepiped (k = 3).
  ("Parallelepiped" is the word Bill wants to keep on hand.)
- **p. 146 — volume, defined recursively by heights (= rejections).**
  - **1-D volume** = `|V₁|` (length).
  - **2-D volume** = `|V₁| · |h₂|`, where `h₂` is the height of `V₂` *away from* `V₁` — **in gacalc's
    terms, `h₂` is `V₂` rejected from `V₁`** (post-reject). That is base × height = the parallelogram
    area.
  - **3-D volume** = (2-D volume) · `|h₃|`, where `h₃` is the third vector **rejected from the plane of
    the first two**.
  - So in general **k-D volume = `∏_{j=1..k} |h_j|`**, with `h_j` = `v_j` rejected from the span of the
    ones before it.
- **p. 308 — the word "content".** Defines **content** as the general term for area / volume / the
  higher-dimensional version of that concept. This is the term gacalc adopts: `content([a₁,…,a_k])` is
  the k-dimensional content. **Cite W&T p. 308 for `content`; p. 146 for the recursive height
  construction; p. 144–145 for the parallelogram-area-and-sin grounding.**

## The connection to gacalc (why this book, specifically)

W&T's recursive volume — `∏ |h_j|`, the heights being rejections — is **exactly gacalc's frame
orthogonalization** (`make_orthogonal_frame`, `tasks/define-frame.md`): each `h_j` = `v_j` rejected
from the span of the previous vectors = the orthogonalized `w_j`. Hence

>   `content([v₁,…,v_k]) = ∏_j |w_j| = |v₁ ∧ … ∧ v_k| = √det(Gram)`.

So there are **two equal ways to compute content**: W&T's **product of rejected heights**, and the
**magnitude of the wedge blade**. That is the same "two constructions, one result" pattern as the two
orthogonalizations gacalc already keeps side by side for teaching (rejection vs Hestenes' blade
product; see `tasks/reference/design-decisions.md`). Whether gacalc implements `content` as `|wedge|`,
as `∏ |heights|`, or **both with an equivalence test** is the open implementation question in
`tasks/area-volume-content.md`.

## Signed (oriented) content — the determinant, for k = n

`content`/`area`/`volume` are **unsigned** (a magnitude, W&T's measure). gacalc also exposes the
**signed** content — `signed_content`/`signed_area`/`signed_volume` — but only when the vectors span
the full space (`k = n`): then `a_1∧…∧a_n = (signed content)·I_n`, and the signed content is that
scalar — the **determinant**, which flips sign when two vectors swap, with `abs(signed) == unsigned`.
For `k < n` (e.g. the area of two vectors in 3-space) the orientation is the wedge *bivector's*
attitude, not a scalar ±, so there is no signed scalar and it raises; likewise for the dimensionless
`Gn`. This is the high-school "signed area = `ad − bc`" / right-hand-rule orientation — kept general
functions unsigned so they still work for any `k ≤ n`, with the sign added only where it exists.

## How they're exposed (free functions + a little method sugar)

The canonical interface is the **free functions** in `gacalc.measure` (`area`, `volume`, `content`,
`content_by_rejection`, `signed_area`, `signed_volume`, `signed_content`). For discoverability, the
**fixed-arity** ones also exist as **inherited methods on `MultiVectorBase`** — `v.area(w)`,
`v.volume(w, u)`, `v.signed_area(w)`, `v.signed_volume(w, u)` — thin pass-throughs (a deferred import,
inherited by every vector type, *not* generated per-algebra). `content` / `content_by_rejection` take a
*sequence*, so they stay free-function-only.

## Related

- `tasks/area-volume-content.md` — the task that defines `area`/`volume`/`content` and sweeps the
  codebase/book for wedge-magnitude sites to rename in these terms.
- `tasks/define-frame.md` — the frame orthogonalization whose `∏ |w_j|` *is* W&T's recursive volume.
