# Step 2: ePiX figures for projection and rejection in 2D — the result and the derivation

**Created:** 2026-10-07 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-10-07 (overnight autonomous run)
**Part of:** `tasks/archive/2026/10/07/book-epix-figures.md` · **Depends on:** step 1 (`_scene2d.py`) ·
**Next:** `tasks/archive/2026/10/07/book-epix-figures-step-3-projection-3d.md`

Two figure sets for the projection pages: (a) the result — `project(a, b)` as the shadow of `a` on the
line through `b`, `reject(a, b)` as the perpendicular remainder, `a = project + reject` — for
`book/docs/projection.rst`; (b) the precalculus derivation for `book/docs/proof-projection.rst` (rotate
the picture so `b` lies on the x-axis, read the projection off as the x-coordinate and the rejection as
the y-coordinate, rotate back), filling that page's two `.. TODO figure` markers. The math is
`src/gacalc/standardposition.py` (`project_sp`/`reject_sp`), proved in
`proofs/GacalcProofs/StandardPosition.lean` and `Projection2D.lean`; reference:
`tasks/reference/reduction-to-standard-position.md`.

## What was done

- Result figures: `proj1` (a, b, dashed line through b, foot of the perpendicular), `proj2`
  (projection blue along b + rejection green perpendicular, right-angle marker, labelled
  `proj_b a` / `rej_b a`), `proj3` (a = proj + rej tip-to-tail).
- Derivation figures `sp1`–`sp5`: goal → rotation angle φ marked → rotated so b is on the x-axis (faint
  dashed originals) → projection = x-coordinate, rejection = y-coordinate (right angle) → rotated back.
  Shared vectors live in `_projection_scene.py`; `right_angle_at` was added to `_scene2d.py` for a
  right-angle marker at an arbitrary corner.
- `projection.rst` (proj1–3) and `proof-projection.rst` (sp1 at the first TODO marker, sp2+sp3 at the
  second, sp4+sp5 in "Now the algebra") were wired with alt text; `.. TODO prose` was left for the
  maintainer. The pre-existing `Title underline too short` warning in `proof-projection.rst` was fixed.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-07)

- The **2D** derivation was drawn here. The page's prose (an agent draft of 2026-09-30) is still
  3D-framed ("one plane at a time": xy then xz), so a `.. TODO prose` note near the top of
  `proof-projection.rst` flags the 2D-then-3D restructuring as the maintainer's; the 3D pictures belong
  to step 3's follow-on.
- Vectors: `a` is the rotation sequence's (1.25 at 66°), `b` = 1 at 20°; the projection scalar is
  ≈ 0.868, so in standard position a′ is at 46° and its x-coordinate is the projection.

## Verification

Figures rendered; the `make format` gate was green; the Sphinx HTML build had **no warnings** and
embedded all 8 PNGs. The full html+PDF build ran at the end of step 3.
