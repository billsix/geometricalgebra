# Why don't the generated graded subtypes (and `Scalar`) have `slots=True`?

**Status:** complete (2026-06-27) — `slots=True` added to the graded subtypes + `Scalar`; verified.
Ready to archive.
**Proposed:** 2026-06-27
**Completed:** 2026-06-27

## Done (2026-06-27)

Changed the generator (`tools/gen_specialized.py`) so `generate_graded_type` (~L1630) and
`generate_scalar` (~L1190) emit `dataclass_decorator(eq=False, slots=True)` (matching `generate_class`).
Regenerated; verified `Vector2`/`Bivector2`/`Rotor2`/`Scalar` now have `__slots__` and **no per-instance
`__dict__`**, basis class-constants still resolve, arithmetic/`coefficient()` still work. Gates green:
`ruff` + `ty check src tools` clean, `make`-style determinism (regen twice → identical), full suite
**246 passed**. As predicted this is a *behavioral* generator change (the decorator line differs from the
old output), so it is **not** byte-identical to the pre-change baseline — that's expected, and the
determinism + test gates are what cover it.

## Question

`Gn` and the full specialized classes `G1`/`G2`/`G3` are `@dataclass(slots=True)`, but the generated
**graded subtypes** (`Vector_n`/`Bivector_n`/`Trivector3`/`Rotor_n`) and the shared **`Scalar`** are
only `@dataclass(eq=False)` — **no slots**. Why, and should they be slotted too?

## Findings (empirical, 2026-06-27)

Generated with `python tools/gen_specialized.py`, then inspected at runtime:

| class | decorator | instance has `__dict__`? |
| --- | --- | --- |
| `Gn` (gn.py) | `dataclass(slots=True)` | no |
| `G1`/`G2`/`G3` (full) | `dataclass(eq=False, slots=True)` | no |
| `Vector2`/`Bivector2`/`Rotor2` (graded) | `dataclass(eq=False)` | **yes** (per-instance dict) |
| `Scalar` | `dataclass(eq=False)` | **yes** |

Where the decorators are emitted in `tools/gen_specialized.py`:
- full classes — `generate_class`, ~line 1292: `dataclass_decorator(eq=False, slots=True)`
- graded subtypes — `generate_graded_type`, ~line 1536: `dataclass_decorator(eq=False)`  ← no slots
- `Scalar` — `generate_scalar`, ~line 1100: `dataclass_decorator(eq=False)`  ← no slots

## Analysis — why the asymmetry exists

**It is a historical oversight, not a technical blocker.**

- `slots=True` was introduced in commit `4d6380a` ("upated using match"), back when the generator
  still emitted source as **strings** (`ap("@dataclasses.dataclass(eq=False, slots=True)")`) and **only
  the full classes existed**.
- The **graded subtypes + `Scalar` were added later** (see
  `tasks/archive/2026/06/06/graded-blade-subtypes.md`) and were written with just `eq=False`; the
  `slots=True` flag was simply never carried over to the new generators.

**There is no inheritance/slots conflict.** All generated classes (full, graded, and `Scalar`)
inherit from `MultiVectorBase` — which has `__slots__ = ()` precisely so slotted subclasses don't
inherit a `__dict__` (base.py:84–86). The graded subtypes do **not** inherit from the full classes
(verified: `cls()` defaults the base to `MultiVectorBase`), so there's no "duplicate slot for
`coeff_e_1`" problem.

**The full classes already prove every ingredient is slots-compatible.** `G1`/`G2`/`G3` combine, with
`slots=True` and passing tests, exactly what the graded subtypes have:
- the `MultiVectorBase` base with empty `__slots__`,
- `coeff_*` dataclass fields (with numeric defaults),
- basis blades declared as `ClassVar` in the body (excluded from `__slots__`) plus post-class
  `Cls.e_1 = Cls.from_blade_dict(...)` assignments — class-attribute writes are unaffected by slots,
- zero-arg `super().method(...)` calls (the `slots=True` + zero-arg-`super()` CPython bug was fixed in
  3.11; the project runs Python 3.14).
The graded subtypes are a structural **subset** of this, so `slots=True` works for them unchanged
(confirmed by building a slotted `MultiVectorBase` subclass with the graded layout — `__slots__` held
only the `coeff_*` fields, the class-constant placeholder was excluded, class-const assignment worked).

## Recommendation

**Add `slots=True` to the graded-subtype and `Scalar` generators** so every generated value type is
slotted, matching `Gn` and the full classes.

- Benefits: removes the per-instance `__dict__` (lower memory + faster attribute access) for the
  value types most likely created in bulk (numeric pipelines, plotting, mvp rotations); and it makes
  the generated family internally consistent.
- Cost/risk: low. Slots forbid setting *undeclared instance attributes* — desirable for immutable
  value types, and the codebase already relies on this for the full classes. No API change.
- One caveat worth a sentence in the task: this is a *behavioral* generator change, so the generated
  output **will differ** from the old baseline (the decorator line changes) — unlike a pure
  byte-identity-preserving refactor. `make check-generated` (determinism) must still pass, and the
  full suite must stay green; but do **not** expect a zero diff vs. the previous generation.

## Plan (once approved)

- [ ] In `tools/gen_specialized.py`: change `generate_graded_type`'s decorator (~1536) and
      `generate_scalar`'s (~1100) from `dataclass_decorator(eq=False)` to
      `dataclass_decorator(eq=False, slots=True)`.
- [ ] `make generate` (or `python tools/gen_specialized.py`); spot-check that `Vector2`/`Scalar`
      instances no longer have `__dict__` and the basis class-constants still resolve.
- [ ] `make test` (full suite incl. conformance + graded + doctests) green.
- [ ] `make check-generated` (regenerate twice, byte-identical) green.
- [ ] `ruff` + `ty check src tests` clean.
- [ ] Optional: a one-line note could go under CLAUDE.md "Architecture" that *all* generated value
      types (full + graded + `Scalar`) are slotted — but the current text doesn't claim otherwise, so
      likely no doc change needed.

## Notes / cross-refs

- `tasks/archive/2026/06/06/graded-blade-subtypes.md` — where the graded subtypes were introduced
  (and where slots was not carried over).
- Per CLAUDE.md "Code generation": the fix is a `tools/` edit only; the regenerated `g*.py`/`scalar.py`
  are gitignored, so a correct change shows as a `tools/gen_specialized.py` diff with nothing under
  `src/gacalc/` in git.
