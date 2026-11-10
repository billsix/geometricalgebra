# Standard-position project/reject: defined on the e_3 axis, built from 2-D vector-to-vector rotations

**Status:** ready — the design is decided (Decisions, 2026-11-10)
**Priority:** 4
**Difficulty:** 5
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

`project_sp`/`reject_sp` (`src/gacalc/standardposition.py`) raise `ValueError` when `b` lies along
`e_3`, because the first alignment step divides by `|xy-part of b| = 0`. Make them **defined
there** with the zero-vector rule (0 → 0 is the identity; 0 → nonzero raises `ValueError`), and
rebuild each plane rotation the way the book writes a rotation: **a sum of scalars times vectors**,

    rotate(v) = cos * v_plane + sin * rotate_90_degrees(v_plane) + v_axis,

the book's equation `eq-rotate-formula` (`book/docs/proof-rotate.rst`), with `cos`/`sin` read off
coordinates as in `book/docs/proof-rotate-from-a-to-b.rst` and no angle computed. The current
expanded-component form, `(cos * x - sin * y) * e_1 + (sin * x + cos * y) * e_2 + z * e_3`, goes.
As in modelviewprojection, where the maintainer first defined it, the quarter turn is a 2-D
operation in the e_1/e_2 plane only: gacalc's existing method `g2.Vector.rotate_90_degrees()`, which
is built from coordinates (`(x, y) ↦ (-y, x)`), not from the geometric product.
Each 3-D plane rotation copies that plane's two coordinates into a 2-D vector, rotates it there, and
writes it back, leaving the third coordinate alone. Done means:
`project_sp(a, 1 * e_3) == a.projected_onto(e_3)`, the 0→0 / 0→a rule is doctested, the Lean
`StandardPosition.lean` transcription follows the new shape, and the gate (`make test`,
`make type-check`, the Lean build) is green.

## Context (read first)

- `tasks/reference/reduction-to-standard-position.md` — the theme and the **non-circular bootstrap**
  (elementary plane rotations → project/reject → `projection_rotation`). The module docstring says no
  versors / geometric product / matrices, so the rotation used here is built from coordinates, **not**
  from `transforms.projection_rotation` (defined from project/reject) — decided (Decisions).
- `book/docs/proof-rotate.rst` — `eq-rotate-formula`: `r(a; θ) = cos(θ) * a + sin(θ) * r(a; π/2)`,
  `r(a; π/2) = (-a_2, a_1)`. "A rotation is a blend of the point and its 90°-rotated self." This is
  the shape the code must read as.
- `book/docs/proof-rotate-from-a-to-b.rst` — the rotation from `a`'s direction to `b`'s collapses to
  one turn with `cos = (a_1 b_1 + a_2 b_2)/(|a||b|)`, `sin = (a_1 b_2 - a_2 b_1)/(|a||b|)`, applied
  as `cos * v + sin * r(v; π/2)`; Lean `rotateFromTo_collapse` / `rotateFromTo_carries`
  (`proofs/GacalcProofs/RotateFromTo2D.lean`).
- `book/docs/proof-projection-3d.rst` — the 3-D page: swing the xy shadow onto the x-axis, then the
  z part down, "one plane at a time, each a plain 2D rotation that leaves the third coordinate alone".
- The quarter turn to use is the **method** `g2.Vector.rotate_90_degrees()` (`src/gacalc/g2.py`,
  emitted by `tools/gen_specialized.py`): its body is `Vector(coeff_e_1=-self.coeff_e_2,
  coeff_e_2=self.coeff_e_1)`, coordinates only; the `== v * Bivector.e_12` line is a doctest, not
  the definition. So 𝒢₂'s quarter turn bootstraps the 3-D plane rotations with no self-reference.
  The generator derives that body from `v * e_12` at generation time, but the emitted code is the
  coordinate swap. (The module-level factory `g2.rotate_90_degrees()` wraps the same method as an
  `InvertibleFunction`; the method is all this task needs.) For a turn by an angle there is now
  `g2.Vector.rotate(θ)` (`tasks/archive/2026/11/10/g2-rotate-by-angle-restore.md`); this task reads
  `cos`/`sin` off coordinates instead, so it writes the same blend inline.
- `book/docs/notebooks/proof-cross.py` hand-writes `rotate_xy`/`rotate_xz`/`rotate_yz` in the
  expanded form; rewrite them the same way (copy the pair into a `g2.Vector`, blend, write back). `g2` imports `base`, `functions`, `gn` and
  `transforms`, never `standardposition`, so the new import has no cycle.
- History, gacalc: the first version (`80f44ae`) and today's (`e6b2f96`, `126ce69`) both use the
  expanded `(cos * x - sin * y, sin * x + cos * y)` components; none used the scalar-times-vector form.
