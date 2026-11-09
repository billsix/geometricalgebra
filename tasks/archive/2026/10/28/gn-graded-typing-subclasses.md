# Investigate Gn graded typing-subclasses (Vector/Bivector/Versor/Scalar) + overloads

**Created:** 2026-10-27 · **Completed:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

An investigation only; no library change.

Investigated whether `Gn` (the dimension-agnostic reference) can gain graded typing subclasses like the
generated `G` classes have. Outcome: **feasible, but not worth a full subtype hierarchy on `Gn`** —
precise graded typing already lives on the generated `G`, and `Gn`'s only incremental benefit is
narrowing at a known-grade point in dimension-agnostic code. Recommended a thin, static-only `TypeGuard`
layer, wired only where a real call site needs it, with operations widening back to `Gn`. Both design
questions were settled per the maintainer's "whatever you recommend." Full verdict, empirical findings, and
rejected alternatives: `tasks/reference/gn-graded-typing-feasibility.md`.

## Decisions

- **Q1 (narrowing-view vs. grade-driven `from_blade_dict`): narrowing-view.** Operations widen to `Gn`;
  the caller re-narrows at the next known-grade step. Grade-driven auto-narrowing would re-derive the
  generator's operation-driven typing on `Gn` — already rejected on the `G` side as value-dependent.
- **Q2 (`as_vector()` methods vs. `TypeGuard`/`TypeIs`): `TypeGuard`.** Thin marker subtypes
  (`Vector(Gn)` with `__slots__ = ()`) + a `Gn`-specific `TypeGuard`-returning helper. Not `TypeIs` (a
  plain grade-1 `Gn` is not a subtype instance, so `TypeIs` would be unsound); `as_vector()` real
  instances are the heavier fallback only if `isinstance` dispatch is ever needed.

## What was done (empirical investigation, no library change)

- Confirmed the crux from the code: shared `base.py` methods construct results with
  `type(self).from_blade_dict(...)` / `type(self).zero()`, so a naive `Gn` subclass mis-types operation
  results.
- Wrote two throwaway spikes, `spike_runtime.py` and `spike_typing.py` (removed at archive; in git
  history), and ran them in the container:
  - `spike_runtime.py`: `class Vector(Gn): __slots__ = ()` subclasses cheaply; `a*a` for `a = 3e₁ + 4e₂`
    returned a value of class `Vector` holding `{(): 25}` (a scalar, `.is_vector() == False`) — the
    mis-typing — and `Gn.from_blade_dict(...)` widened it back to `Gn`.
  - `spike_typing.py` under `ty`: `TypeGuard[Vector]` narrows the positive branch to `Vector` (leaves
    `Gn` after); `TypeIs[Vector]` additionally narrows the else-branch to `Gn & ~Vector`.
- Captured the verdict, design fork ((A) static-only `TypeGuard` vs. (B) real instances + widening
  overrides), and rejected alternatives in the reference doc; scaffolded the opt-in implementation task.

## Follow-ups

- `tasks/reference/gn-graded-typing-feasibility.md` — the durable verdict.
- `tasks/gn-graded-typing-implement.md` — the opt-in implementation, scaffolded gated on a go-ahead
  **and** a concrete consumer (the investigation found none).
