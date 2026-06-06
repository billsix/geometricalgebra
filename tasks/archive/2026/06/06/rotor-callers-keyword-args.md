# Call rotor/rotation methods with keyword arguments (self-documenting call sites)

**Status:** complete
**Completed:** 2026-06-06
**Started:** 2026-06-06

> **Done (2026-06-06).** Converted all positional `rotor_from_vectors(...)` and `rotate(...)` call
> sites to keyword form (`from_vector=…, to_vector=…`): `test_graded.py` (rotor ×4 + rotate ×4),
> `test_conformance.py` (rotate ×2), and the three notebooks (`displayg2.py`, `displaymv.py`,
> `displaygraded.py`). No rename, no signature change, no regen. `ty`/`ruff` clean, 161 tests pass.
> The `create_rotor` rename stays declined (the keyword call style gives the from/to readability).

## Goal

The methods already have well-named parameters — `rotor_from_vectors(from_vector, to_vector)`
and `rotate(from_vector, to_vector)`. The only problem is that some **call sites pass them
positionally**, which hides which argument is the "from" and which is the "to":

```python
R = MultiVector.rotor_from_vectors(e_1, to)          # which is which?
```

Fix: call them with **keyword arguments**, so the geometry reads off the call:

```python
R = MultiVector.rotor_from_vectors(from_vector=e_1, to_vector=to)
```

**No rename, no new parameters, no Python-keyword games** — purely a call-site readability
change. (This supersedes an earlier over-scoped idea to rename to `create_rotor` /
`create_rotor(from=…)`; `from` is reserved and the params already say from/to.)

## Scope — positional call sites to convert to keyword form

`rotor_from_vectors(...)`:
- `notebooks/displayg2.py` — `G2.rotor_from_vectors(e_1, to)` (the helper added this session)
- `notebooks/displaymv.py` — `MultiVector.rotor_from_vectors(e_1, to)`
- `notebooks/displaygraded.py` — `Vector2.rotor_from_vectors(frm, to)`
- `tests/test_graded.py` — `Gn.rotor_from_vectors(frm, to)` ×2, `Vector2.rotor_from_vectors(...)`,
  `Vector3.rotor_from_vectors(...)` (lines ~241, 251, 259, 266, 274)

`rotate(...)` (same from/to signature — convert for consistency):
- `tests/test_graded.py` — `Gn.rotate(frm, to)` ×2, `Vector2.rotate(f2, t2)`, `Vector3.rotate(f3, t3)`
- `tests/test_conformance.py` — `cls.rotate(...)`, `Gn.rotate(e_1, e_2)`
- `notebooks/displaygraded.py` — `Vector2.rotate(frm, to)`
- `tests/test_multivector.py` — **already keyword** (`MultiVector.rotate(from_vector=e_1,
  to_vector=e_2)`); leave as the model.

Not touched: the method **definitions** in `base.py` (params are already well-named); no
generated code (`rotor_from_vectors`/`rotate` are inherited, not emitted); `plane_of_rotation`
(no args).

## Plan

- [ ] Convert the positional `rotor_from_vectors(...)` calls above to
      `from_vector=…, to_vector=…`.
- [ ] Convert the positional `rotate(...)` calls likewise (consistency with `test_multivector`).
- [ ] `python -m pytest -q` (expect 161) + `entrypoint/format.sh` (ruff + ty clean). No regen.

## Notes / decisions

- Pure readability; no behavior change, no signature change, no new tests.
- Trivial enough to be a single edit pass — kept as a task only because the author asked to track
  it and prioritize it.

## Open questions

- Any appetite for *also* renaming the method (`rotor_from_vectors` → `create_rotor`) as a separate
  aesthetic change? Current read: **no** — the keyword-argument call style already gives the
  desired `from…/to…` readability. (Left here only so the earlier idea is recorded as declined.)
