# Rewrite `plane_rotation`'s rotor construction on top of `exp()`

**Status:** investigated 2026-07-29 — **recommend DROP; awaiting Bill's
decision.** The swap was measured against this task's own constraints and
violates two of them (evidence below). (Split out per Bill's decision
2026-07-29: `exp` landed standalone first; this swap was to be its own
change.)

## Findings (2026-07-29, measured in the container against the landed `exp`)

The naive swap — `rotor = (plane_i * (-theta / 2)).exp()` — fails:

1. **Constraint 1 (float reproduction): FAILS.** Sweeping 10,000 angles,
   **1,096** produced rotors that are not byte-identical to the hand-built
   `cos(θ/2) − sin(θ/2)·i` (worst delta 1.1e-16, i.e. 1 ulp). Cause: `exp`
   computes `|A| = math.sqrt((θ/2)²)`, and `sqrt(x²)` is not exactly `|x|`
   for ~11% of doubles.
2. **Constraint 2 (symbolic rendered form): FAILS.** For θ declared merely
   `real=True` (what `notebooks/displayrotations.py` and mvp's symbolic use
   look like), the exp-built rotor renders as `cos(Abs(theta)/2)` /
   `-theta*sin(Abs(theta)/2)/Abs(theta)`; a no-assumptions symbol is worse
   (`sqrt(theta**2)` everywhere). Only a `positive=True` symbol collapses to
   the clean `cos(theta/2)` form.

**Why, and why it isn't fixable inside `exp`:** `plane_rotation` writes the
closed form using two facts `exp` cannot know — the bivector it built is
*unit* (so `|−(θ/2)i| = |θ|/2` needs no sqrt), and the half-angle's sign
cancels by trig parity (cos even, sin·Â odd). `exp` computes `|A|` blindly,
as it must for arbitrary input. The hand-built form is therefore not a
"hand-built rotor" convention violation but the *better implementation*;
the "never hand-build a rotor" rule targets user code, and the rotor
*definition* inside the library was already its documented exemption.

**What guards equivalence instead:** the two agreement tests landed by
the exp task (archived: `tasks/archive/2026/07/29/exp-for-rotors.md`)
(`tests/test_exp.py::test_exp_agrees_with_plane_rotation_
{numeric,symbolic}`) pin `exp((−θ/2)i)` ≡ the `plane_rotation` rotor
(is_close for floats; exact form for a positive symbol), so a future
regression in either construction fails the suite.

**Recommendation: drop this task** (keep `plane_rotation` as-is), recording
the reason here. Needs Bill's explicit say-so to drop.

---

*Original goal and constraints, kept for the record:*

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
