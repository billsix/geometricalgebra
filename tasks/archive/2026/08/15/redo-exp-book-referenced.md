# Redo `exp()` from scratch, book-referenced — and add a unit-bivector builder `i(a, b)`

**Created:** 2026-08-01 · **Completed:** 2026-08-15

A deliberate **redo** of already-merged work. The maintainer read the then-current `exp()`, did not
understand or like it, and wanted it rebuilt from a foundation checkable against books. The specific
sore point was the hyperbolic vector branch (`A² > 0 → cosh|A| + sinh|A|·Â`), which the maintainer
suspected had been lifted from galgebra rather than derived from a trusted source. The maintainer also
wanted a function `i` that takes two vectors, for use with `exp`, and asked whether it should be the
full- or half-angle version. The work ran as an investigation with the maintainer (who read books in
parallel), then five implementation subtasks. The full math, rationale and book citations were written
into `tasks/reference/unit-bivector-and-rotors.md`.

## Starting point

- `MultiVectorBase.exp()` (`base.py`) dispatched by grade: scalar → `exp(s)`; grade-2 blade / 𝒢₃
  pseudoscalar (`A² < 0`) → `cos + sin·Â`; grade-1 vector (`A² > 0`) → `cosh + sinh·Â`; otherwise
  `ValueError`. It followed the numeric-preservation convention (`math.*` for float, `sympy.*`
  otherwise) and built results via dispatching arithmetic, never `from_blade_dict`. A generated
  `Bivector_n.exp() -> Rotor_n` override narrowed the type.
- Tests: `tests/test_exp.py` (properties + two `plane_rotation` agreement gates),
  `tests/test_conformance.py::test_exp`, `tests/test_graded.py::test_exp_narrows_bivector_to_rotor`,
  the `exp` doctests, and an exp-map section in `notebooks/displayrotations.py`.
- The first implementation's design record is `tasks/archive/2026/07/29/exp-for-rotors.md` (the "no
  `hint`, the sign is structural" rationale and the `A² = (−1)^(r(r−1)/2)|A|²` grade formula behind the
  sinh/cosh branch). Its history starts at `b807f46` ("starting implementing exp"); later touches to
  `base.py` / `tests/test_exp.py` are `ae568f0`, `7f8f06d`, `76a4036`. No Hestenes & Sobczyk page for
  `exp` had ever been found; the docstring cited only the power series.

## Investigation findings (2026-08-14)

- **galgebra confirmed.** In galgebra (github.com/pygae/galgebra, `v0.6.1rc1`, galgebra commit
  `ff0a938`, the version the archived task cited), `Mv.exp` in `galgebra/mv.py` is the power series
  split by the sign of `A²`: `cosh(n)+sinh(n)·Â` for `A²>0`, `cos(n)+sin(n)·Â` for `A²<0`, with
  `hint='+'/'-'` only for the symbolically undecidable case (which gacalc doesn't have: Euclidean makes
  the sign structural by grade). It cites no book and has no unit-bivector-from-two-vectors builder. So
  gacalc's grade-1 branch did mirror galgebra's `A²>0` branch, as the maintainer suspected.
- **`normalize(a∧b)` is a unit bivector with `i² = −1`** (any Euclidean 2-blade), so it acts as the
  imaginary unit and `exp(−(θ/2)·i) = cos(θ/2) − sin(θ/2)·i` is the half-angle rotor. **A unit bivector
  is not a rotor**: `exp` consumes the bivector to make a rotor. The request's "unit Rotor2 … for use
  with exp" conflated the two.
- **The builder already existed, unexposed, inside `transforms.plane_rotation`** (`plane =
  a.outer_product(b)`, grade-1 checks, parallel guard, `i = plane.normalize()`). `rotor_from_vectors`
  (`|a||b| + b·a`, angle locked to a↔b) is a different object.
