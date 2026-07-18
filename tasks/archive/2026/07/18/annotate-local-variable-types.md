# Add type annotations to local variables & untyped functions

**Status:** complete
**Completed:** 2026-07-18 — ty clean on src/tests/tools, 285 tests pass. Code
changes are in the working tree (Bill to commit).
**Created:** 2026-07-18
**Audited:** 2026-07-18 (AST audit over every hand-written `.py`; results below)

## Outcome / decisions (2026-07-18)

Implemented across notebooks, tests, `tools/bench.py`, `setup.py`, and the
`src/gacalc/` hand-written core (19 files). Gate: `make format` → **ty clean on
src, tests, tools**; `make test` → **285 passed**. Ruff adds **zero** new errors
(the 6 `E501` it reports are pre-existing prose lines in `notebooks/displaymv.py`,
byte-identical to HEAD — left untouched; see open question below). Notable calls
made while getting the gate green — each is a small *standard* worth codifying in
the new style-standard task:

- **`from_blade_dict` param → `Mapping[tuple[int, ...], Coef]`, not `BladeCoef`
  (`dict`).** `dict` is *invariant* in its value type, so callers passing
  `dict[..., Symbol]` were rejected; the method only reads the mapping, so the
  covariant `Mapping` supertype is correct (ty even suggests it). Fixed in
  `base.py` + `gn.py`.
- **`__iter__` deliberately left unannotated.** Typing it `Generator[Coef]` makes
  ty treat a multivector as a destructurable iterable, so the `case [*sequence]:`
  patterns in `project`/`reject`/`reflect` then also match a lone multivector and
  widen the bound element type — a false positive (a multivector isn't a `Sequence`
  at runtime). Rather than touch that self-flagged-uncertain control flow, the
  annotation was dropped with an explanatory comment. *(Standard: don't fight the
  checker; a correct annotation that forces edits to unrelated logic isn't worth
  it in a readability pass.)*
- **Reused-name locals stay unannotated** (`bench.py` `sa`/`sb`): they're assigned
  a `Gn` then later a `MultiVectorBase`, so a single declared type can't cover both
  — flow inference handles it; annotating breaks it.
- **Polymorphic-over-`cls` locals typed `MultiVectorBase`** (tests), never a
  concrete class; parametrized `cls` params and the `to()` helper's *return* left
  unannotated to preserve the gradual typing that dimension-defaulting calls
  (`dual()`, `unit_pseudoscalar()`) rely on.
- **`_same_value` (test_conformance) wrapped in `sympy.sympify(...)`** to mirror the
  sibling `simplify_equal` (test_graded) — once its params were typed, `Coef`
  arithmetic no longer matched `sympy.simplify`'s overloads.
- **`nbplotutils.py` plotting locals intentionally skipped** — matplotlib artist
  glue, no GA/pedagogical value.
- **Notebooks:** annotated helper sigs + only the display locals whose GA *type* is
  the teaching point; scratch/string-table locals skipped.

## Goal

`ty check src`, `tests`, and `tools` are already fully clean — but ty (like all
Python type checkers) *infers* local-variable types and does not require them to
be spelled out. So a "clean" tree still has a lot of code where the annotations
live only in the checker's head, not on the page. The ask: **add explicit type
annotations where they aid readability** — to local variables that are currently
un-annotated, and to functions whose signatures are missing types. The
`notebooks/` folder is the clearest example, but the audit found gaps in
`tests/`, `tools/`, `setup.py`, **and the hand-written `src/gacalc/` core** too.

This is a **readability / pedagogy** pass, not a correctness fix — the tree
already type-checks. gacalc is a teaching library; explicit types on the demo
notebooks and reference code make the *shapes* of geometric-algebra values
(`Vector2`, `Rotor2`, `Bivector3`, `ComposableFunction[...]`, …) visible to a
reader instead of implicit.

## Audit findings (2026-07-18)

