# Why `Vector2.e_1` is `0` (not the basis vector) — and should it be?

**Created:** 2026-06-07 · **Completed:** 2026-06-07

## The observation

In the author's shell, on a generated `G2` build, `gacalc.g2.Vector2.e_1` evaluated to `0` (so
`5 * Vector2.e_1 + 3 * Vector2.e_2` was `0`); only `Vector2.basis_vector(1)` gave the basis vector. The
author expected `Vector2.e_1` to be that basis vector.

## Findings

- **Mechanism.** `Vector2` was a plain `@dataclass` whose coefficient fields were named after the basis
  blades (`e_1: numbers.Real = typing.cast(numbers.Real, 0)`). On an instance `e_1` is the coefficient;
  on the class it is the field default leaking through — standard dataclass behaviour, not a designed
  value.
- **Nothing used it.** A search of `src`, `tests`, `tools` and `notebooks` found only instance field
  access in generated methods, the module-level constants (`g2.e_1`, typed `G2`, not `Vector2`), and
  `Vector2.basis_vector(1)` (the only `Vector2`-typed basis vector; `test_graded.py` built
  `E1, E2` that way).
- **Name collision.** The coefficient field occupied the name `e_1`, so the field default could not
  become the basis vector (every partially-constructed value would get a vector as a coefficient), and
  splitting class vs instance access would need a generated descriptor or metaclass, which was judged
  surprising machinery.

## Decision (the author, 2026-06-07)

Free the `e_n` names: rename the coefficient fields to `coeff_*`; then a plain class-level constant
`e_1` serves both `Cls.e_1` and `inst.e_1` with no descriptor. Users read components through the
algebra — `component(blade)` (scalar) and `project(blade)` (blade-valued) — which works identically on
`Gn` (no named fields) and the specialized classes, making `coeff_*` pure storage. The blast radius was
contained because every cross-representation interaction goes through the blade-dict interchange (keyed
by blade tuples, not field names) and the module-level constants; the observable changes were the
dataclass `repr` and the constructor kwargs. The three phases were done in order, with the author
committing between them. Two questions were settled: the scalar field became `coeff_scalar` too, for
uniformity; and the `component` fix (Phase 3) stayed in this task, since the rename is what made
`component` the primary user path.

## Phase 1 — coefficient fields renamed to `coeff_*` (commit `9e28603`)

All in `tools/gen_specialized.py`, across `G1/G2/G3`, the graded subtypes and `Scalar`:

- The overloaded `field_name` was split: `blade_label(blade)` → `e_1`/`e_12`/`scalar` (docstrings and
  the internal cse symbol names `a_e_1`/`b_e_1`), and `field_name(blade)` → `coeff_e_1`/`coeff_scalar`
  (the dataclass field). `blade_of_field` became `blade_of_label`. `rename_map` maps the label symbol
  `a_e_1` to the attribute `self.coeff_e_1`.
- Hardcoded `"scalar"` field literals became `field_name(())`; non-field uses of `"scalar"` (TypeSpec
  `kind`, grade words, the label) were left alone.
- The module-level public constants (`g2.e_1` and `__all__`) kept their `blade_label` names.
- Docstrings changed "stored as named fields: e_1, e_2" to "basis blades: e_1, e_2".

A sweep confirmed `tests/`, `notebooks/`, `README.md` and `tools/bench.py` used only module constants,
`basis_vector(n)` and the blade-dict protocol, and `base.py`/`gn.py` are field-name-agnostic. 161 tests
passed; `ty`, `ruff` and `make check-generated` were clean.

## Phase 2 — `e_1`, `e_2`, `e_12`, … became class constants

Each generated class (`G1/G2/G3` and the graded subtypes) got a constant of its own type for each of its
nonempty blades, so `Vector2.e_1 == Vector2.basis_vector(1)` and `inst.e_1` falls through to the same
constant. Two generator helpers: `basis_classvar_decls(name, blades)` emits `e_1: typing.ClassVar[Name]`
in the class body (excluded from fields/`__slots__`, visible to `ty`), and
`basis_constant_assignments(name, blades)` emits `Name.e_1 = Name.from_blade_dict({(1,): 1})` after the
class, which cannot reference itself mid-definition. Both `generate_class` (`slots=True`) and
`generate_graded_type` use them.

Decisions: constants are per type (`G2.e_1` is a `G2`, `Bivector2.e_12` a `Bivector2`); they coexist
with the untouched module-level constants; `Scalar` gets none; **`Gn` gets none** on purpose, being
dimension-agnostic (users use `gn.e_1` or `Gn.basis_vector(n)`; nothing assumed `Gn.e_1`). README
"Graded subtypes", CLAUDE.md "Architecture" and `notebooks/displaygraded.py` were updated; new tests
`test_basis_blade_class_constants` and `test_basis_constant_instance_fallthrough`. 163 tests passed;
`ty`, `ruff` and `make check-generated` were clean.

## Phase 3 — `component` fixed as the grade-general getter

`AbstractMultiVector.component(x)` had been `self.dot(x).scalar_part()` with a "TODO - is this really
how I should define it?" comment: right for vectors, sign-wrong for grade ≥ 2 (`e_12 · e_12 == −1`). It
became `(self * x.reverse()).scalar_part()` (Hestenes' α_J = ⟨A ẽ_J⟩; reverse equals inverse for unit
Euclidean blades), with a real docstring saying `x` must be a unit basis blade and pointing to `project`
for the blade-valued part. Being in the ABC and overridden nowhere, the one change covered `Gn`, `G1/G2/G3`
and every graded subtype.

`component` had been untested, which is why the bug hid. New tests: `test_component` in
`test_conformance.py` (over `[Gn, G1, G2, G3]`, n = 1..3, every blade incl. the grade-≥2 sign and the
reconstruction `Σ_b component(b)·b == x`) and `test_component_reads_coefficients` in `test_graded.py`.
CLAUDE.md known-issue #2 dropped `component`; the README quick-start shows `a.component(e_1)`. 170 tests
passed; `ty` and `ruff` were clean.
