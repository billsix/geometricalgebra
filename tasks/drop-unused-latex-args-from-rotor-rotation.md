# Drop the unused `latex_repr` args from `rotor_rotation` (inline the known string)

**Status:** proposed — needs go-ahead
**Created:** 2026-07-16

## Goal

`rotor_rotation(from, to, *, latex_repr="R", latex_repr_inv="R^{-1}", interpolate=None)`
(in `src/gacalc/transforms.py`) exposes `latex_repr` / `latex_repr_inv` as parameters, but
**no caller ever overrides them** — every call site uses the defaults. The right LaTeX string
is already known (`R` / `R^{-1}`), so it belongs *inline in the function body*, not as a
parameter the API has to carry and document. Remove the two `latex_repr*` parameters from
`rotor_rotation` and hardcode `"R"` / `"R^{-1}"` where it constructs the `InvertibleFunction`.

## Scope — this is `rotor_rotation` only, NOT `plane_rotation`

The two rotation factories look similar but their LaTeX params have opposite status:

| function | latex params | actually overridden by a caller? |
| --- | --- | --- |
| `rotor_rotation` | `latex_repr: str = "R"`, `latex_repr_inv: str = "R^{-1}"` | **No** — dead. gacalc tests call it positionally (`rotor_rotation(v, to)`); mvp never calls it. |
| `plane_rotation` | `latex_repr: Callable\|None`, `latex_repr_inv: Callable\|None` | **Yes — keep.** mvp brands its rotations `RX_`/`RY_`/`RZ_`/`R_` (`modelviewprojection/.../mathutils.py:115–186`); `tests/test_plane_rotation.py:161–166` asserts on custom labels. |

So the cleanup applies cleanly to `rotor_rotation`. `plane_rotation`'s callable labels are a real,
used feature (a facade branding per-axis rotations) — leave them.

## Plan

- [ ] Remove `latex_repr` / `latex_repr_inv` params from `rotor_rotation`'s signature.
- [ ] In the `InvertibleFunction(...)` construction (transforms.py ~L488–495), pass the
      literals `"R"` and `"R^{-1}"` directly.
- [ ] Update the docstring line "``latex_repr`` / ``interpolate`` let a caller ... label the
      function ..." — drop the `latex_repr` half (keep the `interpolate` note).
- [ ] Grep-confirm no caller passes `latex_repr=`/`latex_repr_inv=` to `rotor_rotation`
      (gacalc: `tests/test_transforms.py`, `tests/test_numeric_magnitude.py`; and mvp) — verified
      none do at task-creation time, re-verify before editing.
- [ ] Run `make test` (or host `pytest -q` after `make generate`) + `ruff`/`ty` clean.

## Notes / decisions

- **`interpolate` param** is *also* never overridden by any caller today — same "dead parameter"
  smell. But it's a different kind of knob (an interpolation law, not a display string) and the
  user's request was specifically the LaTeX string. Flagging it here; **out of scope unless Bill
  says otherwise** (see open question).

## Open questions

- Also drop `rotor_rotation`'s unused `interpolate` param in the same pass, or leave it?
- Confirm the inlined strings should stay exactly `"R"` / `"R^{-1}"` (the current defaults).
