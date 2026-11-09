# Relocate `rotate` to transforms.py and rename the three rotation functions

**Created:** 2026-07-16 · **Completed:** 2026-07-16

The projection-based `rotate(from, to)` classmethod was moved off `MultiVectorBase` (`base.py`) to a
free function in `transforms.py`, beside `rotor_rotation` and `plane_rotation`, so all rotation
*factories* live in one place and the algebra base keeps only the rotor *builder*
(`rotor_from_vectors`). It was renamed `projection_rotation`, and every test, notebook, docstring and
doc was updated.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-07-16)

1. **Hard-remove** `rotate` from the class API, with no deprecation shim (the alternative considered:
   a thin forwarding classmethod, kinder to external callers). mvp needed no edit:
   github.com/billsix/modelviewprojection only imported `plane_rotation` (unchanged) and defined its
   own `Vertex.rotate` / `mplt.rotate` / local `rotate = plane_rotation(...)`; a grep found no
   `rotor_rotation` and no `.rotate(from_vector=…)`.
2. **Option A** naming: `rotate` → `projection_rotation`; `rotor_rotation` and `plane_rotation` kept.
3. `rotor_from_vectors` **stayed** on `MultiVectorBase`: it builds a value, not a transform.

## Naming rationale

The old names mixed two axes. `rotate` was a bare imperative verb that returned a function rather than
rotating, clashed with the noun-phrase `*_rotation` names, and as a classmethod read as "the object
rotates itself." `rotor_rotation` was named by **formulation** (rotor sandwich), `plane_rotation` by
**spec** (plane + angle). Two functions shared the from/to spec and differed only in formulation
(projection vs rotor), so the from/to pair is disambiguated by formulation and the unique-spec one is
named by its spec — which the prose in `transforms.py` and `test_transforms.py` already did ("the
projection formulation" vs "the rotor formulation").

Rejected, **Option B** (spec-only names, e.g. `from_to_rotation` / `rotor_rotation` /
`plane_rotation`): it didn't distinguish the two from/to variants, and `from_to_rotation` is clumsier.

The four functions at the time:

| function | location | produces | formulation | spec |
| --- | --- | --- | --- | --- |
| `rotate` → `projection_rotation` | `base.py` classmethod → `transforms.py` | in-plane part turned, perp part fixed | projection | from/to |
| `rotor_from_vectors` | `base.py` classmethod | the rotor *value* `\|a\|\|b\| + b a` (a builder) | — | from/to |
| `rotor_rotation` | `transforms.py` | versor sandwich `R v R⁻¹` | rotor | from/to |
| `plane_rotation` | `transforms.py` | half-angle rotor sandwich, angle free | rotor | plane + angle |

## What was done

- `projection_rotation` in `transforms.py` derives the type from its operand
  (`type(from_vector).project(...)`), as `rotor_rotation` / `plane_rotation` do, so it stays
  representation-agnostic; it gained a doctest, joined `transforms.__all__`, and is re-exported from
  `gn.py`.
- Tests: `tests/test_multivector.py` (6 calls + import), `tests/test_conformance.py` (both calls +
  import), `tests/test_graded.py` (4 calls + header comment + import), `tests/test_transforms.py`
  (`G3.rotate` call + import). `tests/test_numeric_magnitude.py` only used `rotor_rotation` and needed
  no change.
- Notebooks: `notebooks/displayrotations.py`, `notebooks/displaygraded.py`.
- Docs: `CLAUDE.md` (Rotations & rotors, `plane_rotation`, both Convention paragraphs, which had
  required `cls.rotate(from_vector=…, to_vector=…)(v)` and were rewritten to the free-function form,
  Operators), `README.md`, the `transforms.py` module docstring and cross-refs, and the three `rotate`
  mentions in `base.rotor_from_vectors`.
- No `make generate` was needed: `rotate` was hand-written and only inherited by the generated
  classes (the generator had zero references).

## Verification

- `python -m pytest -q`: **281 passed** (doctests included).
- `ruff check` + `ruff format --check` + `ty check` clean on every touched file (pre-existing E501s in
  the untouched, in-progress `notebooks/displaymv.py` were not from this change).
- The containerized `make test` gate was not run: a pure-Python change touching no generated-code or
  flag-gated path, so the host suite exercised it fully.
