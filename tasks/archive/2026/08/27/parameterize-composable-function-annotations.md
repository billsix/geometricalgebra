# Parameterize bare `ComposableFunction` / `InvertibleFunction` annotations

**Created:** 2026-08-27 · **Completed:** 2026-08-27

## Goal

`ComposableFunction` and `InvertibleFunction` are generic (`ComposableFunction(Generic[V])`,
`InvertibleFunction(ComposableFunction[V])`, `src/gacalc/functions.py`), but ~74 annotations across
`src/`, `tests/` and `notebooks/` spelled them bare, which a type checker reads as implicit `Any`.
Every knowable type parameter was specified, and a `CLAUDE.md` rule was added so new code
parameterizes generics by default. The generated `g*.py` were already parameterized by the overload
work. `MultiVectorFn = Callable[[MultiVectorBase], MultiVectorBase]` is a concrete alias, not a
generic, and was left as is.

## The gotcha — `V` is unbounded and the classes are invariant

`V = typing.TypeVar("V")` is unbounded on purpose (`functions.py` must not import `base`), and a plain
`TypeVar` is invariant, so `ComposableFunction[MultiVectorBase]` and `ComposableFunction[g3.G]` are
different, non-assignable types. A blanket `[MultiVectorBase]` was therefore wrong: each annotation
had to match its value's exact `V` (`translate(some_g3_G)` gives `InvertibleFunction[g3.G]`), and
`ty check` (a wrong parameter is a hard error) was the proof of each choice.

## Decision (William Emerison Six <billsix@gmail.com>, 2026-08-27)

**Keep the transform factories generic `[V]`** — `translate` / `rotor_rotation` / `plane_rotation`
stay `b: V -> InvertibleFunction[V]`, because carrying the concrete type through the transform is
worth keeping. So no factory was widened; call sites got the exact `V` per site. The source-level
functions with no value to bind `V` (`uniform_scale`, `scale_non_uniform`) became `[MultiVectorBase]`.

## What changed

- **Source:** `transforms.py` → `[MultiVectorBase]` for the `uniform_scale`/`scale_non_uniform`
  returns, `to_matrix`'s `fn` param, and the `components_in_plane` / `components_exterior_to_plane`
  locals. `nbplotutils.py`'s nine plotting `fn` params became **`InvertibleFunction[Any]`**: first
  tried `[MultiVectorBase]`, which container pyright showed was wrong — callers pass concrete
  `InvertibleFunction[MultiVector]` etc. while the helpers apply them to `MultiVectorBase`, so under
  invariance a fixed `[MultiVectorBase]` rejects the callers and a bound TypeVar rejects the internal
  application; `[Any]` is the only form compatible both ways.
- **Tests, exact `V` per site:** `test_transforms.py`, `test_multivector.py` → `[MultiVectorBase]`;
  `test_numeric_magnitude.py` → `[g3.Vector]`; `test_plane_rotation.py` → `[g2.Vector]` with
  `[g3.Vector]` and `[Gn]` exceptions at individual sites, plus its `Callable[[Coef], InvertibleFunction]`
  sites.
- **Notebooks:** `displaygraded.py` → `[g3.Vector]`; `displayrotations.py` → `[MultiVectorBase]` (+
  import); `displaymv.py` → `S=[MultiVectorBase]` (+ import), `R=[MultiVector]`.
- **Left bare (correct):** `isinstance(f, InvertibleFunction)` in `functions.py` (a subscripted generic
  can't be an isinstance arg) and `MultiVectorFn`.
- **Skipped:** `notebooks/.ipynb_checkpoints/displaymv-checkpoint.py`, a stale Jupyter autosave
  (tracked but gitignore-matched); noted as worth a separate `git rm`.
- **`CLAUDE.md`:** added "Parameterize generic types — never a bare generic" to Coding standard › Type
  annotations, with the invariance/unbounded-`V` caveat, the `[Any]` case, and the
  isinstance/`MultiVectorFn` exceptions.

## Verification

ruff clean; ty clean on `src`, `tests`, and the full-context generated modules; 411 tests in the
container (`make test`), behaviour unchanged. Container `pyright` showed these edits introduced zero
new notebook errors. An initial "20 pre-existing errors" figure covered only the three notebooks
edited here; a full `pyright notebooks/` run found 47 across five files, none at lines this task
changed. They were filed as `tasks/archive/2026/08/27/fix-notebook-pyright-type-errors.md` and the
gate `tasks/archive/2026/11/04/add-notebook-pyright-gate.md`. Related: the generated types' precision
in `tasks/reference/generated-product-typing.md`.
