# Call rotor/rotation methods with keyword arguments (self-documenting call sites)

**Created:** 2026-06-06 · **Completed:** 2026-06-06

`rotor_from_vectors(from_vector, to_vector)` and `rotate(from_vector, to_vector)` already had
well-named parameters, but several call sites passed them positionally
(`MultiVector.rotor_from_vectors(e_1, to)`), hiding which argument is "from" and which is "to".
Every positional call was converted to keyword form
(`rotor_from_vectors(from_vector=e_1, to_vector=to)`). This was a call-site readability change
only: no rename, no signature change, no new tests, no regen. It was tracked as a task because the
author asked for it.

## Decisions

- **Renaming to `create_rotor` was declined.** An earlier, over-scoped idea was to rename to
  `create_rotor` / `create_rotor(from=…)`; `from` is a reserved word, and the keyword call style
  already gives the from/to readability.
- `rotate(...)` calls were converted too, for consistency with `tests/test_multivector.py`, which
  already used keywords and served as the model.
- Not touched: the method definitions in `base.py`, generated code (both methods are inherited, not
  emitted), and `plane_of_rotation` (no arguments).

## What changed

`tests/test_graded.py` (`rotor_from_vectors` ×4, `rotate` ×4), `tests/test_conformance.py`
(`rotate` ×2), and the notebooks `displayg2.py`, `displaymv.py` and `displaygraded.py`.

## Verification

`ty`/`ruff` clean; 161 tests pass.
