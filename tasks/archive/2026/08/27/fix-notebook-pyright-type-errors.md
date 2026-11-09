# Fix the pre-existing pyright type errors in the notebooks

**Created:** 2026-08-27 · **Completed:** 2026-08-27

## Goal

`pyright notebooks/` reported **47 errors across five notebooks** (`displayg2` 19, `displaymv` 12,
`displayg3` 8, `displayrotations` 6, `displaygraded` 2). All predated
`tasks/archive/2026/08/27/parameterize-composable-function-annotations.md` and none broke execution,
but the annotations were wrong. The task brought the notebooks to zero pyright errors; the 41
`reportUnusedExpression` warnings on Jupyter display cells are intentional and were left. Pyright
runs only in the container (host `ty` does not check `notebooks/`), so all verification was in the
nested `gacalc` image.

## Root causes found

1. **`compose` / `compose_intermediate_fns` on a mixed-`V` list** (~18, the biggest group): a
   `list[InvertibleFunction[Vector] | InvertibleFunction[G]]` cannot unify to one
   `ComposableFunction[V]` because `V` is invariant (`src/gacalc/functions.py`) — the same root cause
   as the parameterize task's `nbplotutils` `[Any]` fix.
2. **A local annotated narrower than its RHS** (~11), e.g. `projection_2d: Gn = projection_rotation(...)(v)`
   where the call returns `MultiVectorBase`.
3. **sympy-stub friction** (~10): `simplify` has no overload for `Coef` (a union including `float`).
4. **`G` passed where `Vector` is expected in `__call__`** (3).
5. **`inverse` / `dot` / factory-alias mismatches** (~4), e.g. `T = translate` declared to return
   `MultiVectorFn` though `translate` returns `InvertibleFunction[V]`.
6. **`reportRedeclaration`** (2): the same name re-annotated in two cells.

Approach: one notebook at a time, easiest first, re-running pyright after each; widen a local to its
true type in preference to `# type: ignore`; reserve casts for third-party-stub friction and the
sanctioned use-site casts; record rather than make any `src` change.

## What changed

- **displaymv.py** — `T` retyped as `Callable[[MultiVector], InvertibleFunction[MultiVector]]`, which
  alone cleared 9 downstream errors (`inverse` / `compose` / `compose_intermediate_fns`); the
  deliberately-`MultiVectorBase` `dual()` result cast for `dot()`; the `rotate` binding typed.
- **displayg2.py** — `rotate` built from the **G basis** (`plane_rotation(e_1, e_2)`) instead of
  `Vector.e_1`, so it is `InvertibleFunction[G]`; this fixed 10 errors (3 `G`-in-`__call__`, 7 mixed
  `compose`) and matches the notebook's "every value is a `g2.G`" theme (rationale comment updated).
  The redeclared `a` became `a_full`; `rotate` and three `fn` bindings typed `[G]`; two
  `sympy.simplify` args cast.
  - Judgment call: the switch dropped the incidental demo of a `Vector`-built rotor applied to a `G`.
    The rejected alternative was casting at ~10 call sites.
- **displayg3.py** — redeclared `a` → `a_full`; three `sympy.simplify` args cast.
- **displaygraded.py** — a `bivector * scalar` reordered (operand order only); the g3 `w` renamed
  `w3`; the g2 `w` typed.
- **displayrotations.py** — a `Gn * scalar` reordered; the deliberately-`MultiVectorBase`
  `rotor_from_vectors` / `projection_rotation` / pipeline results cast back to `Gn`; `f` typed.

**`src/` was deliberately untouched.** Several errors trace to `Gn`/graded methods that return bare
`MultiVectorBase` by design (`dual`, `rotor_from_vectors`, `projection_rotation`, `project`/`reject`,
whose docstrings say "cast at the use site"). Narrowing those in `gn.py` would remove these casts and
unblock `tasks/archive/2026/10/09/use-bivector-from-vectors-and-i-in-notebooks-and-tests.md`; it was
left as that task's prerequisite.

## Verification

- `pyright notebooks/` in the container: 47 → **0 errors** (41 expected warnings). Ruff clean and
  idempotent (`ruff check` / `ruff format --check`).
- Behaviour unchanged: the notebooks with semantic edits (displayg2's basis change, displaygraded's
  reorder, displayg3) were executed headlessly in the container (`jupytext --to ipynb` +
  `jupyter nbconvert --execute`, `MPLBACKEND=Agg`) and passed; displaymv and displayrotations carry
  only annotation/cast/commutative-reorder edits.
- This unblocked the gate in `tasks/archive/2026/11/04/add-notebook-pyright-gate.md`.