Ran an `ast`-based audit (`scratchpad/audit.py`) over every hand-written file for
(a) function params with no annotation, (b) functions with no `-> return`, and
(c) bare `name = ...` local assignments. **Two assumptions in the first draft of
this doc were wrong** and are corrected here.

**Important caveat on the raw local counts below:** the "un-annotated assign"
tallies include module-level things that should *not* be annotated — type aliases
(`Coef`, `BladeCoef`, `MultiVectorFn`, `_OperandT`), `__all__`, `__slots__`,
loop targets — so the genuinely-annotatable local set is smaller than the raw
number and needs judgment, not a blanket pass. Counts are an upper bound.

### Generated modules — out of scope

`g1/g2/g3.py`, `scalar.py` are code-generated and gitignored. Any change to their
local-var style is a `tools/gen_specialized.py` edit and a **separate** task; do
not touch the emitted files.

### notebooks/ — the headline example (untyped helper sigs + display locals)

| file | untyped params | missing `->` | bare locals (raw) |
| --- | --- | --- | --- |
| `displaygraded.py` | `kind(x)`, `show(*values)` | `kind`, `show` | 22 |
| `displaymv.py` | `rotate(angle)` | `rotate` | 14 |
| `displayg2.py` | `rotate(angle)` | `rotate` | 23 |
| `displayg3.py` | — | — | 18 |
| `displayrotations.py` | — | — | 19 |

Caveat — these are **jupytext percent-format notebooks, not plain modules**:
annotations must stay valid as notebook cells, must not break the `# %%` cell
structure or the `.ipynb` round-trip, and shouldn't pull in imports solely to
annotate a throwaway display local. The display locals whose GA *type* is the
teaching point (`Vector2` vs `Rotor2` vs `Bivector2`) are the high-value targets;
scratch locals (`header`, `sep`, `rows`, `cos`, `sin`) are low-value.

### tests/ — CORRECTION: `-> None` is NOT already universal; it's split per-file

The first draft claimed test functions are "typically `-> None` already." **False.**
It's inconsistent *by file* — some authors annotated, some didn't:

| file | test defs | missing `-> None` | note |
| --- | --- | --- | --- |
| `test_transforms.py` | 44 | **44** | none annotated; also 4 untyped params, ~75 bare locals |
| `test_generator.py` | 21 | **21** | none annotated |
| `test_graded.py` | 23 | **20** | mostly bare; `widen(x)`/`simplify_equal(a,b)` untyped |
| `test_numeric_magnitude.py` | 4 | **4** | none annotated |
| `test_conformance.py` | 34 | 1 | already annotated (the 1 is a helper); `scalar_eq`/`_same_value` params bare |
| `test_multivector.py` | 24 | 1 | already annotated; `planewise_wedge(...)` params bare |
| `test_subclass_preservation.py` | 9 | 1 | already annotated |
| `test_plane_rotation.py` | 16 | 0 | fully annotated ✅ |
| `test_vector_ergonomics.py` | 9 | 0 | fully annotated ✅ |

So a concrete, mechanical sub-goal emerges: **make test-function `-> None`
consistent** across the 4 files that lack it (a well-defined, low-risk edit),
independent of the fuzzier local-variable pass. Locals in tests: many come from a
`vec(cls, *coords)` helper returning `MultiVectorBase`; for tests parametrized
over `cls`, the honest local annotation is the base `MultiVectorBase` (its
concrete type varies per param).

### tools/bench.py + setup.py — low-risk

- `bench.py` — function *signatures already fully typed*; only ~18 bare locals
  (`idx`, `speedup`, `cls`, `sa`, `t_typed`, …). Good warm-up.
- `setup.py` — one bare return: `build_py_with_codegen.run(self)` → `-> None`.

### src/gacalc/ — CORRECTION: NOT fully typed; a small, defined set of bare sigs

