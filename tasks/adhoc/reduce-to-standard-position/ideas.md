# Reduction-to-standard-position — repo scan → ideas list (2026-09-30)

Where the standard-position (frame-reduction) theme could be applied, one line of "why it helps"
each. Raw grep hits: `data/scan.txt`. Decisions are recorded in
`tasks/reduce-to-standard-position.md`. **Pass 1 scope was project + reject.** Items marked DONE
landed this pass; the rest remain as future ideas. (The Lean was built with elementary
coordinate-plane rotations, not versors — see the task doc's History section.)

## LEAN (`proofs/GacalcProofs/`) — done

- **L1 (DONE — elementary):** `StandardPosition.lean` — `rotXY`/`rotXZ` (rotate the two in-plane
  components, keep the perpendicular one — no versors), `rotXY_preserves_dot`/`rotXZ_preserves_dot`
  (orthogonal when `cos²+sin²=1`), and `proj_rotXY_equivariant`/`proj_rotXZ_equivariant`/
  `vecReject_rotXY_equivariant`: projection/rejection commute with a plane rotation — the general
  justification of "rotate to standard position, project/reject, rotate back".
- **L2 (DONE — elementary):** the explicit alignment `rotXY_aligns_xy`→`rotXZ_aligns_xz`→
  `rotate_b_to_e1` (sends `b` to `|b|·e₁` by composing the two plane rotations), plus
  `rotate_b_to_e1_magnitude` (stated via the actual `magnitude`). This is the concrete "rotate to
  standard position" a student sees, done with high-school 2D rotations only.
- **L3 (DONE, `5395912`):** `mul_eq_proj_dot_add_reject_wedge` — the vector geometric product
  `ab = a·b + a∧b` reconstructed from `project`+`reject` (`mul_proj_eq_dot` for the dot half,
  `plane_eq_wedge` for the wedge half). The maintainer's "project/reject build the product" payoff.
  Versor-free.
- **Python (DONE):** `src/gacalc/standardposition.py` `project_sp`/`reject_sp` — the same elementary
  rotations, asserted equal to canonical in `tests/test_standardposition.py`.

## BOOK (`book/docs/`) — the maintainer says this already does reduce-to-coordinates BEST

- **B1 (DRAFTED 2026-09-30 — maintainer to refine voice):** `book/docs/proof-projection.rst` (the
  narrative proof, voice modelled on `proof-rotate.rst`) + `book/docs/notebooks/proof-projection.py`
  (the calculation notebook using `project_sp`), both registered in `projection.rst`'s toctree. Drafted
  from the modelviewprojection-book voice guide. Figure placeholders left as `.. TODO figure` (no SVGs
  invented). *Remaining:* the maintainer's voice pass + real figures + `make docs` build check.
- **B2:** `book/docs/projection-rejection-3d.rst` + `.../notebooks/projection-rejection-3d.py` — show
  the 3D case by the literal e₁-alignment chain (project onto a plane, 2D-rotate, rotate back). *Why:*
  this is exactly the maintainer's described method; the book is where a student "verifies not derives".
- **B3:** `book/docs/rotate.rst` already teaches 2D rotation — cross-reference it as the trusted
  building block the standard-position chain reduces to. *Why:* names the "already known to work" 2D op.

## CODE (`src/gacalc/`) — duplicate primed defs

- **C1 (DONE):** `project_sp`/`reject_sp` in `src/gacalc/standardposition.py` — the
  rotate-project-rotate-back construction (elementary rotations), with `tests/test_standardposition.py`
  asserting equality to the canonical `projected_onto`/`rejected_away_from`.
- **C2:** `vectorcalc.py:34` `cross` and `base.py:1629` — a standard-position `cross` (reduce to the
  2D-known `Rotate2D90`-style step) is the direct analogue of `multivariate-math/crossproduct.tex`.
  *Why:* it's the exact operation the LaTeX archetype bootstraps; natural once project/reject exist.
  (Out of Pass-1 scope, but the most faithful port of the inspiration.)

## NOTEBOOKS (`notebooks/`) — the show_mult-style verification

- **N1:** a `notebooks/`-side demo pairing `show_mult` with the standard-position projection so a
  student watches `a` rotate to standard position, the projection happen trivially, and rotate back —
  tied to the proof-notebook methodology task (`reference-doc-lean-workflow-and-proof-notebooks.md`).
  *Why:* the "verify not derive" payoff; also exercises the `\underbrace` cancellation-display idea.

## Cross-cutting

- **X1 (DONE):** the `CLAUDE.md` pointer noting primed standard-position defs are an accepted duplicate
  alongside the canonical Hestenes ones (mirrors the duplicate-`rotate` carve-out).
- **X2 (DONE):** the reference doc `tasks/reference/reduction-to-standard-position.md` — the theme, the
  `crossproduct.tex` archetype, the non-circularity argument, the prime convention.
