# Rewrite `plane_rotation`'s rotor construction on top of `exp()`

**Status:** proposed — follow-up to `tasks/exp-for-rotors.md`; **blocked until
that task lands.** (Split out deliberately per Bill's decision 2026-07-29:
`exp` lands standalone first, this swap is its own change.)

## Goal

`transforms.plane_rotation` currently hand-builds the half-angle rotor with
explicit trig: `rotor = plane_i * (-sin_half) + cos_half`
(`src/gacalc/transforms.py`, inside the `rotation(theta)` closure). Once
`exp()` exists, that same rotor is `(plane_i * (-theta / 2)).exp()`. Making
`exp` the single source of the half-angle rotor means the repo convention
"never hand-build a rotor by trigonometry" holds *inside the library too*, and
`plane_rotation` becomes a worked example of the exp-map rather than a
duplicate of it.

## Constraints the swap must preserve (why this is its own task)

1. **Numeric preservation, including the `i_numeric` float-coercion path.**
   `plane_rotation` keeps TWO copies of the unit bivector (exact + float-coerced)
   and picks per θ, precisely so numeric pipelines never grow sympy
   coefficients (measured ~6x arithmetic slowdown when they do — see the long
   comment in the closure). The rewrite must keep feeding the float plane to a
   float θ, and `exp`'s own float-in/float-out rule must reproduce the same
   float rotor coefficients.
2. **Symbolic display form.** With symbolic θ the rotor must still render as
   `cos(theta/2)` / `sin(theta/2)` — check the *rendered* form, not just
   `__eq__` (equality is simplify-aware and would mask a form regression;
   notebook output is part of the contract).
3. **Behavioral equality gate:** the `exp`-built rotor equals the hand-built
   one for numeric AND symbolic θ — the agreement test added by
   `exp-for-rotors` is the gate; this task must not weaken it.
4. Inverse path unchanged: the closure uses `rotor.reverse()` for the inverse
   (unit rotor) — the `exp`-built rotor is equally unit, keep that.

## Gates

`make test` (the plane_rotation doctests + conformance + the agreement test),
plus a manual notebook render check of a symbolic-θ rotor
(`notebooks/displayrotations.py`).
