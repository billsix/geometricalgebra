# Fix the pre-existing pyright type errors in the notebooks

**Status:** DONE 2026-08-27 (William Emerison Six <billsix@gmail.com>) — see Outcome.
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)

## Outcome (2026-08-27)

All **47 errors across the five notebooks → 0** (`pyright notebooks/` in the container; the 41
`reportUnusedExpression` warnings on display cells are intentional and left). Ruff clean and idempotent
(`ruff check`/`ruff format --check`). Fixes by notebook:

- **displaymv.py** — retyped `T` as `Callable[[MultiVector], InvertibleFunction[MultiVector]]`
  (`translate` returns `InvertibleFunction[V]`, not `MultiVectorFn`); that one fix cleared 9 downstream
  errors (`inverse` / `compose` / `compose_intermediate_fns`). Cast the deliberately-`MultiVectorBase`
  `dual()` result for `dot()`. Typed the `rotate` factory binding.
- **displayg2.py** — built `rotate` from the **G basis** (`plane_rotation(e_1, e_2)`) instead of
  `Vector.e_1`, so it is `InvertibleFunction[G]`: fixed 10 errors (3 `G`-in-`__call__`, 7 mixed
  `[Vector]|[G]` `compose`). Matches the notebook's "every value is a `g2.G`" theme; rationale comment
  updated. Renamed the redeclared `a`→`a_full`; typed `rotate` and the three `fn` bindings `[G]`; cast
  two `sympy.simplify` args (`Coef` stub friction).
- **displayg3.py** — renamed redeclared `a`→`a_full`; cast three `sympy.simplify` args.
- **displaygraded.py** — reordered a `bivector * scalar` (operand order, not math); renamed the g3
  `w`→`w3` (redeclared vs the g2 `w`); typed the g2 `w`.
- **displayrotations.py** — reordered a `Gn * scalar`; cast the deliberately-`MultiVectorBase`
  `rotor_from_vectors` / `projection_rotation` / pipeline results back to `Gn`; typed the `f` binding.

**Behaviour verified unchanged** by executing the notebooks headlessly in the container
(`jupytext --to ipynb` + `jupyter nbconvert --execute`, `MPLBACKEND=Agg`): every notebook carrying a
*semantic* edit passed — displayg2 (the `rotate`-basis change), displaygraded (the operand reorder),
and displayg3. displaymv (annotation/cast-only, no runtime change) and displayrotations (a commutative
reorder + no-op casts) carry only behaviour-preserving edits.

**`src/` deliberately untouched.** Several errors trace to `Gn`/graded methods that return bare
`MultiVectorBase` by design (`dual`, `rotor_from_vectors`, `projection_rotation`, `project`/`reject` —
their docstrings say "cast at the use site"). Used the sanctioned use-site casts. Narrowing those
returns in `gn.py` would erase these casts *and* unblock [[use-bivector-from-vectors-and-i-in-notebooks-and-tests]]
— left as that task's prerequisite, not done here.

**Judgment call for review:** the displayg2 `rotate` basis switch (`Vector.e_1` → G `e_1`) drops the
incidental demo of a `Vector`-built rotor applied to a `G`. The alternative was casting at the ~10 call
sites; chose the basis switch as cleaner and truer to the notebook's theme.

## Goal

`pyright notebooks/` reports **47 errors across five notebooks**. All predate the
[[parameterize-composable-function-annotations]] work (none are at lines that task touched) and none
break execution — the notebooks run and `make test` is green — but the annotations lie, which is
exactly the "a bare/near-miss annotation silently degrades to the wrong type" problem the parameterize
task fixed for `src`/`tests`. This task cleans the notebooks to **zero pyright errors** (warnings —
the `reportUnusedExpression` display cells — stay; they're intentional Jupyter display lines).

**Why pyright, not `ty`:** host `ty` doesn't check `notebooks/` (they're not on its paths, and pyright
is only in the container image, not on the host). So this whole task is verified **in the nested
`gacalc` container** — see Verification.

## The 47 errors, by file (full `pyright notebooks/` run, 2026-08-27)

| File | errors |
| --- | --- |
| `displayg2.py` | 19 |
| `displayg3.py` | 8 |
| `displaymv.py` | 12 |
| `displayrotations.py` | 6 |
| `displaygraded.py` | 2 |

Regenerate the list any time (in the container, from repo root):
`pyright notebooks/ | grep 'error:'`.

## The error families (root causes — this is where the D5 is)

