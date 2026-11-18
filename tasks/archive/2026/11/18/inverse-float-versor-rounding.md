# `inverse()` rejects a float versor because of rounding, so 3D float `versor_rotation` crashes

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; overnight batch
`overnight-batch-2026-11-18`)
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-18 (found while writing `tests/test_frame_svd.py` for
`tasks/archive/2026/11/18/frame-svd-investigation.md`)

## Outcome

`MultiVectorBase.inverse` (`src/gacalc/base.py`) used to raise `RuntimeError` unless `Ã * A` was
exactly a scalar. A 𝒢₃ versor built from float vectors has `Ã * A` = scalar + about 1e-16 on a
bivector blade, so `versor_rotation(from_vector=a, to_vector=b)` crashed on ordinary float 3D
vectors.

The gate now also accepts `_is_scalar_up_to_rounding(Ã * A)`, a new module-level helper in
`base.py`. It returns `True` only when:
- some coefficient is inexact (a Python `float` or a sympy `Float`);
- the scalar part is nonzero;
- every other coefficient is at most `_SCALAR_RESIDUE_REL_TOL = 1e-9` times the scalar part.

The tolerance is relative, because the scalar is `|A|²` and grows with the vectors. Exact input
never takes this path, a symbolic coefficient beside float ones returns `False`, and a genuinely
mixed-grade float element still raises. The inverse returned is unchanged, `Ã / |A|²`.

- **Tests:** `tests/test_inverse_float_versor.py` (4):
  - the float versor inverts (`R * R⁻¹ ≈ 1`);
  - `versor_rotation` on float 3D vectors rotates and round-trips;
  - float scalar + vector still raises;
  - exact input keeps exact coefficients.

  The helper's doctests cover the residue, a real bivector part, exact input and a mixed symbolic
  coefficient.
- **The SVD test's workaround is gone.** `tests/test_frame_svd.py`'s route 1 builds Q from
  `versor_rotation` again, instead of `projection_rotation` wrapped in an `InvertibleFunction`.
- **`CHANGELOG.md`:** `[Unreleased]` › Fixed.

## Judgment calls

- **sympy `Float` counts as inexact.** The first version checked only for Python `float`, and the
  SVD test still failed. `Frame.orthonormal_vectors()` returns sympy `Float` coefficients for
  Python-float input, because the orthogonalization routes through sympy. That is an observation,
  not a bug fixed here. It bears on `tasks/tolerance-from-coefficient-type.md`, whose "is this float
  input?" check must treat sympy `Float` the same way.
- **The helper is local to `base.py` for now.** `tasks/tolerance-from-coefficient-type.md` plans to
  move `frame._has_float` to `base.py` as the one shared check; this helper can use it then.

## Verification

- ruff and `ty check` were clean on `base.py` and the tests.
- `base.py` doctests, the new tests and `tests/test_frame_svd.py` passed.
- The host fast suite passed: 1891 passed, 2 skipped (GL modules excluded on the host, since the GL
  packages are not installed there).
- The batch's container gate at the end covers the GL modules.
