# Present student-facing facts in sine/cosine, not dot/wedge (Lean proofs + Python)

**Status:** done. **Priority:** 5. **Difficulty:** 5.
**Completed:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).
**Durable knowledge harvested to:** `CLAUDE.md` › "Presenting to students" and "Coordinates only when
needed"; `tasks/reference/lean-ga-proof-architecture.md` (naming, the nonzero-guard convention, the
`0/0` rationale). **Follow-ups:** `tasks/archive/2026/10/09/prefer-sine-cosine-presentation-followups.md` (deferred Lean
candidates, maintainer to review), `tasks/lean-cross-standard-position-capstone.md`.

## What this was

Establish and apply the principle: when a result is **shown to a student** (a Lean proof's stated
form, a Python docstring, a notebook, the book), prefer the **sine/cosine-of-the-angle** phrasing over
raw **dot/wedge** where a faithful option exists — "perpendicular ⇒ cos = 0", "parallel ⇒ sin = 0",
"area = |a||b| sin θ" are what a geometry/trig student can picture. The dot/wedge form stays the
**primitive**; the trig form is layered on top. Recorded as a standing rule in `CLAUDE.md`.

## What was done

**Lean — `proofs/GacalcProofs/StudentTrigForms.lean` (new).** The student-facing trig theorems,
collected in one file (because `cos_between`/`sin_between` sit high in the import graph, so a corollary
beside its primitive would cycle):
- Perpendicular → `cos = 0`: `dual_perp`, `reject_perp` (G2 and G3), `cross_perp_left`/`_right`,
  `dual_wedge_perp_left`/`_right`, `proj_plane_perp_normal`.
- Parallel → `sin = 0`: `parallel_smul`.
- Area → `|a||b| sin θ`: `area_eq_mag_mul_sin`.
Each is **named for the geometry** (cosine is an implementation detail — no `_cos`/`_sin` suffix),
**stated over objects** (`{a b : G3}` + `IsVector`, not coefficient tuples), **nonzero-guarded**
(`normSq ≠ 0`, which makes `cos = 0 ⟺ dot = 0` — excluding the meaningless `0/0` case so the trig form
is as strong as the primitive), and **proved by citing an object-level `_dot`/wedge helper**
(`dual_perp_dot`, `reject_perp_dot`, `cross_perp_left_dot`, `dual_wedge_perp_left_dot`,
`wedge_parallel_smul`, `proj_plane_perp_normal_dot`). Those helpers were lifted from their original
coordinate-tuple forms to object-level in their home files (`Predicates2D`, `Projection2D`,
`Projection3D`, `Cross`, `Predicates3D`).

**Python — raise on a zero operand (breaking change).** The angle-based methods `cosine`, `abs_sin`,
`is_orthogonal_to`, `is_parallel_to` (`base.py`), the generated `g2.Vector.sine`
(`tools/gen_specialized.py`), and `nbplotutils.sine` now raise a clear `ValueError` for a zero vector
(the angle is undefined) instead of returning `0/0` junk or a bare `ZeroDivisionError`. The
**implementations stay on the robust dot/wedge primitive** — reimplementing a predicate as `cos == 0`
would reintroduce the `0/0` fragility — and the student-facing phrasing was added to the docstrings
(leading with cosine/sine, cross-referencing `cosine`/`abs_sin`). `test_signed_sine` updated to expect
`ValueError`; `CHANGELOG.md` `[Unreleased]` records the breaking change. `area`/`volume` are
unaffected (no division; a degenerate measure of 0 is meaningful).

**Notebooks + book:** inventoried — the student-facing material already largely prefers sin/cos
(`notebooks/displayg2.py`, `book/docs/notebooks/levels-of-abstraction.py`, `proof-rotate.rst`), so the
library docstrings were the lagging surface (now fixed). Sin/cos-first writing of book *placeholders*
belongs in the book's voice pass, not a mirror of existing text.

**Audit (did every dot-compared-to-zero caller get rewired?):** yes — in Python the only
`inner_product == zero` is inside `is_orthogonal_to` itself; in Lean the `dot … = 0` occurrences are
the perp theorems' own statements, the deferred hypothesis-side premises, or steps already wired
through `reject_perp_dot`.

## Verification

`make lean` green (`StudentTrigForms` + the lifted helpers build, no `sorry`/`admit`); 672 pytest
pass; `ruff` + `ty` clean (generator regenerates deterministically with the `sine` guard).
