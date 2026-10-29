# Parameterize bare generic type annotations

**Status:** in progress. **Priority:** 5  **Difficulty:** 1

## BLUF

Five annotations (four in `src/gacalc/nbplotutils.py`, one in
`tools/gen_specialized.py`) use a bare `dict`/`list`/`type` where the parameters
are knowable from the surrounding code; a bare generic silently degrades its
parameters to implicit `Any` (shared Python standard, "Parameterize generic
types"). Give each its real domain parameters (`BladeReal`, `MultiVectorBase`,
…). "Done" = the five sites parameterized and `make format` (ruff + `ty`) green.

## Context (cold-start)

Found by an AST scan for annotations whose value is a generic container left
unsubscripted. gacalc's own domain aliases make the exact parameters clear:
`BladeReal = dict[Blade, Real]`, `Blade = tuple[int, ...]`,
`Real = int | float | sympy.Expr` (`src/gacalc/base.py`), all already imported in
`nbplotutils.py`.

## The sites and their fixes

- `src/gacalc/nbplotutils.py` `_blade_terms(mv) -> list` → `-> list[MultiVectorBase]`
  (returns the single-blade multivectors that sum to `mv`).
- `src/gacalc/nbplotutils.py` `_expand_numerators_dict(mv) -> dict` → `-> BladeReal`
  (returns `mv`'s blade dict with numerators expanded — same shape as
  `to_blade_dict`).
- `src/gacalc/nbplotutils.py` `out: dict = {}` → `out: BladeReal = {}` (the
  accumulator `_expand_numerators_dict` builds and returns).
- `src/gacalc/nbplotutils.py` `data: list = list(itertools.product(...))` →
  `list[tuple[MultiVectorBase, MultiVectorBase]]` (pairs from
  `product(_blade_terms(a), _blade_terms(b))`, unpacked `left, right` below).
- `tools/gen_specialized.py` `src: type` → `src: type[MultiVectorBase | Gn]` (the
  loop is `for src in (MultiVectorBase, Gn):`; both are module-level imports).

## Scanner false positives — deliberately NOT changed (with reason)

- `src/gacalc/nbplotutils.py` `rng: np.random.Generator = np.random.default_rng(...)`
  — `np.random.Generator` is a concrete numpy class, **not** `collections.abc.Generator`;
  it is not a bare generic. Leave as-is.
- `tools/gen_specialized.py` `pairs_iter: ast.Tuple = ast.Tuple(...)` — `ast.Tuple`
  is an AST node class, **not** `typing.Tuple`; not subscriptable as a generic.
  Leave as-is.

## Verification

`make format` (containerized: regenerate specialized modules, then ruff + `ty`);
annotation-only, no runtime behaviour change. `gen_specialized.py` is the
*generator* (hand-written source), so editing its own annotation is correct — this
does not touch any generated output.
