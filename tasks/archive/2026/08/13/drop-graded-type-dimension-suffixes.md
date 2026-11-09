# Drop the dimension suffix from generated types (Vector2 → Vector, G2 → G, …)

**Created:** 2026-08-13 · **Completed:** 2026-08-13

Renamed **every** generated type to drop the algebra-dimension suffix, so each self-contained
`gN.py` exports `Scalar`, `Vector`, `Bivector`, `Trivector`, `Rotor`, and the full class `G`:
`from gacalc.g2 import Vector` is the 2-D vector; **the module is the namespace.** `Gn` in `gn.py`
stayed `Gn` (the `n` is a variable, not a fixed dimension). This was Option B from the 2026-08-13
investigation.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-13)

1. **The full class drops its suffix too:** `G2`/`G3` → `G`.
2. **Module-qualified repr:** `__repr__` shows the module (`g2.Vector(coeff_e_1=1.5,
   coeff_e_2=2.0)`), recovering the dimension a bare `Vector(...)` would lose, and fitting "the
   module is the namespace" better than the suffix. Trade-off accepted: the repr is not eval-able
   under a bare `from gacalc.g2 import Vector`, which is fine for a teaching library.
3. **Version 0.0.16** (not 0.1.0).

## What changed

- **Generator** (`tools/gen_specialized.py`): `scalar_spec` → `"Scalar"`; `graded_specs` →
  `"Vector"`/`"Bivector"`/`"Trivector"`/`"Rotor"`; `full_name_for(dim)` → `"G"`. Dispatch cases,
  constructors, overload return types, `__all__` and doc-region marker names followed, since no
  `gN.py` imports another dimension's types. The `@dataclass` got `repr=False` and an emitted
  `__repr__` baking in the module short name; `base` got the module-qualified `__repr__` too.
- The companion reorder (`tasks/archive/2026/08/13/reorder-generated-class-emission.md`) was
  bundled in (same `main()` + name functions).
- **Tests and `tools/bench.py`** were module-qualified (`import gacalc.g2 as g2; g2.Vector`), not
  aliased: aliasing would re-add the suffix and fight the design (e.g. `test_conformance`'s
  `{1: G1, 2: G2, 3: G3}` became `{1: g1.G, 2: g2.G, 3: g3.G}`). Done with a codemod,
  `codemod.py` (removed at archive; in git history).
- **Doctests** in `src` were updated to the module-qualified repr.
- **Prose** across `src` and the docs (`tasks/reference/design-decisions.md`, CLAUDE.md,
  `tasks/reference/*`) was swept with `prose_codemod.py` (removed at archive; in git history). It
  needed a second pass for single- vs double-backtick markdown enumerations (the
  `` `G`/`G`/`G` `` collapse); the first pass only handled the double-backtick rst/docstring style.
- Notebooks module-qualified; doc-region markers renamed (`Vector2 __add__ method` →
  `Vector __add__ method`), whose 10 mvp `literalinclude` references were left to the mvp task.
- Version bumped to **0.0.16** with a `CHANGELOG.md` entry (PyPI rejects a reused version, so the
  release had to precede mvp's adoption).

## Verification

ruff, ty, 348 tests, and generation determinism all green; no leftover suffixed names.

## Left to others

The release itself (`make release` / `git tag`) was the maintainer's. mvp adoption was gated on
that release, in
github.com/billsix/modelviewprojection `tasks/archive/2026/08/13/adopt-unsuffixed-gacalc-graded-types.md`.
