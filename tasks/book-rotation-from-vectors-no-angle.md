# Book section: a rotation that takes vector a to vector b, without naming an angle

**Status:** proposed — needs go-ahead (a *later* book section; not on the critical path)
**Priority:** 8
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

A book idea to pursue **later**: present a rotation defined by a **from-vector and a
to-vector** — "rotate the direction of :math:`\vec{a}` onto the direction of :math:`\vec{b}`"
— with **no angle ever named**. The machinery already exists in gacalc (both Python and the
Lean proofs); this task is only about *writing the book section that teaches it*. It is
deliberately **not** used in the standard-position projection proof
(`book/docs/proof-projection.rst`, archived task
`tasks/archive/2026/10/08/projection-standard-position-make-2d.md`), which is grounded in the
angle-based `r(v; θ)` rotation on purpose — this is the complementary "you don't even need the
angle" story, for a later chapter.

**Do the 2D case first (maintainer, 2026-10-08):** the primary deliverable is a **2D**
rotate-from-:math:`\vec{a}`-to-:math:`\vec{b}`, **derived from the book's own building
blocks** — the rotation `r(v; θ)` of `proof-rotate.rst`, projection/rejection, and the
geometric product — rather than presented as a library call. In the book's 2D-first-then-3D
structure (`tasks/reference/book-outline.md`) this is a Part I section; the 3D version is the
later step-up. **Do not start yet.**

## The 2D construction (do first), from our own building blocks

Candidate derivations, all strictly 2D and angle-free, to pick among / sequence when writing:

- **From the geometric product (the cleanest):** for unit vectors :math:`\hat a, \hat b`, the
  product :math:`\hat a\,\hat b` *is* the full-angle rotor that carries :math:`\hat a` to
  :math:`\hat b` — right-multiplying by it rotates. This is exactly `uvec_mul_uvec`
  (`(uvec α)(uvec β) = fullAngleRotor(β − α)`) and `fullAngleRotorFromTo` /
  `fullAngleRotorFromTo_carry` in `proofs/GacalcProofs/Rotation2D.lean`, and the one-sided
  2D rotor is the students' first encounter there. No angle is ever named — the two vectors
  supply the cosine and sine directly (`uvec_dot` / `uvec_wedge`).
- **From project/reject:** `projRotation f t v` in 𝒢₂
  (`proofs/GacalcProofs/ProjectionRotation2D.lean`) builds the same rotation from
  projection/rejection; proven to carry from→to, be an isometry, and equal the versor sandwich.
- **From `r(v; θ)` (the contrast):** the angle-based rotation needs the angle; showing that the
  product/project routes give the *same* map without ever naming it is the payoff to highlight.

The Python side for the 2D case: `g2`'s `versor_from_vectors` / `rotor_from_vectors` and
`transforms.versor_rotation` / `projection_rotation`.

## What already exists (so the section is write-up, not new math)

- **Python (gacalc):**
  - `MultiVectorBase.versor_from_vectors(from, to)` and `rotor_from_vectors(from, to)`
    (`src/gacalc/base.py`; specialized in `g2`/`g3`) — the versor / unit-versor that carries
    `from` to `to`.
  - `transforms.projection_rotation(from, to)`, `transforms.versor_rotation(from, to)`,
    `transforms.plane_rotation(a, b)` (`src/gacalc/transforms.py`) — `InvertibleFunction`
    rotation factories keyed by two vectors, no angle argument.
- **Lean (machine-checked):** `projRotation f t v` in `proofs/GacalcProofs/ProjectionRotation2D.lean`
  and `ProjectionRotation3D.lean` — "a general rotation defined from project/reject," proven to
  carry from→to (`projRotation_carries_from_to`), to be an isometry (`projRotation_isometry`),
  and to equal the versor sandwich (`projRotation_eq_sandwich`). The durable account is in
  `tasks/reference/reduction-to-standard-position.md` ("Step 3 — the general rotation from
  project/reject", "2D specialization").
- **modelviewprojection** has no distinct construct of its own — it only vendors gacalc's
  `rotor_from_vectors` (`book/docs/_gacalc_src/base.py`). So this is a gacalc story.

## Why it is worth a section

The projection proof needed the angle because it reduces to standard position. But the
*geometric-algebra* way to rotate "from here to there" never mentions an angle: the geometric
product `b a / |b||a|` (or the versor from the two vectors) already encodes the rotation that
takes one direction to the other. Teaching that — side by side with the angle-based rotation
of `proof-rotate.rst` — is a payoff moment: the angle was scaffolding; the vectors are enough.

## Open questions (for when this is picked up)

1. Which home — a new `.rst` (e.g. `rotation-from-vectors.rst`) in Part I, or folded into an
   existing chapter? It likely belongs *after* `geometric-product.rst` (it needs the product)
   and relates to `projection.rst`.
2. Which of the three 2D derivations above to lead with (recommend the geometric-product one),
   and how much of the project/reject route to show alongside. (2D-first-then-3D is decided —
   maintainer, 2026-10-08.)

## See also

- `tasks/book-proof-rotate-from-a-to-b.md` — the **angle-based** rotate-from-a-to-b proof
  (reduction-to-standard-position, cos/sin, per-step diagrams), the companion to this angle-free
  version. That one comes first (right after "Proof: Rotate"); this is the later "you don't even need
  the angle" payoff.
- `tasks/reference/reduction-to-standard-position.md` — the proven `projRotation` account.
- `tasks/reference/transform-and-composable-function-layer.md` — the rotation factories.
- `tasks/reference/unit-bivector-and-rotors.md` — the versor / rotor math.
