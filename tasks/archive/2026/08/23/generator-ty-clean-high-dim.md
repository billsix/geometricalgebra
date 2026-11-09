# Make the generated g4/g5 modules ty-clean (fix pre-existing type imprecisions surfaced at n≥4)

**Created:** 2026-08-22 · **Completed:** 2026-08-22

Generating 𝒢₄ for the first time (Part 2 of
`tasks/archive/2026/08/23/precise-blade-typing-and-g4-g5-default.md`) made `ty check src` report
**179 diagnostics, all in `g4.py`**; g1/g2/g3 were clean. Runtime was correct (dim-4 conformance, 162
tests) and no gate failed (nothing ran ty on g4/g5), so this was a code-quality issue for the shipped
high-dim modules. All 179 were resolved by real fixes, none by suppression. The durable rules were
harvested to `tasks/reference/generated-product-typing.md`.

## Diagnosis

The flagged lines were byte-identical to g3's (e.g. `left: G = _coerce(self, G)`, clean in g3,
flagged in g4); the earlier precise-typing edits never touched `_coerce`/`__radd__`/`from_blade_dict`/
`_geometric_product`. They were **genuine latent imprecisions** that ty only surfaced on the 3×-larger
g4 module (529 KB vs 166 KB): g3 passing reflected ty being incomplete at smaller scale, not the code
being sound. This was established after reading the design and the archived typing work
(`investigate-final-full-classes`, `retype-even-odd-part-off-self`, `restore-ty-on-generated-sandwich`).

## Fixes

| category | count | fix | why it was real |
|---|---:|---|---|
| `invalid-assignment` | 86 | `_coerce` made generic, `def _coerce[T: MultiVectorBase](x, cls: type[T]) -> T` (PEP 695, `base.py`) | `_coerce` was typed `-> MultiVectorBase`, so assigning to a `: G` local was unsound |
| `invalid-return-type` | 40 | the `@final` types annotate the concrete class (`-> G`, `-> Scalar`, `-> Vector`) instead of `typing.Self`, via `self_ann` in `generate_scalar`/`generate_class`/`generate_graded_type` | the 2026-07-23 work made methods construct `G(...)` concretely but kept `-> Self`; ty does not fully collapse `Self` to `G` under `@final`. `-> G` is a valid narrowing override of base's `-> Self`, and the coerce branch's `cast(Self, …)` still matches |
| `redundant-cast` | 40 | dropped `cast(Coef, d.get(b, 0))` in `from_blade_dict` (`d: BladeCoef`, so the value is already `Coef`) | the cast was always unnecessary |
| `invalid-overload` | 8 | the `project`/`reject`/`reflect` implementation returns `wrapper[Any]` (`transform_factory_overrides`) | `ComposableFunction`'s `V` is necessarily invariant (`func: Callable[[V], V]`), so a `ComposableFunction[Vector]` overload return is not assignable to an impl returning `ComposableFunction[MultiVectorBase]`; you cannot covariantly narrow an invariant generic. The gradual impl type is harmless because only the overloads are called, and they keep the precise `[Vector]` (optimistic but runtime-correct, since the function is grade-preserving). Latent since the `onto: Vector` overload of 2026-08-03 |
| `invalid-method-override` | 5 | base `__radd__` parameter narrowed from `MultiVectorBase \| Coef` to `Coef` | it is only ever called with a bare number (a multivector left operand uses its own `__add__`), matching the generated `__radd__` |

Progress: 179 → 93 after `_coerce`, → 48 errors + 40 warnings after `__radd__`, → 0. The
`redundant-cast` warnings turned out to make `ty check` exit nonzero in this project, contrary to an
early assumption that warnings don't fail it.

**Suppression was rejected** because these were real imprecisions, not false positives: suppressing
would hide a benign type-lie that could mask a future real one, and would rot once ty's small-module
checking caught up with g1–g3. The fixes were small, made the intent explicit, and tightened g1–g3 too
(or were no-ops there). All were generator/`base.py` changes; the gitignored `g*.py` changed on disk
only.

## Also found and fixed

- **`.gitignore` didn't cover g4/g5**: it listed `g1.py`/`g2.py`/`g3.py` explicitly, so generated
  g4/g5 were untracked (an accidental-commit hazard), and ruff/ty checked them directly (which is why
  `ty check src` saw g4 at all). Replaced with the glob `/src/gacalc/g[0-9]*.py`, which covers g1..g10+
  but not the tracked hand-written `gn.py`.
- **One stray `redundant-cast` per module** (the single-blade pseudoscalar's `magnitude_squared`,
  `cast(Coef, coeff**2)`): `cast_coef` (`tools/astbuild.py`) now skips a single `field ** constant`;
  multi-term sums still cast, since ty can't narrow the sympy sum.

## How it is verified

ty (like ruff) respects `.gitignore`, so the dev gate `ty check src` skips every generated `g*.py`.
The generated modules must be checked **explicitly and together**:
`ty check src/gacalc/g1.py … g5.py gn.py base.py functions.py transforms.py nbplotutils.py`. A
single-file `ty check src/gacalc/g3.py` gives ~119 isolation false positives and is not a valid check.
Wiring this full-context check into `make test-all-dims`, so g4/g5 cleanliness can't silently regress,
was recommended here.

## Verification

- g1/g2/g3: 0 diagnostics in full context and 370 tests after every fix (`make generate` ~23 s).
- Iteration ran against g4 (~5 min per regen); g5 (~87 min) was confirmed once at the end.
- **Definitive `GACALC_DIMS=1,2,3,4,5` full-context ty run: "All checks passed!" (0 errors, 0
  warnings)** across g1–g5 and all hand-written modules; full-dim conformance 198 passed.

## Related

- `tasks/archive/2026/08/23/precise-blade-typing-and-g4-g5-default.md`: the work that surfaced this.
- `tasks/reference/generated-product-typing.md`: the generated-typing design.
- `tasks/reference/generated-algebra-generation-cost.md`: the g4/g5 regen costs.
