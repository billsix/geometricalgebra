# Add missing docstrings to base/gn, and give every generated method a docstring

**Created:** 2026-07-21 · **Completed:** 2026-09-26 (branch `docstrings`, squashed into `c77e62a`;
author William Emerison Six <billsix@gmail.com>)

Every `MultiVectorBase`/`Gn` method that lacked a docstring got one, and the code generator was
extended so every method of every generated class (`G` and the graded subtypes) also carries one —
grade-aware, student-facing text with executable doctests for the dev dims g1–g3, and the copied base
docstring elsewhere. The durable mechanism and conventions live in
`tasks/reference/generated-docstrings.md`; this doc is the work record.

## What was done

**Part 1 — base/gn docstrings.** A house-voice (Hestenes) docstring on every previously undocumented
method: in `base.py` the constructors/classmethods (`from_scalar`, `from_coef`, `zero`, `one`,
`bases`, `symbolic_multivector`, `unit_pseudoscalar_squared`), the operators (`__mul__`, `__rmul__`,
`__add__`, `__radd__`, `__sub__`, `__neg__`, `__abs__`), `dot`, the grade predicates, `grades` /
`max_grade`, and `_repr_latex_`; in `gn.py`, `__post_init__`, `from_blade_dict`, `to_blade_dict`,
`_geometric_product`, and `BladeDictionaryEntry.as_multivector`. An AST audit confirmed 100% coverage.

**Part 2 — every generated method gets a docstring.** One post-build pass,
`inject_method_docstrings` in `tools/gen_specialized.py`, gives each generated method a docstring. For
g1–g3 a `CUSTOM_METHOD_DOCS` table (keyed `role|method`, values literal text or `(role, n)` callables)
supplies grade-aware docstrings for every method of every graded role (scalar / vector / bivector /
trivector / rotor / odd), with doctests wherever an example teaches (products, `dual`,
projection/rejection, `exp` → rotor, `cross`, the 𝒢₂ quarter turn, the rotor `sandwich`, the `Odd_3`
conversions, `reverse`, …). Methods with no custom entry, and all dims ≥ 4, fall back to the copied
base/`Gn` docstring.

## Decisions and findings

- **Methods with no base counterpart** (the scalar-aware `__rsub__`/`__eq__` wrappers) get a
  generated one-liner; the `@overload` stubs stay bare because they never render (a refinement of the
  original "one-liner on stubs" answer).
- **Broad specialization** (the maintainer's choice): a grade-aware docstring on essentially every
  graded method, because the abstract base text is too abstract for the students the g1/g2/g3 classes
  teach.
- **`inspect.getdoc` inherits through the MRO**, so generated overrides already surfaced the base
  docstring in autodoc; the payoff was grade-specific content, executable doctests and
  self-documenting generated source, not fixing broken docs.
- **Doctest conventions** (the maintainer's calls): explicit unit coefficients (`1 * Vector.e_1`,
  including sum terms and product operands; bare only for direction args); typed comparisons, never
  bare Python numbers (`== Scalar.from_scalar(-1)`, since a multivector never `==` a bare number —
  `tasks/reference/symbolic-equality.md`); annotations on locals (`R: Rotor = …`) rather than
  `type()` assertions. Type narrowing stays tested in `tests/test_operator_typing.py`,
  `test_odd3.py` and `test_exp.py`, which already covered the facts the doctests illustrate.
- **`tools/gen_specialized.py` was made E501-exempt** (`pyproject.toml` per-file-ignores): it is
  largely docstring string literals `ruff format` cannot reflow. `base.py`/`gn.py` stay ≤ 88 columns.
- Left as optional follow-ups: richer full-class `G` docstrings (generic base copies suit the general
  representation) and doctests for the remaining prose-only custom entries.
- The hand-written-module sweep (`transforms.py` / `nbplotutils.py` / `functions.py`) and the autodoc
  rendering fixes (`|A|` RST escaping, the `ₙ` glyph) were not done here; they were the sibling
  `tasks/archive/2026/09/26/docstrings-for-sphinx.md`, completed the same day.

## Verification

All containerized gates green (2026-09-26): `make format` (ruff + ty + changelog), `make test` (649
passed, +153 doctests over the previous 496), `make check-generated`, `make check-regions`. Generator
internals: `tasks/reference/code-generator-architecture.md`.
