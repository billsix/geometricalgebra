# Consider renaming the grade-0 number type "scalar" → "real"

**Status:** proposed — needs go-ahead
**Priority:** 7
**Difficulty:** 6
**Created:** 2026-09-26 **Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)

## BLUF

Consider renaming the *number* API of the algebra from "scalar" to "real" — chiefly
`Scalar.from_scalar(x)` → `Scalar.from_real(x)`, and possibly the `Scalar` type itself →
`Real`, the field `coeff_scalar` → `coeff_real`, and the coefficient type `Coef` → `Real`.
This covers both boundaries: the real number you put *in* (the constructor) and the real
number you take *out* (coefficients, `scalar_part`, `magnitude`, iteration — see (A′)). The pedagogical case: students know
**real numbers** from high-school math, whereas "scalar" carries an operational
connotation (a thing that *scales* something else by multiplying) that we may not want to
front-load. "Done" for THIS task = a decision (go / no-go) informed by the marked-up
inventory and the usefulness write-up below; it is **not** authorization to rename.
**If we go ahead, it needs its own reference doc** (a decision record + the kept/renamed
terminology map), because "why is the constructor `from_real` but the method still
`scalar_part`?" will be asked repeatedly.

## Context (read first)

- gacalc is a **published PyPI library** (github.com/billsix/geometricalgebra). Any renamed
  public name is a **breaking change** for consumers → SemVer bump + `CHANGELOG.md` entry,
  and probably a deprecation alias for one release. This is the single biggest cost.
- The word "scalar" is used in the source in **three distinct senses**, and only ONE is a
  rename candidate. Conflating them is the trap this task exists to prevent.
- Rough scale (2026-10-04, tracked files only — the gitignored generated `g*.py` are excluded):
  **584** whole-word occurrences of "scalar" on 489 lines
  (`git grep -oiw scalar -- src tools tests notebooks README.md | wc -l`), **1060** as a substring
  (`git grep -oi scalar …`, which also counts `pseudoscalar` etc.) — but the *public API surface*
  that would actually change is small
  (a handful of names); the bulk is the generator, tests, and established GA terms.

## Deviation from Hestenes — and why the Real/Scalar distinction is right in Python (William Emerison Six <billsix@gmail.com>, 2026-09-26)

**This project deliberately distinguishes a plain real number from a grade-0 multivector; Hestenes
does not — and that difference is a consequence of paper vs. Python, not a disagreement with the
math.** On paper Hestenes treats the real number `5` and the grade-0 multivector `5` as the same
object: `5` and `5 + 1·e₁` are both just multivectors with real coefficients, and nothing in the
notation forces a type boundary. In Python there IS a boundary the paper never had: the real number
`5` is a Python `int` / `float` / `sympy.Expr` — it is **not** an instance of `MultiVectorBase` or
any generated class, and (by the symbolic-equality contract) a multivector is never `==` a bare
number. So "a real number" and "a grade-0 element of 𝒢ₙ" are genuinely different Python types with
different behavior, even though they denote the same mathematical thing.

That makes naming the *real number* explicitly — rather than calling it "scalar", which in GA is the
grade-0 *element* — a useful, honest distinction FOR THIS IMPLEMENTATION: it tells the reader which
side of the Python type boundary a value is on. **It must be documented as a deliberate deviation
from Hestenes, with this reasoning**, in the eventual reference doc (`scalar-vs-real-naming.md`): we
are not renaming because Hestenes is wrong, but because Python's type system draws a line his paper
did not need.

## The three senses of "scalar" (the marked-up inventory)

### (A) RENAME CANDIDATES — the grade-0 *number* type and its number bridge

These denote "a plain real number living in the algebra" and are the actual subject:

- `MultiVectorBase.from_scalar(scalar)` (`src/gacalc/base.py`). The headline case:
  `from_scalar` → `from_real`. (Its param is even named `scalar: int | float`.)
