# Parameterize bare `ComposableFunction` / `InvertibleFunction` annotations

**Status:** DONE 2026-08-27 (William Emerison Six <billsix@gmail.com>) — see Outcome.
**Priority:** 5
**Difficulty:** 4

## Outcome (2026-08-27)

Done. All bare `ComposableFunction` / `InvertibleFunction` annotations parameterized; **factories kept
generic** per the decision. Gates: **ruff clean; ty clean on `src`, `tests`, AND the full-context
generated modules; 411 tests** (behaviour unchanged — annotations are runtime-irrelevant).

- **Group A (`src`):** `transforms.py` → `[MultiVectorBase]` (`uniform_scale`/`scale_non_uniform`
  returns, `to_matrix`'s `fn` param, the two `components_*` locals); `nbplotutils.py` → the nine
  plotting `fn` params became **`[Any]`** (polymorphic — see the container re-verification below;
  first tried `[MultiVectorBase]`, which was wrong).
- **Group B (call sites), the exact `V` per site, proven by `ty`:**
  - `test_transforms.py`, `test_multivector.py` → **`[MultiVectorBase]`** (the `vec` helper and
    `_plane_e12` are `MultiVectorBase`-typed).
  - `test_numeric_magnitude.py` → **`[g3.Vector]`** (`rotor_rotation` of `g3.Vector`s).
  - `test_plane_rotation.py` → **`[g2.Vector]`** (`E1`/`E2` are `g2.Vector`), with **`[g3.Vector]`**
    (lines 73, 93) and **`[Gn]`** (line 91) exceptions — exactly the per-site variance the task
    predicted; also parameterized the `Callable[[Coef], InvertibleFunction]` sites.
- **Group B notebooks:** `displaygraded.py` → `[g3.Vector]`; `displayrotations.py` →
  `[MultiVectorBase]` (+ a `MultiVectorBase` import); `displaymv.py` → `S=[MultiVectorBase]` (+ import),
  `R=[MultiVector]`. Host `ty` doesn't check notebooks, so these were first done by reasoning —
  then **verified with `pyright` in the container** (see below).

## Container re-verification (2026-08-27) — caught and fixed a real bug

Ran `pyright` inside the nested `gacalc` image (host `ty` doesn't reach notebooks; host has no
pyright). It caught that **`nbplotutils.py`'s `fn: InvertibleFunction[MultiVectorBase]` was WRONG**:
these plotting helpers accept *any* transform (callers pass concrete `InvertibleFunction[MultiVector]`
etc.) but apply it internally to `MultiVectorBase` values — with `InvertibleFunction` invariant, a
fixed `[MultiVectorBase]` rejects the concrete callers, and a bound TypeVar rejects the internal
base-application. **Fixed to `InvertibleFunction[Any]`** (the only thing compatible both ways) — added
to the CLAUDE.md rule. After the fix: pyright shows **my annotation changes introduce ZERO new errors**
(every remaining error is at a line I did not touch — all pre-existing notebook type issues, **out of
scope** for this task). Final gates: ruff clean; host `ty` on `src`+`tests` clean; **411 tests pass in
the container** (`make test`).

**Correction (2026-08-27):** the initial "20 pre-existing errors" figure only covered the three
notebooks *this* task edited (`displaygraded` 2, `displaymv` 12, `displayrotations` 6). A full
`pyright notebooks/` run reports **47 errors across five files** — the two I never touched
(`displayg2.py` 19, `displayg3.py` 8) carry the other 27. None are at lines this task changed. Filed
as two follow-ups: [[fix-notebook-pyright-type-errors]] (clean all 47) and
[[add-notebook-pyright-gate]] (a container `pyright` gate so notebook regressions get caught — depends
on the first landing).
- **Left bare (correct):** `isinstance(f, InvertibleFunction)` in `functions.py` (a subscripted
  generic can't be an isinstance arg); `MultiVectorFn` (a concrete `Callable` alias, not a generic).
- **Skipped:** `notebooks/.ipynb_checkpoints/displaymv-checkpoint.py` — a stale Jupyter autosave
  backup (tracked but also gitignore-matched); not real source. Worth a separate `git rm` cleanup.
- **CLAUDE.md:** added the "Parameterize generic types — never a bare generic" rule (with the
  invariance/unbounded-`V` caveat and the isinstance/`MultiVectorFn` exceptions) to Coding standard ›
  Type annotations.

## Goal

`ComposableFunction` and `InvertibleFunction` are **generic** (`class ComposableFunction(Generic[V])`,
`class InvertibleFunction(ComposableFunction[V])`, `functions.py`). Many annotations spell them
**bare** — `f: InvertibleFunction`, `-> InvertibleFunction`, `p: ComposableFunction` — which a type
checker reads as the unparameterized (implicit-`Any`) form, silently discarding the value type the
function transforms. **Wherever the type parameter is knowable, specify it.** Also add a `CLAUDE.md`
coding-standard rule so new code parameterizes generics by default.

## Investigation (2026-08-27)

- **~74 bare `: `/`-> ` annotations** of `ComposableFunction`/`InvertibleFunction` across `src/`,
  `tests/`, `notebooks/` (excludes generated `g*.py`, which are already parameterized —
  `ComposableFunction[Vector]` etc. — by the overload work). Command to regenerate the list:
  `grep -rnE "(:|->) *(ComposableFunction|InvertibleFunction)([^[a-zA-Z_]|$)" src tests notebooks
  --include="*.py" | grep -v "g[1-5].py"`.
- **The source factories are MOSTLY already parameterized** — `translate(b: V) -> InvertibleFunction[V]`,
  `rotor_rotation(...) -> InvertibleFunction[V]`, `plane_rotation(...) -> Callable[[Coef],
  InvertibleFunction[V]]`, and `base.project`/`reject`/`reflect` (`-> ComposableFunction[MultiVectorBase]`
  etc.). So call sites *can* be tightened without a source change in most cases.
- **`MultiVectorFn = Callable[[MultiVectorBase], MultiVectorBase]` is a concrete alias, NOT generic
  — out of scope** (already fully specified). Don't "parameterize" it. (It coexists with
  `ComposableFunction[MultiVectorBase]`; leave both as they are.)

### THE gotcha — `V` is unbounded and the classes are INVARIANT

`functions.py` defines `V = typing.TypeVar("V")` **unbounded** (on purpose — `functions.py` must not
import `base`, so `V` can't be bound to `MultiVectorBase`). A plain `TypeVar` is **invariant**, so
`ComposableFunction[MultiVectorBase]` and `ComposableFunction[g3.G]` are **different, non-assignable
types**. Consequences that make this task D4, not a mechanical sweep:

- **You cannot blanket-append `[MultiVectorBase]`.** Each annotation must match its value's *exact*
  `V`. `f: InvertibleFunction = translate(some_g3_G_value)` must become
  `f: InvertibleFunction[g3.G]` (because `translate(b: V) -> InvertibleFunction[V]` gives
  `InvertibleFunction[g3.G]`), **not** `[MultiVectorBase]`.
- **Verify every change with `ty check`** — a wrong parameter is a hard error, which is exactly how
  you confirm you picked the right `V`.

## Work, in two groups

### A. Source-level (unambiguous — element type is `MultiVectorBase`)

These functions operate on `MultiVectorBase` (their inner `f(vector: MultiVectorBase) ->
MultiVectorBase`) but declare a bare return/param:

- `src/gacalc/transforms.py:516` `uniform_scale(m: float) -> InvertibleFunction` →
  `-> InvertibleFunction[MultiVectorBase]`.
- `src/gacalc/transforms.py:550` `scale_non_uniform(*factors: float) -> InvertibleFunction` →
  `-> InvertibleFunction[MultiVectorBase]`.
- `src/gacalc/transforms.py:597` `to_matrix(fn: InvertibleFunction, ...)` →
  `fn: InvertibleFunction[MultiVectorBase]`.
- `src/gacalc/transforms.py:213-214` the `components_in_plane` / `components_exterior_to_plane`
  locals (`= cls.project(plane)` / `cls.reject(plane)`, which return
  `ComposableFunction[MultiVectorBase]`) → `ComposableFunction[MultiVectorBase]`.
- `src/gacalc/nbplotutils.py:169,191,226,267,328,339,355,376,440` — the nine `fn: InvertibleFunction
  = _IDENTITY` plotting-helper params (`_IDENTITY = identity()`, applied to multivectors) →
  `InvertibleFunction[MultiVectorBase]`.

**Note the coupling:** once `uniform_scale`/`scale_non_uniform` are `[MultiVectorBase]`, a
`compose([uniform_scale(2.0), translate(some_concrete_value)])` mixes
`InvertibleFunction[MultiVectorBase]` with `InvertibleFunction[<concrete>]` — and invariance means
those don't share one `V`. Check whether such call sites still infer cleanly; if not, either the test
value should be `MultiVectorBase`-typed or the annotation must reflect the actual inferred `V`. This
is the first place to run `ty` and adjust.

### B. Call-site locals (per-site `V`, invariance-sensitive)

The remaining ~60 bare locals in `tests/` (`test_transforms.py`, `test_plane_rotation.py`,
`test_numeric_magnitude.py`, `test_multivector.py`) and `notebooks/` (`displayrotations.py`,
`displaygraded.py`). For each, read the RHS to get the exact `V`:

- from `translate(x)` / `rotor_rotation(from, to)` / `plane_rotation(a, b)(θ)` → `InvertibleFunction[<type of the value>]`;
- from `project(onto)` / `reject`/`reflect` → `ComposableFunction[MultiVectorBase]` /
  `InvertibleFunction[MultiVectorBase]`;
- `ComposableFunction(fn, "...")` constructions → `[MultiVectorBase]` when `fn` is a
  `MultiVectorBase` callable;
- `tests/test_transforms.py:84` `fns: list[InvertibleFunction]` → `list[InvertibleFunction[<V>]]`.

Do these in a second pass, `ty check tests` after each file.

## Decision (Bill, 2026-08-27)

**Keep the transform factories generic `[V]`.** `translate`/`rotor_rotation`/`plane_rotation` stay
`b: V -> InvertibleFunction[V]` — the concrete-type-through-the-transform precision is worth keeping.
So this task does **not** widen any factory to `[MultiVectorBase]`; it just makes the annotations
honest about the `V` the value already has. Consequence for **Group B**: it is **the exact `V` per
site** (`[g3.G]`, `[Gn]`, `[MultiVectorBase]`, … read from each RHS), NOT one uniform parameter —
which is precisely why every change is verified with `ty check` (invariant `V`; a wrong parameter is
a hard error). The Group-A source fixes stay `[MultiVectorBase]` (`uniform_scale`/`scale_non_uniform`
etc. have no value to bind `V` and operate on `MultiVectorBase`).

## CLAUDE.md update (part of this task)

Add to the **Coding standard › Type annotations** section a rule:

> **Parameterize generic types in annotations — never a bare generic.** Write
> `ComposableFunction[MultiVectorBase]` / `InvertibleFunction[g3.G]`, not a bare `ComposableFunction`
> / `InvertibleFunction` (a bare generic silently degrades to implicit `Any` in its parameter).
> These two are **invariant** with an **unbounded** `V` (`functions.py` can't import `base`), so the
> parameter must match the value's *exact* `V` — `InvertibleFunction[g3.G]` for a `translate` of a
> `g3.G` value, `[MultiVectorBase]` for the representation-agnostic transforms — never blanket
> `[MultiVectorBase]`. `MultiVectorFn` (a concrete `Callable` alias) is already fully specified and is
> not a generic to parameterize.

## Verification

- `ty check src` and `ty check tests` clean (this is the whole point — every parameter must be the
  correct `V`, and ty proves it).
- `make format` clean (ruff), `make test` green (annotations are runtime-irrelevant, so behaviour is
  unchanged; the win is purely static).
- No `# type: ignore` / cast added to make a wrong `V` pass — if a site can't be cleanly
  parameterized, that's a finding (likely the compose-of-mixed-`V` case above), record it rather than
  paper over it.

## Cross-links

- `src/gacalc/functions.py` — `ComposableFunction(Generic[V])` / `InvertibleFunction(ComposableFunction[V])`,
  `V = TypeVar("V")` (unbounded; the invariance root).
- `src/gacalc/transforms.py`, `src/gacalc/nbplotutils.py` — the Group-A source fixes.
- `tasks/reference/generated-product-typing.md` — where the generated types' `ComposableFunction[Vector]`
  precision (project/reject/reflect overloads) already lives; this task extends the same "spell the
  parameter" discipline to the hand-written and call-site annotations.
- `CLAUDE.md` › Coding standard › Type annotations — the convention to add.
