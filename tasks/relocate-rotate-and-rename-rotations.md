# Relocate `rotate` to transforms.py and rename the three rotation functions

**Status:** proposed — needs go-ahead
**Started:** 2026-07-16

## Goal

Move the projection-based `rotate(from, to)` off `MultiVectorBase` (where it sits
as a classmethod in `base.py`) and make it a free function in `transforms.py`,
alongside the two rotation functions that already live there (`rotor_rotation`,
`plane_rotation`) — so all rotation *factories* live in one place and the algebra
base is left with just the rotor *builder* (`rotor_from_vectors`). Then rename the
three rotation functions to a consistent scheme, and update every test, notebook,
docstring, and doc (incl. `CLAUDE.md` / `README.md`) that references them.

## Background — the current four functions

| function | location | signature | what it produces | formulation | spec |
| --- | --- | --- | --- | --- | --- |
| `rotate` | `base.py` (classmethod) | `(from, to) -> MultiVectorFn` | in-plane part turned, perp part fixed | **projection** | from/to vectors |
| `rotor_from_vectors` | `base.py` (classmethod) | `(from, to) -> MultiVectorBase` | the rotor *value* `\|a\|\|b\| + b a` | — (a **builder**, not a rotation fn) | from/to vectors |
| `rotor_rotation` | `transforms.py` | `(from, to) -> InvertibleFunction` | versor sandwich `R v R⁻¹` | **rotor** | from/to vectors |
| `plane_rotation` | `transforms.py` | `(a, b) -> (θ -> InvertibleFunction)` | half-angle rotor sandwich, angle free | **rotor** | plane + angle |

The **three rotation functions** the user means are `rotate`, `rotor_rotation`,
`plane_rotation` (the ones that yield a rotation). `rotor_from_vectors` is a rotor
*builder* returning a multivector — it stays in `base.py` (it's algebra, produces a
value) and is out of scope for the rename except where prose references it.

## Plan

- [ ] Move `rotate` from `MultiVectorBase` (`base.py`) to a free function in
      `transforms.py`. Body currently calls `cls.project(plane)` / `cls.reject(plane)` /
      `cls.identity`; as a free function it derives the type from the operand's own
      type (`type(from_vector).project(...)`), exactly as `rotor_rotation` /
      `plane_rotation` already do — so it stays representation-agnostic (`Gn`/`G1`/`G2`/`G3`).
- [ ] Re-export from `gn.py` (which already re-exports `plane_rotation`, `rotor_rotation`)
      so `from gacalc.gn import <name>` keeps working; add to `transforms.__all__`.
- [ ] Decide final names (see **Naming** below) and apply.
- [ ] Update tests: `tests/test_multivector.py` (6 `MultiVector.rotate` calls, ~L430–456),
      `tests/test_conformance.py` (L192–193, `cls.rotate` / `Gn.rotate`),
      `tests/test_graded.py` (L317, 329, 339, 346, `*.rotate`), `tests/test_transforms.py`
      (L416–421, `test_rotor_rotation_matches_projection_rotate` + `G3.rotate`),
      `tests/test_numeric_magnitude.py` (imports `rotor_rotation`).
- [ ] Update notebooks: `notebooks/displayrotations.py` (L38, 95, 98, 132 — `Gn.rotate`),
      `notebooks/displaygraded.py` (L169, 177 — `Vector2.rotate`).
- [ ] Update docs/prose: `CLAUDE.md` (the "base.rotate is projection-based" paragraph and
      the two **Convention** paragraphs that mandate `cls.rotate(from_vector=…, to_vector=…)(v)`),
      `README.md` (the graded-subtypes section mentioning `rotate(from, to)`), and the
      `transforms.py` module docstring (L30–40) + the cross-references inside
      `rotor_rotation` / `plane_rotation` docstrings that point at `MultiVectorBase.rotate`.
- [ ] `make generate` is **not** needed — `rotate` is hand-written in `base.py`, not generated.
      But regenerate + `make test` to confirm nothing downstream broke, and re-run
      `entrypoint/format.sh` (ruff + ty) which must stay clean.

## Naming — analysis and suggested replacements

The three names today mix two different axes and don't signal which functions are
siblings:

- `rotate` — a bare **imperative verb**, but it doesn't rotate; it *returns a function*
  that rotates. It clashes stylistically with the two noun-phrase `*_rotation` names,
  and `rotate` vs `rotor` is easy to misread. As a classmethod it also reads as "the
  object rotates itself," which it doesn't.
- `rotor_rotation` — named by **formulation** (uses a rotor sandwich). Same from/to spec
  as `rotate`.
- `plane_rotation` — named by **spec** (what defines the plane). Uses the rotor
  formulation internally, so it *can't* be named "rotor_…" without collision.

Two functions share the **from/to** spec and differ only in **formulation**
(projection vs rotor); the third has a unique **plane+angle** spec. The clean
resolution: within the shared from/to spec, disambiguate by formulation; the
unique-spec one is named by its spec. That's exactly what the prose already does —
`transforms.py` and `test_transforms.py` already call `rotate` "the **projection**
formulation" and contrast it with "the **rotor** formulation."

**Recommended (Option A — minimal, aligns with existing prose):**

| current | → suggested | rationale |
| --- | --- | --- |
| `rotate` | **`projection_rotation`** | from/to spec, projection formulation; sibling to `rotor_rotation`; matches existing "projection formulation" wording and the test name `..._matches_projection_rotate` |
| `rotor_rotation` | **keep** `rotor_rotation` | from/to spec, rotor formulation |
| `plane_rotation` | **keep** `plane_rotation` | plane+angle spec |

Result: `projection_rotation(from, to)` and `rotor_rotation(from, to)` read as the
two from/to formulations; `plane_rotation(a, b)` is the plane/angle one. All three are
free functions in `transforms.py`, all noun-phrase `*_rotation`.

**Alternative (Option B — full spec-based naming), for discussion:** rename by
*specification* only — e.g. `from_to_rotation` (projection) / `rotor_rotation` (rotor) /
`plane_rotation`. Weaker: it doesn't distinguish the two from/to variants, and
`from_to_rotation` is clumsier than `projection_rotation`.

I recommend **Option A**.

## Notes / decisions

- Moving `rotate` out of the base is a genuine public-API change: today it's callable on
  every class (`Vector3.rotate(...)`, `Gn.rotate(...)`). After the move it's a free function
  — the **Convention** blocks in `CLAUDE.md` that require rotations to read as
  `cls.rotate(from_vector=…, to_vector=…)(v)` must be rewritten to the new free-function form.
- `rotor_from_vectors` (the rotor *builder*) stays on `MultiVectorBase` — it returns a
  multivector value, not a rotation function; only prose references need touching.

## Open questions

- Go/no-go on **removing** `rotate` from the class API entirely vs. leaving a thin
  deprecated classmethod shim that forwards to the new free function (kinder to any
  external caller / the mvp book project that shares `transforms.py`).
- Confirm the naming choice: **Option A** (`projection_rotation`) as recommended, or Option B?
- Should `rotor_from_vectors` also migrate for symmetry, or stay in `base.py` as algebra?
  (Recommendation: stay — it builds a value, not a transform.)