- History, github.com/billsix/modelviewprojection — where the 2-D derivation began. Read these two
  commits; they are the model for this task:
  - `917fbe3f` (2024-09-11, "updated definition of rotate and added uniform scale") gave the 2-D
    `Vertex` `rotate_90_degrees(self) -> Vertex(x=-self.y, y=self.x)` and rewrote `rotate` from the
    expanded components to `cos(θ) * self + sin(θ) * self.rotate_90_degrees()`, the change asked for
    here.
  - `6347afa3` (2024-09-11, "update rotate in 3D to use rotate from 2D", `book/src/demo14/demo.py`)
    built the 3-D `rotate_x`/`rotate_y`/`rotate_z` from that 2-D rotate: e.g. `rotate_x` copies
    `(y, z)` into a `Vertex2D`, rotates it, and returns `Vertex(x=self.x, y=r.x, z=r.y)`.
  - mvp later replaced these with gacalc's rotor-based factories (`d1bb728b`, 2026-07-08), so the
    current mvp tree no longer has the coordinate form.
- `proofs/GacalcProofs/StandardPosition.lean` (`projectSP_eq_proj`, `rejectSP_eq_reject`) transcribes
  the current `(cos, sin)` formulas; it must follow the change.
- `transforms.projection_rotation` already treats parallel same-direction vectors as the identity and
  opposite ones as a `ValueError`; whether the zero rule also applies to the public rotation factories
  is decided: yes, all of them (Decisions).

## Plan

1. Use the existing `g2.Vector.rotate_90_degrees()` method as the quarter turn; no new function.
   (If the code generator ever changes that method to multiply by `e_12`, the bootstrap breaks; add
   a comment at the call site naming that dependency.)
2. Add the 2-D rotation from vector `u` to vector `w`, in the book's form (`book/docs/proof-rotate-from-a-to-b.rst`):
   `cos = (u_1 w_1 + u_2 w_2)/(|u||w|)`, `sin = (u_1 w_2 - u_2 w_1)/(|u||w|)`, applied as
   `cos * v + sin * v.rotate_90_degrees()`, on `g2.Vector`s. Zero rule through the shared guard
   `MultiVectorBase.require_rotation_endpoints`: `u = w = 0` is the identity, one of them zero raises.
3. Rewrite `_project_via_standard_position` the mvp `6347afa3` way: for each plane, copy the two
   coordinates into a 2-D vector, rotate it there with step 2, and write them back with the third
   coordinate untouched. Align: the (x, y) shadow of `b` onto `|shadow| * e_1`, then the (x, z) pair
   onto `|b| * e_1`; keep the x-coordinate; rotate back with from/to swapped, in reverse order. For
   `b = b_z e_3` the first step is 0 → 0, the identity. Drop the e_3 `ValueError`; its doctest becomes
   `project_sp(a, 1 * e_3) == a.projected_onto(e_3)`. Check the import: `standardposition` would then
   import `gacalc.g2`; confirm `g2` does not import `standardposition` (no cycle).
4. Lean (`proofs/GacalcProofs/StandardPosition.lean`): restate `rotXY`/`rotXZ` through the 2-D
   `rotPlane` of `proofs/GacalcProofs/RotateFromTo2D.lean` (or a `rot90` there, if it lacks one) on the
   copied coordinate pair, and prove the new form equal to the old by `ext; simp; ring`, so the existing
   theorems keep their proofs. Add the 0 → 0 branch to `projectSP` and extend `projectSP_eq_proj` to
   the e_3 axis.
5. Docs: module docstring (no e_3 restriction; the scalar-times-vector form; cite `eq-rotate-formula`),
   `tasks/reference/reduction-to-standard-position.md`, `book/docs/proof-projection-3d.rst` if it
   quotes the old restriction, CHANGELOG `[Unreleased]` (behavior change: `project_sp`/`reject_sp`
   no longer raise for `b` along `e_3`).

## Decisions

- The rotation inside `project_sp` is built **from coordinates**, not from `projection_rotation`,
  which keeps the non-circular bootstrap and the Lean proof (William Emerison Six
  <billsix@gmail.com>, 2026-11-10).
- Each plane rotation is written **as a sum of scalars times vectors**, `cos * v + sin *
  rotate_90_degrees(v)` (plus the untouched axis part), following the book (`eq-rotate-formula` in
  `book/docs/proof-rotate.rst`) and its history, not the expanded per-coordinate formulas the
  current code uses; this needs a `rotate_90_degrees` that turns its input vector 90° (William
  Emerison Six <billsix@gmail.com>, 2026-11-10).
- The zero-vector rule (0 → 0 is the identity, 0 → nonzero and nonzero → 0 raise `ValueError`) applies to **all the public rotation factories** too (William Emerison Six <billsix@gmail.com>, 2026-11-10). That part does not depend on the hold, so it was split into `tasks/rotation-factories-zero-vector-rule.md`.
- The quarter turn is the existing elementary method `g2.Vector.rotate_90_degrees()`: 𝒢₂ is used to
  bootstrap the 3-D plane rotations, each copying its coordinate pair into a `g2.Vector`, rotating
  there and writing back, as modelviewprojection's `6347afa3` did with `Vertex2D` (William Emerison
  Six <billsix@gmail.com>, 2026-11-10).
