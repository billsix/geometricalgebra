# Drop the dimension suffix from generated types (Vector2 → Vector, G2 → G, …)

**Status:** proposed — needs go-ahead (API-breaking; coordinate with a gacalc release + mvp)
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-08-13

## Goal

Rename **every** generated type to drop the algebra-dimension suffix, so each self-contained
`gN.py` exports unsuffixed names: `Scalar`, `Vector`, `Bivector`, `Trivector`, `Rotor`, **and
the full class `G`**. `from gacalc.g2 import Vector` is the 2-D vector, `from gacalc.g2 import G`
the 2-D full class — **the module is the namespace.** `Gn` in `gn.py` stays `Gn` (it is the
genuinely dimension-agnostic general representation — the `n` is a variable, not a fixed
dimension). This is **Option B** from the 2026-08-13 investigation.

## Decisions (Bill, 2026-08-13)

1. **Full class drops too** — `G2`/`G3` → `G` (not kept suffixed).
2. **Module-qualified repr** — override `__repr__` so it shows the module (see below); this
   recovers the dimension that a bare `Vector(...)` would lose, and is *more* aligned with the
   "module is the namespace" design than the old suffix.
3. **Version 0.0.16** (not 0.1.0).

## The generator change (small)

In `tools/gen_specialized.py`: `scalar_spec` → `TypeSpec("Scalar", …)`; `graded_specs` →
`"Vector"`/`"Bivector"`/`"Trivector"`/`"Rotor"`; **`full_name_for(dim)` → `"G"`** (drop the
`{dim}`); `generate_scalar`'s name arg in `main()` → `"Scalar"`. Everything downstream —
dispatch `case Vector():`, construction `return Rotor(...)`, overload return types, `__all__`,
doc-region marker names — falls out, because each module is self-contained (no `gN.py` imports
another dimension's types).

**Module-qualified repr.** Add `repr=False` to the `@dataclass` decorator and emit a custom
`__repr__` that bakes in the module short name (known at generation time from the filename):
`return f"g2.Vector(coeff_e_1={self.coeff_e_1!r}, coeff_e_2={self.coeff_e_2!r})"` → prints
`g2.Vector(coeff_e_1=1.5, coeff_e_2=2.0)`. So a 2-D vs 3-D value is still distinguishable in a
repr / doctest. (Trade: not eval-able under a bare `from gacalc.g2 import Vector`; fine for a
teaching library.)

## The sweep (the real work)

- **Doctests update to the module-qualified repr.** Every doctest showing a generated-type
  repr changes from `Rotor2(...)` to `g2.Rotor(...)` — `base.py` (`exp` examples), and any in
  `gn.py`/`functions.py`/`transforms.py`/`nbplotutils.py`. Run `pytest --doctest-modules`.
- **Cross-dimension collision inside gacalc → module-qualify.** `tools/bench.py` imports
  graded/full types from both g2 and g3; unsuffixed, they collide. Fix by module-qualify
  (`import gacalc.g2 as g2; g2.Vector`, `g2.G`), NOT aliasing (aliasing re-adds the suffix and
  fights the design). Check `tests/` (`test_conformance` builds `{1: G1, 2: G2, 3: G3}` → now
  `{1: g1.G, 2: g2.G, 3: g3.G}`; `test_graded`, `test_operator_typing`).
- **Doc-region markers rename** (`Vector2 __add__ method` → `Vector __add__ method`); mvp's book
  `literalinclude`s by marker name — handled in the mvp task (10 refs).
- **Docs:** `design-decisions.md`, CLAUDE.md, `tasks/reference/*` reference `Vector2`/`Rotor2`/
  `G2`/… throughout — update (mechanical but broad).

## Release & coordination

- **API-breaking → bump to 0.0.16 and cut a release BEFORE mvp adopts** (PyPI permanently
  rejects a reused version). Add a `CHANGELOG.md` entry (exercises the open
  `changelog-for-breaking-api-changes.md`).
- **mvp adoption is gated on that release** — mvp `tasks/adopt-unsuffixed-gacalc-graded-types.md`
  (the established gate-on-release pattern).

## Companion

- `tasks/reorder-generated-class-emission.md` — do together if convenient (same `main()` + name
  functions).
