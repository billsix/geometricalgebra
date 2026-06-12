# Retire `component`, read coefficients via `to_blade_dict` instead

Status: **DONE 2026-06-12** · proposed 2026-06-12 (Bill)

> **Done.** Deleted `AbstractMultiVector.component`. Migrated the 24 `nbplotutils`
> uses to a `_coord(mv, blade)` helper over `to_blade_dict()` (and floated the
> `Polygon` vertices — the typed helper surfaced a latent matplotlib ArrayLike
> issue the old `Unknown`-typed `component` calls had masked; removed the now-unused
> `ex`/`ey` in one helper). Migrated `test_component` → `test_coefficient_readback`
> (conformance + graded), now asserting the `to_blade_dict()` round-trip +
> reconstruction. Updated `displaygraded.py`, CLAUDE.md, README to the
> `to_blade_dict().get(tuple, 0)` idiom. `scalar_product` kept (it's the genuine
> scalar product, not a coefficient reader).
>
> **Then (Bill's call) added a thin `coefficient(blade)` convenience** on
> `AbstractMultiVector` — restores the ergonomic `v.coefficient(Vector2.e_1)` reader
> (a unit basis blade in), but implemented as a *direct* `to_blade_dict()` lookup
> (`(key,) = blade.to_blade_dict(); return self.to_blade_dict().get(key, 0)`) — no
> geometric product, correct for any grade, with a doctest. Tests (`test_coefficient_readback`
> in conformance + graded) and the README/CLAUDE/`displaygraded` docs now use it;
> `nbplotutils` keeps its tuple-based private `_coord` helper. So `coefficient` is
> the public reader convenience without `component`'s product/sign machinery.
> Full suite **220**, ty + ruff clean.

## Goal

Remove `AbstractMultiVector.component(x)` and replace its callers with a **direct
read of the stored coefficient** via `to_blade_dict()`.

## Why

`component(x) = ⟨A x̃⟩₀ = (A * x.reverse()).scalar_part()` *computes* a geometric
product + grade projection to recover a number the representation **already
stores** (the `Gn` blade dict, or a specialized class's `coeff_*` field). Reading
it straight from `to_blade_dict()` is:

- **direct** — no product computed,
- **representation-agnostic** — the `Gn` dict and the `coeff_*` fields both surface
  through the same interchange protocol,
- **correct for any grade** — it's the actual stored coefficient (right sign), so
  unlike `scalar_product(e_12)` (which is the *negative* of the e₁₂ coefficient),
  `to_blade_dict()[(1,2)]` is the coefficient itself.

(Bill, 2026-06-12: "all I'm trying to do is get the coefficient it already has —
access it directly." Already applied in `to_matrix`, `transforms.py`.)

## The API translation

`component` takes the blade as a **multivector** (a unit basis blade like `e_1`);
`to_blade_dict` is keyed by **blade tuples**:

```python
v.component(e_1)        ->  v.to_blade_dict().get((1,), 0)
v.component(e_12)       ->  v.to_blade_dict().get((1, 2), 0)
B.component(e_1 ^ e_2)  ->  B.to_blade_dict().get((1, 2), 0)
```

For the callers below, the blade is always a basis vector, so the tuple is trivial
(`(1,)`, `(2,)`).

## Scope (measured 2026-06-12)

- **`src/gacalc/nbplotutils.py` — ~24 uses**: `.component(ex)` / `.component(ey)`
  in the plotting helpers (`plot_multivector`, the graph-paper / `draw_*` helpers),
  all reading a basis-vector coordinate. `ex`/`ey` are `e_1`/`e_2`, so each becomes
  `mv.to_blade_dict().get((1,), 0)` / `... (2,) ...`. (Cache `to_blade_dict()` once
  per `mv` where it's read repeatedly, e.g. the `[mv.component(ex), mv.component(ey)]`
  list-comprehensions.)
- **`tests/test_conformance.py::test_component`** — tests reading every blade's
  coefficient (incl. grade ≥2 sign) + the `Σ component(b)·b == x` reconstruction.
  Migrate its assertions to `to_blade_dict().get(...)`, or retire it (the
  interchange protocol is already exercised throughout the suite). **Decision below.**
- **Docs**: `README.md` quick-start shows `a.component(e_1)` (and `B.component(e_1 ^
  e_2)`); `CLAUDE.md` references `value.component(blade)` as the coefficient reader,
  and known-issue #2 notes `component` was "resolved". Update all to the
  `to_blade_dict` idiom.
- **`base.py`**: delete the `component` method (and drop the doc/known-issue text
  that points at it).

## Decisions for Bill

1. **Direct `to_blade_dict().get(tuple, 0)` at call sites (recommended), or a thin
   reader?** The few callers all read basis-vector coords, so direct access is
   clean and needs no new API. (If a named reader is wanted, it'd just wrap
   `to_blade_dict().get` — but that's most of what `component` already is.)
2. **`test_component`: migrate or delete?** It's the only thing exercising the
   grade-general read. The replacement (`to_blade_dict`) is the interchange
   primitive, already heavily tested. Lean: keep a small `test_coefficient_readback`
   that asserts `to_blade_dict()` matches the constructed coefficients + the
   reconstruction identity, so the *property* stays covered without `component`.
3. **Grade ≥2 readers elsewhere?** None found outside `test_component` (all real
   callers read vector coords). Confirm with a final grep before deleting.

## Process

1. Migrate `nbplotutils.py` `.component(...)` → `to_blade_dict().get(tuple, 0)`
   (cache the dict where read repeatedly).
2. Migrate/retire `test_component` (decision 2).
3. Update `README.md` + `CLAUDE.md` to the `to_blade_dict` idiom; drop the
   `component` known-issue text.
4. Delete `AbstractMultiVector.component`; grep to confirm no remaining callers
   (incl. notebooks).
5. `python -m pytest -q`, `ty check src tests`, `ruff` — all green; notebooks run
   headless.

## Relationship

- `scalar_product` stays (it's the genuine scalar product `⟨A B⟩`, used by
  `magnitude_squared`/`cosine`/etc.), and is *not* the right coefficient reader for
  grade ≥2 — `to_blade_dict` is. This task is specifically about the
  *coefficient-readback* role that `component` filled.
- Builds on `tasks/archive/2026/06/07/graded-class-e_n-zero-vs-basis-vector.md`
  (which made `component` the "blessed getter"); this supersedes that role with the
  interchange read.
