# Prove 2D rotation is distributive (linear): prose + Lean (+ the symbolic Python form)

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 4
**Difficulty:** 4
**Started:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Proved that 2D rotation is **distributive / linear** — `R(u + v) = R(u) + R(v)` and `R(k·v) = k·R(v)`
— in all three forms, so a rotation is fixed by what it does to the two natural-basis vectors
(`R(v) = v₁ R(e₁) + v₂ R(e₂)`). Lean: three theorems in `Rotation2D.lean` (`make lean` green). Prose: a
"Rotation is distributive" section in `geometric-product.rst` citing them. Python: a check in the book
notebook and a permanent test (`make test` green). All gates green.

## What was done

- **Lean** (`proofs/GacalcProofs/Rotation2D.lean`): added `rot_add_vec`
  (`rot θ (u + v) = rot θ u + rot θ v`), `rot_smul` (`rot θ (k • v) = k • rot θ v`), and the payoff
  `rot_basis_decomp` (`rot θ v = v.c1 • rot θ e₁ + v.c2 • rot θ e₂`). Each is `simp only [rot, G2.add /
  G2.smul / …, G2.vec]; ext <;> ring` — the coordinate map is linear in `c1`/`c2`. `proofs/check.sh`
  green (no sorry/admit).
- **Prose** (`book/docs/geometric-product.rst`): a "Rotation is distributive" section right after the
  rotor is introduced — `(u + v) * R = u * R + v * R` (labelled `eq-rotation-distributive`), then
  distributing over the natural basis to `v * R = v₁ (e₁ * R) + v₂ (e₂ * R)`, ending on "a rotation is
  determined by what it does to e₁ and e₂" (the hook for the graph-paper picture). Cites the Lean
  theorem names.
- **Python** (`book/docs/notebooks/geometric-product.py`): cells checking `(a + b) * R == a * R + b * R`
  and the basis decomposition symbolically (both simplify to the zero vector). Plus a permanent
  assertion test `test_rotation_is_distributive_over_addition_symbolic_2d` in
  `tests/test_plane_rotation.py`.

## Decisions

- **Placement:** in `geometric-product.rst`, where rotation becomes "multiply by `R`", because the
  distributivity argument is one line from there (the geometric product distributes over `+`); this
  reads better than a separate page.
- **Three forms:** the maintainer asked for prose + Lean; per the project's "three forms" standing rule
  I added the symbolic Python (notebook cell + test), so the result ships complete.

## Verification

`make lean` (no sorry/admit), `make test` (698 passed, +1), `make format` (ruff/ty clean), `make docs`
(HTML + PDF; the section and numbered equation render, the notebook's distributivity cells execute).

## Open questions

None.
