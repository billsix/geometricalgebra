# Make the 2D-only transforms clearly 2D-only to users

**Status:** not started · low priority
**Started:** 2026-06-05 (proposed)

## Goal

Some of the `InvertibleFunction` transform factories in `src/geometricalgebra/transforms.py` are
**inherently planar (act only in the e₁e₂ plane)**, but nothing stops a user from applying them to a
`G3`/`Gn` vector that has an e₃⁺ component — which silently produces a wrong, mixed-grade result.
Make the 2D-only nature obvious and/or enforced, so users don't get garbage out. This is a
clarity/safety improvement, not a new feature — **low priority.**

## Background / findings (2026-06-05)

Transforms split into two groups:

- **Dimension-general (correct in any *n*) — leave alone:** `translate`, `uniform_scale`,
  `scale_non_uniform`, `compose`, `inverse`, `identity`.
- **Inherently 2D (e₁e₂ plane only):** `rotate_90_degrees`, `rotate`, `rotate_around`,
  `scale_non_uniform_2d` (only 2 factors; silently drops e₃⁺), and `is_clockwise` /
  `is_counter_clockwise` (these two already `assert` the inputs lie in the (1,2) plane).

The real hazard is correctness, not just naming: applying `rotate(θ)` to a G3/Gn vector with an e₃
component turns e₃ into the trivector e₁e₂e₃ (`v * e₁e₂`), so the result is mixed-grade, not a
rotated vector.

**Why types can't fully solve this (user's own intuition, confirmed):** `Gn` is a single type
spanning every dimension — there is no `n` in its type — so a type checker cannot distinguish a 2D
`Gn` from a 3D `Gn`. Type-restricting `rotate` to `InvertibleFunction[G2]` would (a) defeat the
representation-preserving design (these are meant to run on `Gn` too), (b) force `transforms.py` to
import a concrete class, breaking its `base`-only layering, and (c) still not constrain `Gn` at all.
So static typing gives partial coverage at best, and not for the representation where the trap is
most likely.

## Options considered

- **A. Runtime planarity guard (preferred):** at apply-time, assert the input has no grade-1
  component outside e₁/e₂ (generalize what `is_clockwise` already does), raising a clear error.
  Catches `Gn` misuse; small per-call cost; fully honest.
- **B. Clearer naming:** rename to e.g. `rotate_in_e1e2_plane` / `rotate_90_in_e1e2_plane`; documents
  only, churns the API.
- **C. Generic `InvertibleFunction[T]`:** doesn't help `Gn`, breaks layering — rejected (this is the
  approach the user's instinct correctly flagged as not working).
- **D. Docstring-only:** already partly done (module + per-fn docstrings say "inherently 2D /
  planar"); no enforcement.

Recommended direction: **A + B** — the runtime guard is the only thing that actually protects the
`Gn` user, with clearer naming as a complementary nicety.

## Plan

- [ ] Decide scope: guard only (A), or guard + rename (A+B)
- [ ] Add a shared planarity check (no grade-1 components beyond e₁/e₂) and apply it inside the
      forward + inverse of `rotate_90_degrees`, `rotate`, `rotate_around`, `scale_non_uniform_2d`
- [ ] (If B) rename the planar factories and update re-exports in `gn.py`, callers, and notebooks
- [ ] Add conformance tests: planar input round-trips; non-planar G3/Gn input raises a clear error
- [ ] Run `python -m pytest -q` and `entrypoint/format.sh` (ruff + ty clean)

## Notes / decisions

## Open questions

- For `scale_non_uniform_2d` on a 3D value, should the guard reject, or is "drop e₃" acceptable
  documented behavior? (Differs from the rotations, which produce genuine garbage.)
- Should the guard be opt-out for power users (perf), or always on?