1. **`compose` / `compose_intermediate_fns` overload failure on a mixed-`V` list** (~18 errors, the
   biggest group — `displaymv`, `displayg2`, `displayg3`). A
   `list[InvertibleFunction[Vector] | InvertibleFunction[G]]` (or `... | MultiVectorFn`) can't unify to
   one `ComposableFunction[V]` because **`V` is invariant** (the same root cause as the parameterize
   task's `nbplotutils` `[Any]` fix). Options per site: annotate the list at the common type the cells
   actually compose at (often `[MultiVectorBase]` or `[Any]`), or — if a genuine `Vector`-vs-`G` mix is
   being composed — decide whether that's a real modeling smell to widen at the source. **Don't** paper
   over with `# type: ignore` before understanding which it is.
2. **Local annotated narrower than its RHS** (~11 errors — `MultiVectorBase`/`Expr`/`G` not assignable
   to a declared `Gn` / `g3.Vector` / `Bivector`). E.g. `projection_2d: Gn = projection_rotation(...)(v)`
   where the call returns `MultiVectorBase`; `b: Gn = sympy.cos(theta)*e_1 + ...` where the RHS is
   `Expr`-typed. Fix by widening the local annotation to the true type, **or** by fixing a real API
   return-type narrowing gap if one is found (e.g. a factory that should return `Gn` but returns
   `MultiVectorBase`). The latter would be a `src` change — flag it, don't force it in the notebook.
3. **sympy-stub friction** (~10 errors — `simplify` has no overload for `Coef`; `Coef` not assignable to
   `Basic`). Calling `.simplify()` / `sympy.simplify(...)` on a `Coef` (a Union that includes `float`).
   Likely the honest fix is a narrow `cast`/annotation at the call, since it's the sympy stubs being
   strict, not our bug — decide per site.
4. **`G` where `Vector` expected in `__call__`** (3 — `displayg2`/`displayg3`): passing a general `G`
   into a function typed for `Vector`.
5. **`inverse`/`dot`/factory-alias mismatches** (~4 — `displaymv`): `MultiVectorFn` passed where
   `InvertibleFunction[V]` is wanted; `MultiVectorBase` passed to `dot`'s `MultiVector` param; the
   `T = translate` alias declared `(MultiVector) -> MultiVectorFn` but `translate` returns
   `InvertibleFunction[V]`.
6. **`reportRedeclaration`** (2 — `displayrotations`: `a: Gn = e_1` then later `a: Gn =
   Gn.symbolic_multivector(...)`): the same name re-annotated in two cells. Rename one (`a2d`/`a3d`, or
   the cross-product `a`/`b` cell's vectors) so the declaration isn't obscured.

## Approach

- **One notebook at a time**, easiest first (`displaygraded` 2 → `displayrotations` 6 → `displayg3` 8 →
  `displaymv` 12 → `displayg2` 19), re-running container pyright after each so a regression localizes.
- **Prefer widening the local annotation to the true inferred type** (read the RHS, as in the
  parameterize task) over `# type: ignore`. Reserve `cast`/`ignore` for genuine third-party-stub
  friction (family 3) and comment *why* at the site.
- **If a fix wants an `src` change** (a real API return-type narrowing gap, family 2/5), **stop and
  record it as a finding** — don't reshape `src` inside a notebook-cleanup task without a decision. It
  may belong to [[use-bivector-from-vectors-and-i-in-notebooks-and-tests]] (blocked on `gn.py`
  narrowing — a `Gn`-returning-`Gn` gap is the same shape).
- **Behaviour must not change** — these are display notebooks; every cell must still produce the same
  output. Annotations are runtime-irrelevant, so `make test` staying green is the guard.

## Verification (container — pyright is not on the host)

```sh
# nested podman; --cgroups=disabled on the inner run
podman run --rm --cgroups=disabled -v "$(pwd)":/gacalc:Z --entrypoint /bin/bash \
    localhost/gacalc:latest -c \
    'cd /gacalc && source /venv/bin/activate && pip install -e . --no-index --no-deps -q && pyright notebooks/'
```

- **`pyright notebooks/` → 0 errors** (the 41 `reportUnusedExpression` warnings on display cells are
  expected — leave them).
- Host `ruff check notebooks` clean; `make test` green (behaviour unchanged).
- No new `# type: ignore` beyond the sympy-stub sites, each commented with its reason.

## Cross-links

- [[parameterize-composable-function-annotations]] (archived) — where these were first spotted and the
  invariance/`[Any]` pattern was established; family 1 here is the same root cause.
- [[add-notebook-pyright-gate]] — the gate that *depends on this landing* (can't gate at 0 errors until
  they're gone).
- `CLAUDE.md` › Coding standard › Type annotations — the "parameterize generics; verify notebooks with
  pyright in the container" rule this task enforces in the notebooks.
- `src/gacalc/functions.py` — invariant unbounded `V` (family 1's root).