- The generated **`Scalar` / `ScalarN` / `Scalar_n`** grade-0 class — generator
  `tools/gen_specialized.py` (`scalar_spec`, `generate_scalar`, the `ScalarN` docstring),
  exported per-module as `Scalar`. Candidate: `Scalar` → `Real`.
- The grade-0 **field** `coeff_scalar` — generated (`tools/gen_specialized.py`, the
  `field_name` blade→field mapping), e.g.
  `Scalar(coeff_scalar=3)`. Candidate: `coeff_real`.
- Possibly `from_coef` / `Coef` (`base.py`) — the symbolic sibling of `from_scalar`;
  if `from_scalar`→`from_real`, decide whether `from_coef` stays (it accepts `sympy.Expr`,
  i.e. a *symbolic* real, so "real" still fits) or is left as the "coefficient" bridge.
- Constructor param names / locals named `scalar` throughout (mechanical, follow the API).

### (A′) The extraction side — a number pulled OUT of the algebra is ALSO a real

Symmetric to (A): the rename is not only about constructing an algebra element *from* a
number, but about the plain Python number you get *back out*. Whenever you extract a
coefficient, that value is a real (numeric or symbolic-real). Same notion of "real number,"
same word to consider:

- **`Coef = int | float | sympy.Expr`** (`base.py`, module level) — the coefficient type: exactly "a
  real number, numeric or symbolic". This is the strongest `→ Real` candidate on the
  extraction side (a type alias `Real` reads as ℝ). It threads everywhere (`BladeCoef`,
  return types of the methods below), so renaming it is high-churn but conceptually clean.
- **`scalar_part()` → returns a `Coef`** — the grade-0 part, *as a real*.
- **`coefficient(blade)` → `Coef`** — reads one coefficient (a real).
- **`magnitude()` / `magnitude_squared()` / `__abs__()` → `Coef`** — norms are reals.
- **Iteration** (`list(v)`) — yields the coordinate *values*, i.e. reals, in blade order.

