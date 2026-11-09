# Make the 2D-only transforms clearly 2D-only to users

**Created:** 2026-06-05 · **Completed:** 2026-06-06
**Superseded:** `rotate_90_degrees` came back, 𝒢₂-only, on 2026-09-06 (see `tasks/archive/2026/09/06/add-quarter-turn-to-g2.md`).

Some `InvertibleFunction` factories in `src/geometricalgebra/transforms.py` were inherently planar
(e₁e₂ plane only), yet nothing stopped a user from applying them to a `G3`/`Gn` vector with an e₃
component, which silently produced a wrong, mixed-grade result. The task was resolved by
**removing** the planar transforms rather than guarding them.

## Findings (2026-06-05)

- **Dimension-general** (correct in any n): `translate`, `uniform_scale`, `scale_non_uniform`,
  `compose`, `inverse`, `identity`.
- **Inherently 2D:** `rotate_90_degrees`, `rotate`, `rotate_around`, `scale_non_uniform_2d` (two
  factors only; silently drops e₃⁺), and `is_clockwise`/`is_counter_clockwise` (which already
  asserted planar input).
- The hazard was correctness: `rotate(θ)` on a vector with an e₃ part turns e₃ into the trivector
  e₁e₂e₃ (`v * e₁e₂`).
- **Types cannot solve it** (the maintainer's intuition, confirmed): `Gn` is one type for every
  dimension, so a checker cannot tell 2D `Gn` from 3D `Gn`. Restricting `rotate` to
  `InvertibleFunction[G2]` would defeat the representation-preserving design, force `transforms.py`
  to import a concrete class (breaking its `base`-only layering), and still not constrain `Gn`.

## Options considered

- **A. Runtime planarity guard** at apply time — the only option that protected a `Gn` user; was the
  recommendation, together with B.
- **B. Clearer naming** (`rotate_in_e1e2_plane`, …) — documents only, churns the API.
- **C. Generic `InvertibleFunction[T]`** — rejected: does not help `Gn` and breaks layering.
- **D. Docstring-only** — already partly in place; no enforcement.

## Decision (the author, 2026-06-06): remove them

These factories were modelviewprojection artifacts, and geometric-algebra rotation was already
covered by the rotor (`AbstractMultiVector.rotate(from, to)` / `rotor_from_vectors`), so the planar
factories carried no GA-teaching weight. Removing them made the mis-transform hazard (and the open
questions about guarding `scale_non_uniform_2d` and making the guard opt-out) moot.

## What changed

- `transforms.py`: deleted `rotate`, `rotate_90_degrees`, `rotate_around`, `scale_non_uniform_2d`,
  `is_clockwise`, `is_counter_clockwise` (the last two were unused); trimmed `__all__`; dropped the
  unused `math`/`sympy` imports; rewrote the module and `scale_non_uniform` docstrings. The
  dimension-general layer was kept.
- `gn.py`: dropped the five re-exports and fixed the example comment.
- `nbplotutils.py`: `sine()` computes `v * e₁₂` directly instead of `rotate_90_degrees()(v)`.
- `tests/test_transforms.py`: the planar cases were dropped; the dimension-general round-trip,
  scale-value, invertibility and error-path tests stayed.
- Notebooks (`displayg2.py`, `displaymv.py`): `scale_non_uniform_2d` → `scale_non_uniform`
  (identical); `rotate(angle)` → a small notebook-local `InvertibleFunction` on the GA rotor
  (`R = cos(a/2) − sin(a/2)·e₁e₂`, sandwich `R v R̃`). `rotate_around` would inline as
  `compose([translate(c), rotate, translate(-c)])`; no notebook used it.

## Verification

Suite 161 passing. The notebook rotor helper was spot-checked directly (notebooks are not run by the
suite): it reproduces the old `rotate` exactly (`rotate(π/2)` of `3e₁+4e₂` → `−4e₁+3e₂`), preserves
type, and composes/inverts.
