# Standard-position project/reject: defined on the e_3 axis, built from 2-D vector-to-vector rotations

**Done:** 2026-11-14. **Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>).
**Branch:** `sp-e3-axis-and-scalar-typing`. Durable knowledge:
`tasks/reference/reduction-to-standard-position.md` ("Each plane rotation is the book's 2-D rotation
on a copied coordinate pair", "The `e₃` axis").

## Outcome

`project_sp` / `reject_sp` (`src/gacalc/standardposition.py`) are now defined for every nonzero `b`,
the `e_3` axis included: `project_sp(a, 1 * e_3) == a.projected_onto(e_3)` is a doctest. Each plane
rotation copies its plane's coordinate pair into a `g2.Vector`, rotates it there with the book's blend
`cos * v + sin * v.rotate_90_degrees()` (`eq-rotate-formula`, `book/docs/proof-rotate.rst`), and
writes the pair back, as modelviewprojection's `6347afa3` did with `Vertex2D`. The Lean transcription
follows the same shape, and `projectSP_eq_proj` now needs only `b ≠ 0`.

## What changed

- **Python.** A private `_rotation_from_to(u, w)` builds the 2-D rotation from `u`'s direction to
  `w`'s, with `cos`/`sin` read off coordinates as in `book/docs/proof-rotate-from-a-to-b.rst` and the
  zero-vector rule through `MultiVectorBase.require_rotation_endpoints` (0 → 0 is the identity, 0 →
  nonzero raises); its docstring doctests all three cases. `_project_via_standard_position` aligns the
  xy shadow of `b` onto `|shadow| * e_1`, then the `(|shadow|, b_z)` pair onto `|b| * e_1`, keeps the
  x-coordinate, and rotates back with from/to swapped in reverse order. The `e_3` `ValueError` and its
  two tests became equality tests (numeric, negative and symbolic `b_3`). The expanded-component
  formulas are gone. A comment at the quarter-turn call names the dependency on
  `rotate_90_degrees` being a coordinate swap, not a product with `e_12`.
- **Book notebook.** `book/docs/notebooks/proof-cross.py`'s `rotate_xy`/`rotate_xz`/`rotate_yz` copy
  their pair into a `g2.Vector` and blend through one `rotate_2d(cos, sin, v)`; the symbolic check
  still gives `[0, 0, 0]`.
- **Lean.** `StandardPosition2D.lean` gained `rot90` (the coordinate quarter turn) and
  `rotPlane_vec_eq_blend` (`rotPlane c s (vec x y) = c*v + s*rot90 v`). `rotXY`/`rotXZ`
  (`StandardPosition.lean`) and `rotYZ` (`CrossStandardPosition.lean`) are defined through
  `GacalcProofs.G2.rotPlane` on the copied pair; their component forms are kept as `rfl` lemmas
  `rotXY_apply`/`rotXZ_apply`/`rotYZ_apply`, which replaced the definitions in every `simp only`, so
  the existing proofs kept their structure. The xy alignment reads `(xyCos b, xySin b)`, which is
  `(1, 0)` when the shadow is zero; `rotXY_aligns_xy_SP` covers both cases, and `cs_xy_unit`,
  `unalignSP_alignSP`, `alignSP_self`, `projectSP_eq_proj`, `rejectSP_eq_vecReject` and
  `rejectSP_eq_reject` dropped their `xyMagnitude b ≠ 0` hypothesis.
- **Docs.** `CHANGELOG.md` `[Unreleased]` › Changed; `tasks/reference/reduction-to-standard-position.md`;
  `tasks/reference/lean-ga-proof-architecture.md` (the coverage row). `book/docs/proof-projection-3d.rst`
  never stated the restriction, so it needed no change.

## Decisions

- **A zero `b` raises `ValueError`** ("cannot project onto the zero vector"). Without the old `e_3`
  error, `b = 0` would make every rotation zero-to-zero and return `a`'s x-component, a wrong answer.
- **`rotYZ` was converted too**, though the plan named only `rotXY`/`rotXZ`, because the notebook's
  `rotate_yz` changed with the other two and the three Lean rotations should read alike.
- **The 2-D blend is spelled `g2.Scalar(cos) * v`**, as `g2.Vector.rotate` already does, so pyright
  types it as a `Vector` (`tasks/reference/pyright-sympy-coefficient-typing.md`).
- **`rot90` and the blend theorem live in `StandardPosition2D.lean`**, beside `rotPlane`, not in
  `RotateFromTo2D.lean` as the plan suggested: `StandardPosition.lean` then imports only the file that
  defines the rotation.
- **Lean's zero branch is an `if` on the cosine/sine** (`xyCos`/`xySin`) rather than a Lean twin of
  `_rotation_from_to`: the identity is `rotPlane 1 0`, so one definition covers both cases and every
  existing lemma about `rotXY c s` still applies.

## Verification

- `make test`'s pytest run (against the existing image): 1676 passed, 2 skipped.
- `make format` (ruff, `ty check` over `src`/`tests`/`tools`/`book/docs/notebooks`, the changelog
  guard): clean.
- `proofs/check.sh` (what `make lean` runs): build OK, no `sorry`, 1051 declarations on the standard
  axioms. The `ring_nf` info at `CrossStandardPosition.lean` `cross_reduced` predates this work.