The point of this section (added per the maintainer, 2026-09-26): "real" describes the numbers at BOTH
boundaries of the algebra — the ones you put in and the ones you take out — which is a
stronger, more consistent story than "real is just the grade-0 constructor." It does NOT by
itself force renaming the extraction *methods* (see the terminology tension below —
`scalar_part` is a GA term, `magnitude` isn't "scalar"-named at all), but it DOES put the
coefficient **type** `Coef` squarely in scope and sharpens the rationale for `Real`.

### (B) KEEP — established Geometric-Algebra / math terminology (do NOT rename)

Renaming these would diverge from Hestenes & Sobczyk and the wider GA literature, and from
math usage students will meet elsewhere. They are effectively externally-defined names:

- **`scalar_part()`** — "the scalar part ⟨A⟩₀ of a multivector" is the
  universal GA term for the grade-0 component; `real_part` would also collide with the
  complex-number meaning. **Keep.**
- **`scalar_product()`** — the scalar product ⟨A B⟩ is a named GA product.
  **Keep.**
- **`is_scalar()`** — "is this a (pure) scalar?" is the grade predicate in
  GA parlance (cf. `is_vector`/`is_bivector`). **Keep** (renaming to `is_real` fights the
  grade-predicate family). *Open question — this one is arguable.*
- **`pseudoscalar` / `unit_pseudoscalar` / `unit_pseudoscalar_squared` /
  `pseudoscalar_squared_sign`** (`base.py`) — "pseudoscalar" is a single GA term
  (the top-grade blade); it is NOT "pseudo" + our "scalar". **Keep, absolutely.**

### (C) INTERNAL — generator/impl names (rename only for consistency, low external cost)

`scalar_spec`, `generate_scalar`, `add_scalar_spec`, `scalar_name`, `scalar_const`,
`scalar_const_coef`, `self_scalar_field`, `scalar_left`/`scalar_right`, `_scalar_dual_doc`
(new) in `tools/gen_specialized.py`. Not public; rename iff we rename the type, purely for
internal consistency.

### (D) CHURN — call sites in tests, notebooks, README, docstrings

`tests/*` (heavy: `test_operator_typing.py`, `test_multivector.py`, `test_graded.py`),
`notebooks/displayg*.py`, `README.md`, and the new specialized docstrings in
`tools/gen_specialized.py` (the `scalar|…` role keys and `Scalar.from_scalar(...)` doctests).
Mechanical, but large and must stay in lockstep with (A).

## Usefulness — the case FOR

- **Meets students where they are.** "Real number" is high-school vocabulary; the grade-0
  elements of 𝒢ₙ *are* the reals. `Real.from_real(3)` (or just recognizing `Real` as ℝ)
  needs no new concept. "Scalar" asks the student to already hold the idea of "a quantity
  that scales a vector" — true, but it is the *operational* role, not what the object *is*.
- **Names the thing, not its job.** A grade-0 element is a real number; that it *acts by
  scaling* is a theorem about multiplication, not its identity. `from_real` reads as "lift a
  real number into the algebra," which is exactly the operation.
- **Consistency with the grade-pure family framing** — `Vector`/`Bivector`/`Trivector` name
  *what the element is*; `Real` continues that ("the grade-0 elements are the reals").
- **Symmetry at both boundaries** (the maintainer, 2026-09-26; see (A′)). A real number goes *in*
  (`from_real`) and a real number comes *out* (coefficients, `scalar_part`, `magnitude`,
  iteration). Naming the grade-0 type / coefficient "real" makes the same word describe the
  numbers on both sides of the algebra — the thing a student hands in and the thing they read
  back are both just real numbers — which is a more coherent mental model than reserving
  "real" for the constructor alone.

## The case AGAINST / risks

- **Breaking public API** on PyPI (see Context) — the dominant cost. Needs a major/minor
  bump, a `CHANGELOG` breaking-change entry, and ideally a `from_scalar` deprecation alias.
- **Splits terminology from the GA literature.** The books say "scalar part", "scalar
  product", "scalar" for grade 0. A student reading gacalc alongside Hestenes now sees
  `Real` where the book says "scalar". The kept (B) names already say "scalar", so we'd ship
  a codebase that says BOTH "real" (the type) and "scalar" (its part/product) — which is the
  very inconsistency the reference doc would have to justify.
- **`scalar` is not wrong**, just abstract; the docstrings written 2026-09-26 already explain
  the grade-0 type in plain terms, which mitigates the pedagogy gap without a rename.
- **Precedent that shrinks the cost above (gacalc 0.1.0, 2026-09-28):** the rotor → versor rename
  was a breaking public rename and was accepted by the maintainer ("nobody but me uses my
  library"), shipped as a `CHANGELOG.md` BREAKING entry plus a consumer grep (mvp) — so the
  mechanism is settled and "breaking public API" weighs less than when this task was filed
  (`tasks/archive/2026/10/04/rename-rotor-to-versor.md`).

## Open questions

1. **Scope of the rename:** just `from_scalar` → `from_real` (smallest, keeps the `Scalar`
   type name), OR also the `Scalar` type → `Real` and `coeff_scalar` → `coeff_real` (full)?
   My lean: it's all-or-nothing — `Real.from_scalar` or `Scalar.from_real` is worse than
   either consistent choice, so decide the whole set together.
2. **Do the (B) established terms stay "scalar"?** I recommend YES for `scalar_part`,
   `scalar_product`, `pseudoscalar` (literature). `is_scalar` is the one genuinely arguable
   case — `is_real` vs keeping the `is_<grade>` family. Your call.
3. **Backward compatibility:** ship a deprecated `from_scalar` alias (one release) or a hard
   break? (PyPI consumers + the mvp/other projects that call `from_scalar`.)
4. **`from_coef`/`Coef`:** leave as the symbolic-coefficient bridge, or fold into the "real"
   naming (a `sympy.Expr` is a symbolic real)?
5. **The coefficient TYPE `Coef` → `Real`?** (the extraction side, (A′)). It is precisely
   "a real, numeric or symbolic," so `Real` reads well and unifies the in/out story — but it
   is a pervasive type alias (all coefficient return types, `BladeCoef`), so high churn and a
   public-type rename. Decide together with the `Scalar`→`Real` question (Q1): renaming the
   type but not `Coef`, or vice-versa, re-introduces the split we're trying to remove. My
   lean: if `Scalar`→`Real`, also `Coef`→`Real`; if we keep `Scalar`, keep `Coef`.

## Recommendation — reals cross the boundary, algebra elements stay inside (William Emerison Six <billsix@gmail.com>, 2026-09-26)

A concrete answer to the "(A′) what returns a real?" question — *should the extraction/measurement
methods keep returning `Coef` (a plain real), or return a grade-0 multivector wrapping it?*

- **Keep every extraction/measurement returning a plain real (`Coef`).** `scalar_part()`,
  `coefficient(blade)`, `magnitude()` / `magnitude_squared()` / `__abs__()`, `scalar_product()`,
  `cosine()`, and iteration (`list(v)`) genuinely yield real numbers, and returning a Python real is
  what makes them usable: `mag < 1.0`, `math.sqrt`, numpy arrays, plotting, and crucially
  `scalar_part() == 0` all work on a real but **not** on a grade-0 multivector — the `mv == bare
  number` footgun (see `symbolic-equality.md`) would make `== 0` / `== 1` silently `False`. Wrapping
  these in a `Scalar` would force a `.scalar_part()` unwrap at every call site and re-introduce that
  footgun. **Do not switch these to return multivectors.**
- **Algebra operations that happen to land in grade 0 stay typed algebra elements.** `A * B`,
  `A ^ B`, projections, `exp`, … already return the resolved type (a grade-0 result is a `Scalar`),
  which is right: they operate *within* the algebra. The boundary is clean — **a real goes IN via
  `from_real` and comes OUT via an explicit extraction; algebra elements never silently decay to bare
  numbers except through a named extraction.** `scalar_product` (= ⟨A B⟩) is an extraction and rightly
  returns a real even though `A*B` (grade 0) returns a `Scalar` — that asymmetry is the boundary
  working as intended, not an inconsistency to "fix".
- **Naming collision this resolves (refines Q1/Q5).** "Real" can name only ONE of {the Python real
  coefficient type `Coef`, the grade-0 element class `Scalar`} — a type alias `Real = int | float |
  sympy.Expr` and a class `Real` cannot coexist. The deviation above says which: the *Python real
  number* is `Real`; the grade-0 *algebra element* is a multivector. So the recommendation is
  **`Coef` → `Real`** (the number type reads as ℝ — what you put in via `from_real` and get out via
  extractions) and **KEEP the grade-0 class as `Scalar`** (it is an element of the algebra,
  deliberately distinct from a Python real). `from_scalar(scalar: int | float)` →
  `from_real(real: Real)` then reads correctly ("lift a real into the algebra"). **This inverts the
  task's original headline lean** (`Scalar` → `Real` class rename): the name "Real" belongs on
  `Coef`, not on the grade-0 class — precisely because the whole point is that a Python real is *not*
  a multivector.

## If we proceed

- Write a reference doc `tasks/reference/scalar-vs-real-naming.md` (decision record + the
  definitive KEEP-vs-RENAME map from (A)/(B) above + **the deviation-from-Hestenes reasoning**
  (paper treats real 5 ≡ grade-0 5; Python's type system does not), so the "real type / scalar
  part" split is explained once and not re-litigated).
- Do the rename as a generator-first change (the `Scalar`/`coeff_scalar` names are emitted
  by `tools/gen_specialized.py`; see `tasks/reference/code-generator-architecture.md`),
  then tests/notebooks/README, then the `CHANGELOG` + version bump.
- Cross-repo: grep consumers (e.g. mvp) for `from_scalar` before breaking it.
