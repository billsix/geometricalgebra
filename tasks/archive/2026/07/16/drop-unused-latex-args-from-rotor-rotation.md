# Drop the unused `latex_repr` args from `rotor_rotation` (inline the known string)

**Status:** complete
**Completed:** 2026-07-16
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

- [x] Removed `latex_repr` / `latex_repr_inv` params from `rotor_rotation`'s signature (now
      `from_vector, to_vector, *, interpolate`).
- [x] `InvertibleFunction(...)` construction passes the literals `"R"` / `"R^{-1}"` directly.
- [x] Updated the docstring — states the label is fixed as `R` / `R^{-1}`, keeps the `interpolate`
      note.
- [x] Re-verified no caller passes `latex_repr=`/`latex_repr_inv=` (gacalc + mvp both clean; mvp
      never calls `rotor_rotation` at all).
- [x] `pytest -q` → **281 passed**; `ruff`/`ty` clean. Confirmed `latex_repr == "R"`,
      `latex_repr_inv == "R^{-1}"` still render at runtime.

## Outcome

`interpolate` left in place per scope (its own open question below, untouched). No generated
code, no mvp change.

## Notes / decisions

- **`interpolate` param** is *also* never overridden by any caller today — same "dead parameter"
  smell. But it's a different kind of knob (an interpolation law, not a display string) and the
  user's request was specifically the LaTeX string. Flagging it here; **out of scope unless Bill
  says otherwise** (see open question).

## Open questions

- Also drop `rotor_rotation`'s unused `interpolate` param in the same pass, or leave it?
- Confirm the inlined strings should stay exactly `"R"` / `"R^{-1}"` (the current defaults).
