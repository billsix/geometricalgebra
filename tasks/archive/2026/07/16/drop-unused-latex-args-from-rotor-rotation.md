# Drop the unused `latex_repr` args from `rotor_rotation` (inline the known string)

**Created:** 2026-07-16 · **Completed:** 2026-07-16

`rotor_rotation(from, to, *, latex_repr="R", latex_repr_inv="R^{-1}", interpolate=None)` (in
`src/gacalc/transforms.py`) exposed `latex_repr` / `latex_repr_inv` parameters that **no caller ever
overrode**. The known strings `R` / `R^{-1}` were moved inline into the function body.

## Scope — `rotor_rotation` only, NOT `plane_rotation`

The two rotation factories looked alike but their LaTeX params had opposite status:

| function | latex params | overridden by a caller? |
| --- | --- | --- |
| `rotor_rotation` | `latex_repr: str = "R"`, `latex_repr_inv: str = "R^{-1}"` | **No** — dead. gacalc tests call it positionally; mvp never calls it. |
| `plane_rotation` | `latex_repr: Callable\|None`, `latex_repr_inv: Callable\|None` | **Yes — kept.** mvp brands its rotations `RX_`/`RY_`/`RZ_`/`R_` (its `mathutils.py`); `tests/test_plane_rotation.py` asserts on custom labels. |

## What was done

- The `latex_repr` / `latex_repr_inv` params were removed; the signature became
  `from_vector, to_vector, *, interpolate`.
- The `InvertibleFunction(...)` construction passes the literals `"R"` / `"R^{-1}"` (the previous
  defaults, unchanged).
- The docstring states the label is fixed as `R` / `R^{-1}` and keeps the `interpolate` note.
- No caller passed `latex_repr=`/`latex_repr_inv=` (gacalc and mvp both checked). No generated code
  and no mvp change.

## Decisions

- **`interpolate`** was also never overridden by any caller — the same dead-parameter smell — but it is
  a different kind of knob (an interpolation law, not a display string), and the request was
  specifically the LaTeX string. It was left in place; whether to drop it was raised with the
  maintainer and left unanswered.

## Verification

`pytest -q`: **281 passed**; ruff/ty clean. `latex_repr == "R"` and `latex_repr_inv == "R^{-1}"`
still rendered at runtime.