The first draft said the core's "public method signatures are already typed
(that's why ty is clean)." **Imprecise** — ty is clean because it *infers*.
Real gaps found (returns are mostly present; several **params** and a few
returns are bare):

- `base.py`
  - `from_blade_dict(cls, blade_coef)` — **core interchange method, param bare**
    (should be `BladeCoef`). Return is already `Self`.
  - arithmetic dunders `__mul__/__rmul__/__add__/__radd__/__truediv__(self, rhs|lhs)`
    — **params bare** (returns already `Self`). ⚠️ These accept a broad union
    (another multivector *or* a scalar `Coef`); annotating them is the **riskiest**
    item — spell the real union and re-run `ty` to confirm it stays clean, since a
    too-narrow annotation could newly fail a caller. Do these last / separately.
  - bare returns: `__iter__` (→ `Iterator[Coef]`), `_repr_latex_` (→ `str`),
    and the nested `add_parens_or_dont(x)` helper.
- `functions.py` — `compose(functions)` (param + return bare), the nested
  closures `composed_fn(x)`/`inv_composed_fn(x)`, `_repr_latex_` return.
- `gn.py` — `from_blade_dict(cls, blade_coef)` param; `as_multivector`/
  `__post_init__` returns.
- `transforms.py` — `to_matrix(...)` return; locals only otherwise.
- `nbplotutils.py` — matplotlib plotting; ~75 bare locals (`ex`, `ey`, `origin`,
  `vertices`, `angle_radians`, …). Big surface, low pedagogical value (it's
  plotting glue, not GA); treat like the notebooks — light touch.

## Approach (annotate however I see fit — Bill's call to my discretion)

Guiding principle: **annotate where the type is non-obvious or pedagogically
useful; leave truly obvious locals alone.** A blanket "every local gets a type"
buries the signal (`n: int = 3` is noise) and inflates the diff. Suggested order,
cheapest/safest first:

- [x] **Audit** every in-scope file (done — findings above).
- [ ] **Mechanical, low-risk first:** add missing test `-> None` in the 4 files
      that lack it; `setup.py` `run` → `-> None`; `bench.py` locals.
- [ ] **Notebooks:** type the helper-function params (`kind`, `show`, `rotate`)
      and the display locals whose GA type is the teaching point. Confirm cells
      still render / round-trip to `.ipynb`.
- [ ] **tests/ locals:** annotate where the type isn't obvious from the RHS,
      using `MultiVectorBase` for values polymorphic across `cls` params.
- [ ] **src/gacalc/ bare sigs:** `from_blade_dict` param (`BladeCoef`),
      `__iter__`/`_repr_latex_`/`to_matrix`/`compose` returns + params. **Leave the
      arithmetic-dunder param union for last** (its caveat is above) and re-run
      `ty` after — that's the one item that can actually change checker results.
- [ ] **src/gacalc/ locals + nbplotutils:** light touch — only genuinely
      non-obvious locals; the core is already carefully typed.
- [ ] **Gate:** `make test` and `make format` (ruff + ty) stay green in the
      container after each slice. No behavior change; no runtime import added only
      for typing (use `from __future__ import annotations` / `TYPE_CHECKING`).

## Open questions

- **How wide?** Three natural scopes — (a) notebooks only (the literal ask), (b)
  notebooks + the mechanical test-`-> None`/`setup`/`bench` cleanup, or (c) all of
  the above **plus** the `src/gacalc/` bare-signature gaps. My inclination: (b) as
  the core deliverable, (c)'s src signatures as a clearly-separable follow-up slice
  (they're signatures, not "local variables," so slightly outside the literal ask).
- **The arithmetic-dunder param union** (`__mul__` etc.) — annotate it (risk: a
  too-narrow union newly trips `ty`), or leave those bare on purpose?
- **Notebook depth** — every display local, or only the ones where the *type* is
  the pedagogical point (my inclination: the latter, to keep cells clean)?
- **nbplotutils.py** — in scope, or leave the plotting glue alone?