- **Book citations:** primary **Dorst, Fontijne & Mann, *Geometric Algebra for Computer Science* §7.4**
  ("Exponential Representation of Rotors"; §7.4.1 rotors as exp of 2-blades, §7.4.3 exp of bivectors,
  §7.4.2 the trig/hyperbolic split), whose structure is gacalc's `exp`; free secondary **Macdonald,
  *Survey of GA & GC*, Eq. (2.3)/(2.4)** (`R = e^{-iθ/2}`). Doran & Lasenby (~§2.7) and Hestenes &
  Sobczyk cover it, but no exact equation/page was pinned, and none was invented.
- **The hyperbolic branch is the Minkowski boost formula** (Dorst §7.4.2; Macdonald §4.1), meaningful
  only for spacetime bivectors in a Lorentzian metric. Applied to a Euclidean vector it has no geometric
  interpretation; it worked only because a vector happens to square positive.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-14)

- **Name it `i`** (the maintainer's call, overriding the research's recommendation of
  `bivector_from_vectors` alone): `i` is the mathematical name of the unit bivector.
- **Layered:** `bivector_from_vectors(a, b)` returns the *raw* bivector `a ∧ b` (magnitude = the
  parallelogram's area) and does not guard parallel vectors (their wedge is legitimately zero); `i(a, b)`
  normalizes it to the unit bivector and owns the parallel guard. Two names for two different things.
- **`i`, `bivector_from_vectors` and `.i()` return a bivector, never a rotor**, and carry no angle: θ
  enters at the call site. A rotor-returning `i` would contradict the notation and duplicate
  `rotor_from_vectors`.
- **Placement** (the full types and the graded types are sibling `@typing.final` subclasses of
  `MultiVectorBase`): `bivector_from_vectors` as a classmethod on the base, beside `rotor_from_vectors`;
  the classmethod `i(a, b)` on `Gn`, `G2`, `G3` and `Vector`, and kept off `MultiVectorBase` (else the
  graded `.i()` would shadow it); the instance `.i()` only on the graded `Bivector` (= `normalize()`) and
  `Rotor` (= `plane_of_rotation()`). `Gn` gets the classmethod, not `.i()`, since a class can't hold both;
  a `Gn` bivector's plane is `.normalize()`. The flagged clash with `identity()`'s inner `i` was a
  non-issue (a local function, not a class member).
- **`exp`: slim, don't delete.** The maintainer raised deleting `exp` entirely. Kept instead, reduced to
  the scalar and negative-square cases ("rotor = exp(bivector)"), because deletion would force
  hand-inlined trig at every rotor site and drop a standard GA operation, and the opacity came from the
  generic grade dispatch, not the bivector math.
- **Drop the hyperbolic vector branch**: correctness for the project's Euclidean-only scope, not only
  cleanup. The alternative (keep it with a docstring calling it the boost formula) was rejected.
- **Rotation from a bivector, `bivector_rotation(i)`** (the maintainer's idea: "something like
  `plane_rotation`, just taking `i` as the parameter"), named to fit the `plane_rotation` /
  `projection_rotation` family. It builds the rotor **directly** as `cos(θ/2) − sin(θ/2)·i`, never via
  `exp(−(θ/2)·i)`: `exp` goes through the magnitude `sqrt(θ²)/2`, which collapses to `θ/2` only under a
  positivity assumption, so a symbolic θ would render as `cos(√(θ²)/2)`. `R` is automatically unit
  (`R R̃ = c² + s² = 1`); any `(c, s)` with `c² + s² = 1` turns by `θ = 2·atan2(s, c)` (θ = 90° is the
  `c = s = 1/√2` case).
- **`bivector_rotation` normalizes `i` internally** (the maintainer: "especially given that floating
  point may be in play"), after validating grade 2 (`TypeError` otherwise). It assumes a simple bivector
  (`i² = −1`, true for every 𝒢₂/𝒢₃ bivector); non-simple 𝒢₄₊ bivectors such as `e₁₂ + e₃₄` were noted
  as out of scope and left unguarded.
- `README.md` / `CLAUDE.md` mention of `bivector_rotation` was reserved for the maintainer to add later.

## What was done

1. **`bivector_from_vectors`, `i(a, b)`, `.i()`** (2026-08-14): implemented in `base.py`, `gn.py` and
   the generator (`i_classmethod` / `i_extractor` in `tools/gen_specialized.py`); `Vector.i` narrows to
   `Bivector` at runtime. 9 new tests (`tests/test_unit_bivector_i.py`), 358 total.
2. **`bivector_rotation(i)`** (2026-08-15) in `transforms.py`, re-exported from `gn.py`. A shared private
   `_unit_bivector_rotor_factory(i)` holds the half-angle construction and numeric preservation, and both
   `bivector_rotation` and `plane_rotation` call it. `plane_rotation` was *not* rewritten to call
   `bivector_rotation`: that returns `InvertibleFunction[MultiVectorBase]` (operand-agnostic, because
   nothing in `i` determines the operand type; you rotate vectors with a bivector plane), and delegating
   would have regressed `plane_rotation`'s precise `InvertibleFunction[V]`, which mvp relies on
   (`Vector3 → Vector3`). Runtime still preserves the operand's concrete type. `plane_rotation` stayed
   coefficient-identical (`test_exp_agrees_with_plane_rotation_symbolic` and `test_plane_rotation.py`
   unchanged). 8 new tests (`tests/test_bivector_rotation.py`) + a doctest.
3. **`exp()` slim-down** (2026-08-15): the `A² > 0` branch was removed, so a vector's `exp` raises
   `ValueError`; the `match` collapsed to a single guarded return. `Bivector_n.exp() → Rotor_n` and the
   𝒢₃ pseudoscalar's `exp` still work. Tests updated (`test_exp_of_a_vector_is_rejected`, formerly
   `..._is_hyperbolic`; conformance `test_exp` rejects a vector in every representation). The docstring
   cites Dorst §7.4; the CLAUDE.md exp bullet and `tasks/reference/design-decisions.md` (both said
   "hyperbolic for a vector") were corrected.
4. **Precise typing for `i` + call-site audit** (2026-08-14), done in
   `tasks/archive/2026/08/26/precise-typing-remaining-methods.md` (Tier 2, the same mechanism): `i`,
   `bivector_from_vectors`, `.i()` and `plane_of_rotation` narrow to `Bivector_n`, `rotor_from_vectors`
   to `Rotor_n` (`Gn.i → Gn` unchanged), via the generator helpers `classmethod_narrowing_overloads` and
   `inherited_classmethod_narrowing`, gated on n ≥ 2. Parameters stayed `MultiVectorBase` on the
   implementation, with a precise `Vector` `@overload`. `test_exp.py`'s two hand-rolled
   `(e_1 ^ e_2).normalize()` sites became `Vector.i(e_1, e_2)`; the `displayrotations.py` sweep found
   only prose. This did **not** let `plane_rotation` reuse `i`: it is generic over `V`, and a classmethod
   returning a concrete `Bivector` would widen `V`, so its wedge stays inline.
5. **Explicit parallel guard in `i`** (2026-08-14): `i(a, b)` (generated and `Gn.i`) raises
   `ValueError("the two vectors are parallel (their wedge is zero): they span no plane of rotation")`,
   matching `plane_rotation`, instead of leaking `normalize`'s `ZeroDivisionError`.
   `test_i_of_parallel_vectors_raises` was updated.

Most of this exposed and named machinery that already existed inside `plane_rotation` /
`plane_of_rotation`, plus the `exp` cleanup; little was new mathematics.

## Verification

Each subtask: ruff + ty clean, generator deterministic, doc-regions OK, and the container gate (ruff
0.16.3, ty, pytest) green; 367 tests at the end.

## Left open at archive

The `exp` docstring citation (Dorst §7.4) was provisional, pending the maintainer's own book reading; a
different anchor (say a Hestenes & Sobczyk page) would be a one-line docstring swap with no
implementation change.
