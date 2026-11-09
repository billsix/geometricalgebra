# Rewrite `plane_rotation`'s rotor construction on top of `exp()`

**Completed:** 2026-07-29 (dropped on the maintainer's explicit say-so; kept as an investigation
record)

Split out per the maintainer's decision of 2026-07-29 (`exp` landed standalone first, in
`tasks/archive/2026/07/29/exp-for-rotors.md`; this swap was to be its own change). The swap was
measured against this task's own constraints and violated two of them, so `plane_rotation` keeps its
hand-built rotor deliberately. Durable rationale: `tasks/reference/design-decisions.md` ›
"`plane_rotation` builds its rotor by hand-written trig ON PURPOSE".

## The proposal

`transforms.plane_rotation` hand-builds the half-angle rotor with explicit trig
(`rotor = plane_i * (-sin_half) + cos_half`, inside the `rotation(theta)` closure in
`src/gacalc/transforms.py`). With `exp()` that rotor is `(plane_i * (-theta / 2)).exp()`; making
`exp` its single source would have extended the "never hand-build a rotor by trigonometry"
convention inside the library. Constraints the swap had to preserve:

1. **Numeric preservation, including the `i_numeric` float-coercion path.** `plane_rotation` keeps
   two copies of the unit bivector (exact + float-coerced) and picks per θ so numeric pipelines
   never grow sympy coefficients (a measured ~6x arithmetic slowdown when they do); `exp`'s
   float-in/float-out rule had to reproduce the same float rotor coefficients.
2. **Symbolic display form**: with symbolic θ the rotor must render as `cos(theta/2)` /
   `sin(theta/2)`, checked on the rendered form, since simplify-aware `__eq__` would mask a form
   regression.
3. **The behavioral equality gate** from the exp task, not weakened.
4. **The inverse path** (`rotor.reverse()` for a unit rotor) unchanged.

## Findings (2026-07-29, measured in the container against the landed `exp`)

The naive swap failed:

1. **Constraint 1 (float reproduction) failed.** Over 10,000 angles, **1,096** rotors were not
   byte-identical to the hand-built `cos(θ/2) − sin(θ/2)·i` (worst delta 1.1e-16, 1 ulp). Cause:
   `exp` computes `|A| = math.sqrt((θ/2)²)`, and `sqrt(x²)` is not exactly `|x|` for ~11% of
   doubles.
2. **Constraint 2 (symbolic rendered form) failed.** For θ declared merely `real=True` (as in
   `notebooks/displayrotations.py` and mvp's symbolic use), the exp-built rotor rendered as
   `cos(Abs(theta)/2)` / `-theta*sin(Abs(theta)/2)/Abs(theta)`; a no-assumptions symbol was worse
   (`sqrt(theta**2)` everywhere). Only a `positive=True` symbol collapsed to `cos(theta/2)`.

**Why it isn't fixable inside `exp`:** `plane_rotation` writes the closed form using two facts `exp`
cannot know: the bivector it built is *unit* (so `|−(θ/2)i| = |θ|/2` needs no sqrt), and the
half-angle's sign cancels by trig parity (cos even, sin·Â odd). `exp` computes `|A|` blindly, as it
must for arbitrary input. The hand-built form is the better implementation, not a convention
violation: the "never hand-build a rotor" rule targets user code, and the rotor definition inside
the library was already its documented exemption.

**What guards equivalence instead:** the two agreement tests from the exp task
(`tests/test_exp.py::test_exp_agrees_with_plane_rotation_{numeric,symbolic}`) pin
`exp((−θ/2)i)` ≡ the `plane_rotation` rotor (is_close for floats; exact form for a positive
symbol), so a regression in either construction fails the suite.
