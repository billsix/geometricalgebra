# Consider renaming the grade-0 number type "scalar" → "real"

**Created:** 2026-09-26 · **Completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>); the rename
shipped with 696 tests, format/ty, `check-generated` and `check-regions` green.
**Decision record:** `tasks/reference/scalar-vs-real-naming.md` (the KEEP/RENAME map and the
deviation-from-Hestenes reasoning).

## Summary

The task weighed renaming the algebra's *number* API from "scalar" to "real", on the pedagogical case that
students know real numbers from high school while "scalar" front-loads an operational meaning (a thing
that scales). The outcome: the Python coefficient type `Coef` became `Real`, `BladeCoef` became
`BladeReal`, and the two constructors `from_scalar`/`from_coef` merged into `from_real(real: Real)`. The
grade-0 class `Scalar`, its field `coeff_scalar`, and the GA terms `scalar_part`, `scalar_product`,
`is_scalar` and `pseudoscalar` were kept. It was a hard breaking change.

## The reasoning

- **Deviation from Hestenes** (William Emerison Six <billsix@gmail.com>, 2026-09-26). On paper Hestenes
  treats the real number `5` and the grade-0 multivector `5` as one object. In Python they are different
  types: `5` is an `int`/`float`/`sympy.Expr`, not a `MultiVectorBase`, and a multivector is never `==` a
  bare number. Naming the Python number "real" says which side of that type boundary a value is on. This
  was a deliberate deviation forced by Python's type system, not a disagreement with the math, and is
  documented as such in the decision record.
- **"Scalar" had three senses in the source**, and only one was a rename candidate: (A) the grade-0
  number type and its number bridge (`from_scalar`, `Coef`), with (A′) its extraction side (the `Coef`
  returned by `scalar_part()`, `coefficient()`, `magnitude()`, iteration); (B) established GA terms,
  effectively externally defined (`scalar_part` (and `real_part` would collide with the complex
  meaning), `scalar_product`, `is_scalar`, `pseudoscalar`, which is one GA term, not "pseudo" + scalar);
  (C) internal generator names in `tools/gen_specialized.py` (`scalar_spec`, `generate_scalar`, …), to
  follow the public names only for consistency. The rest was call-site churn in tests, notebooks, README
  and generator docstrings.
- **Scale** (2026-10-04, tracked files only): 584 whole-word occurrences of "scalar" on 489 lines, 1060 as
  a substring, but the public surface that changed was a handful of names.
- **For:** "real number" is high-school vocabulary; it names what the thing is, not its job; and the same
  word describes the numbers at both boundaries of the algebra, what goes in and what comes out (the
  maintainer, 2026-09-26).
- **Against:** a breaking public rename on PyPI, and a codebase that says both "real" (the type) and
  "scalar" (its part/product) beside the literature's "scalar". The cost was judged smaller after the
  rotor → versor precedent (`tasks/archive/2026/10/04/rename-rotor-to-versor.md`): a breaking rename the
  maintainer accepted ("nobody but me uses my library"), shipped as a `CHANGELOG` BREAKING entry plus a
  consumer grep.
- **Reals cross the boundary, algebra elements stay inside** (William Emerison Six <billsix@gmail.com>,
  2026-09-26). Every extraction/measurement keeps returning a plain real: `mag < 1.0`, `math.sqrt`, numpy,
  plotting and `scalar_part() == 0` work on a real but not on a grade-0 multivector, where `== 0` would be
  silently `False`. Algebra operations that land in grade 0 (`A * B`, `A ^ B`, `exp`, …) stay typed algebra
  elements; `scalar_product` is an extraction and rightly returns a real. Since an alias `Real` and a class
  `Real` cannot coexist, the name went on the Python number type (`Coef` → `Real`) and the grade-0 class
  kept `Scalar`. This inverted the task's original headline lean of renaming the `Scalar` class.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-05)

1. **Scope (a):** rename `Coef` → `Real` and `from_scalar` → `from_real` (parameter `scalar:` → `real:`);
   keep the class `Scalar` and the field `coeff_scalar`. "Real" names the Python number, not the algebra
   element. (The agent's earlier lean had been all-or-nothing on `Scalar` and `Coef` together; the
   boundary reasoning above replaced it.)
2. **`is_scalar()` kept** (the `is_<grade>` family; the literature term), with `scalar_part`,
   `scalar_product` and `pseudoscalar`.
3. **Hard break (a):** a `CHANGELOG` BREAKING entry and a version bump, no deprecation alias. Evidence: no
   in-house consumer used `from_scalar`/`from_coef`/`Coef`/`coeff_scalar` (mvp had zero hits; the only
   out-of-repo matches were galgebra's own unrelated names).
4. **`from_coef` folded (a)** into the one constructor `from_real(real: Real)` (`Real = int | float |
   sympy.Expr` already covers the symbolic case) and removed.
5. **`BladeCoef` → `BladeReal` (a).**

## What was done (2026-10-05)

- **Discovery:** `discover.sh` (removed at archive; in git history) wrote `data/sites.txt`: 336 tracked
  sites of `Coef`/`BladeCoef`/`from_scalar`/`from_coef` across `src`, `tools`, `tests`, `notebooks`,
  `README.md`, `book`, `CLAUDE.md` and `tasks/reference` (the decision record was excluded; its map holds
  the old names on purpose).
- **By hand first:** the two constructors merged into `MultiVectorBase.from_real(real: Real)` (the docstring
  states the boundary; a doctest was added), and the `CHANGELOG` BREAKING entry.
- **Codemod** `rename.py` (removed at archive; whole-word, content-keyed): `BladeCoef → BladeReal`,
  `Coef → Real`, `from_scalar`/`from_coef → from_real`; 38 files rewritten; a second run made 0 changes.
  The generator emits `Real` in every annotation and doctest, so the gitignored `g*.py` followed.
  `tools/astbuild.cast_coef` kept its internal name.
- **Verification:** a re-grep for the four names found none outside the decision record. Gates run nested
  against the existing image: `make test` (696 passed), `make format` (ruff fixed 11 import orderings; ty
  clean), `make check-generated`, `make check-regions`. `make docs` was not run; one code cell in
  `book/docs/notebooks/levels-of-abstraction.py` called `from_real`, left for the next docs build to check.
- **Version:** `pyproject.toml` stayed at 0.1.0; the breaking bump to 0.2.0 and the promotion of
  `[Unreleased]` were left to the maintainer's release step.
