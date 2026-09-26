# Add missing docstrings to base/gn, and give every generated method a docstring

**Status:** complete (2026-09-26, branch `docstrings`; author William Emerison Six
<billsix@gmail.com>). Created 2026-07-21. **Priority:** 6 **Difficulty:** 5

## BLUF

Every `MultiVectorBase`/`Gn` method that lacked a docstring got one, and the code generator
was extended so every method of every generated class (`G` and the graded subtypes) also
carries a docstring — grade-aware, student-facing text with executable doctests for the dev
dims g1–g3, and the copied base docstring elsewhere. The durable mechanism and conventions
live in `tasks/reference/generated-docstrings.md`; this doc is the work record.

## What was done

**Part 1 — base/gn docstrings.** Authored a house-voice (Hestenes) docstring on every
previously-undocumented method: in `base.py` the constructors/classmethods (`from_scalar`,
`from_coef`, `zero`, `one`, `bases`, `symbolic_multivector`, `unit_pseudoscalar_squared`),
the operators (`__mul__`, `__rmul__`, `__add__`, `__radd__`, `__sub__`, `__neg__`, `__abs__`),
`dot`, the grade predicates (`is_vector`/`is_bivector`/`is_trivector`), `grades`/`max_grade`,
and `_repr_latex_`; in `gn.py`, `__post_init__`, `from_blade_dict`, `to_blade_dict`,
`_geometric_product`, and `BladeDictionaryEntry.as_multivector`. An AST audit confirmed 100%
coverage. (Committed by the maintainer in `b0be7ad`.)

**Part 2 — every generated method gets a docstring.** Added a single post-build pass
(`inject_method_docstrings` in `tools/gen_specialized.py`) that gives each generated method a
docstring; `@overload` stubs stay bare. For g1–g3 a `CUSTOM_METHOD_DOCS` table (keyed
`role|method`, values literal text or `(role, n)` callables) supplied **broad, grade-aware**
docstrings for every method of every graded role (scalar/vector/bivector/trivector/rotor/odd),
with doctests wherever an example teaches (products, `dual`, projection/rejection, `exp`→rotor,
`cross`, the 𝒢₂ quarter turn, the rotor `sandwich`, the `Odd_3` conversions, `reverse`, …).
Methods with no custom entry, and all dims ≥ 4, fall back to the copied base/`Gn` docstring.

## Decisions and findings (harvested)

- **Open question — resolved:** generated methods with no base counterpart to copy (the
  `@overload` stubs, the scalar-aware `__rsub__`/`__eq__` wrappers) get a generated one-liner,
  except the `@overload` stubs, which stay bare (they never render — a refinement of the
  original "one-liner on stubs" answer).
- **Scope — resolved:** the maintainer chose **broad** specialization (a grade-aware docstring
  on essentially every graded method), because the abstract base text is too abstract for the
  students the specialized g1/g2/g3 classes are meant to teach.
- **`inspect.getdoc` inherits through the MRO**, so generated overrides already surfaced the
  base docstring in rendered autodoc; the payoff of this work was therefore grade-specific
  content, executable doctests, and self-documenting generated source — not fixing broken docs.
- **Doctest conventions** (maintainer's calls): explicit unit coefficients (`1 * Vector.e_1`,
  including sum terms and product operands; bare only for *direction* args); typed comparisons,
  never bare Python numbers (`== Scalar.from_scalar(-1)`, since a multivector never `==` a bare
  number — see `tasks/reference/symbolic-equality.md`); type **annotations** on locals for
  readability (`R: Rotor = …`), not `type()` assertions. Type-narrowing stays tested in the unit
  tests (`tests/test_operator_typing.py`, `test_odd3.py`, `test_exp.py`), which already covered
  the facts the doctests illustrate — no gaps found.
- **`tools/gen_specialized.py` was made E501-exempt** (`pyproject.toml` per-file-ignores): it is
  now largely docstring-content string literals `ruff format` cannot reflow. `base.py`/`gn.py`
  docstrings are not exempt and stay ≤ 88 cols.

## Verification

All containerized gates green (2026-09-26): `make format` (ruff + ty + changelog),
`make test` (**649 passed**, +153 doctests over the pre-docstring 496), `make check-generated`
(deterministic), `make check-regions` (OK).

## Possible follow-ups (not required)

- Enrich the full-class `G` docstrings (currently generic base copies — appropriate for the
  general representation).
- Add doctests to the remaining prose-only custom entries.

## Relationships

- Mechanism and conventions: `tasks/reference/generated-docstrings.md`.
- Generator internals: `tasks/reference/code-generator-architecture.md`.
- Sibling task `docstrings-for-sphinx.md` (still open) owns the hand-written-module sweep
  (`transforms.py`/`nbplotutils.py`/`functions.py`) and the autodoc rendering fixes
  (`|A|` RST-escaping, the `ₙ` glyph) — NOT done here.
