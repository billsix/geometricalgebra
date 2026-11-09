# Book section: a rotation that takes vector a to vector b, without naming an angle

**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-10-19 (agent, unattended batch)

Wrote the book section that presents a rotation defined by a **from-vector and a to-vector** —
"rotate the direction of :math:`\vec{a}` onto the direction of :math:`\vec{b}`" — with **no angle
ever named**. The machinery already existed in gacalc (Python and the Lean proofs), so this was a
write-up, not new math. It is deliberately **not** used in the standard-position projection proof
(`book/docs/proof-projection.rst`, `tasks/archive/2026/10/08/projection-standard-position-make-2d.md`),
which is grounded in the angle-based `r(v; θ)` rotation on purpose; this is the complementary "you
don't even need the angle" story. The prose carries a `Draft` banner for the maintainer's voice pass.

## Why it earned a section

The projection proof needed the angle because it reduces to standard position. The geometric-algebra
way to rotate "from here to there" never mentions an angle: the geometric product `b a / |b||a|` (or
the versor from the two vectors) already encodes the rotation that takes one direction to the other.
Shown side by side with the angle-based rotation of `proof-rotate.rst`, the angle turns out to be
scaffolding; the vectors are enough.

## Decisions

- **2D first** (the maintainer, 2026-10-08): the deliverable was a **2D** rotate-from-`a`-to-`b`,
  **derived from the book's own building blocks** — `r(v; θ)` of `proof-rotate.rst`,
  projection/rejection, and the geometric product — rather than presented as a library call; a Part I
  section in the book's 2D-first-then-3D structure (`tasks/reference/book-outline.md`), with 3D as the
  later step-up.
- The agent took the task's own recommendations for the two questions it had raised (unattended batch,
  2026-10-19):
  1. **Home:** a new page `book/docs/rotation-from-vectors.rst`, a child of `geometric-product.rst`'s
     toctree (it needs the product), not folded into an existing chapter.
  2. **Lead derivation:** the geometric-product route — the product of two unit vectors `â * b̂` is the
     full-angle rotor, and `â * (â * b̂) = b̂` by associativity + `â * â = 1`, no angle named
     (`uvec_mul_uvec`: `(uvec α)(uvec β) = fullAngleRotor(β − α)`; the vectors supply the cosine and
     sine directly via `uvec_dot`/`uvec_wedge`). The project/reject route (`projRotation`) was shown
     second (shorter), and the angle-based `proof-rotate-from-a-to-b` contrasted as "the angle was
     scaffolding."
- **Draft banner** (`.. note:: Draft`) on the prose, matching the `levels-of-abstraction` /
  `vector-addition` voice-pass pattern; the notebook and the cited Lean are not draft.

## What was done

- **Prose:** `book/docs/rotation-from-vectors.rst` — "A Rotation from Two Vectors — No Angle," wired
  into `geometric-product.rst`'s nested toctree. No ePiX figures.
- **Notebook:** `book/docs/notebooks/rotation-from-vectors.py` (percent-format, every binding typed)
  checks symbolically: the product of two unit vectors is the rotor (`cos(α−β) − sin(α−β) e₁₂`), the
  carry `â * (â * b̂) − b̂ == 0`, the versor and projection routes agree, and the rotation carries
  `frm` onto `(|frm|/|to|) * to`.
- **Cited, not written** (already existed): Lean `uvec_mul_uvec`, `uvec_dot`, `uvec_wedge`,
  `fullAngleRotorFromTo_carry` (`proofs/GacalcProofs/Rotation2D.lean`); `projRotation_carries_from_to`,
  `projRotation_isometry`, `projRotation_eq_sandwich` (`ProjectionRotation2D.lean`, also
  `ProjectionRotation3D.lean`); Python `versor_from_vectors`/`rotor_from_vectors` (`base.py`),
  `versor_rotation`/`projection_rotation`/`plane_rotation` (`transforms.py`). modelviewprojection has no
  construct of its own (it only vendors gacalc's `rotor_from_vectors`), so this is a gacalc story.
- **Doc delta:** `tasks/reference/book-outline.md` lists the new page + notebook.

## Verification

`ruff check`/`ruff format --check` clean, `ty check book/docs/notebooks` clean,
`tools/check_annotations.py` reported no row for the new notebook, and the notebook's four checks
executed host-side to the zero vector / equality. The full `make docs` (Sphinx HTML + lualatex PDF) was
run in-sandbox against the existing `gacalc:latest` BUILD_DOCS image via `docs.sh`'s own `podman run`
(avoiding the `: image` nested rebuild); its result went to the session report and was not recorded
here. The build is not `-W`, so unresolved cross-refs would be warnings, not errors.

## See also

- `tasks/archive/2026/10/08/book-proof-rotate-from-a-to-b.md` — the **angle-based** rotate-from-a-to-b
  proof (reduction to standard position, cos/sin, per-step diagrams), which comes first (right after
  "Proof: Rotate"); this is the later payoff.
- `tasks/reference/reduction-to-standard-position.md` — the proven `projRotation` account ("Step 3 — the
  general rotation from project/reject", "2D specialization").
- `tasks/reference/transform-and-composable-function-layer.md` — the rotation factories.
- `tasks/reference/unit-bivector-and-rotors.md` — the versor / rotor math.
