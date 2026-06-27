# Add Python type annotations as broadly as reasonable (signatures + tools + emitted)

**Status:** complete (2026-06-27) — option 1 done; signatures added across `tools/` + `nbplotutils.py`;
`tools/` now under `ty` and clean. Ready to archive.
**Proposed:** 2026-06-27
**Completed:** 2026-06-27

## Done (2026-06-27)

Option 1 chosen (bring `tools/` under `ty`). Full **parameter + return** signature coverage added:

| module | untyped params before → after | no-return before → after |
| --- | --- | --- |
| `tools/gen_specialized.py` | 72 → **0** | 8 → **0** |
| `tools/astbuild.py` | 39 → **0** | 2 → 1 (`__init__`, conventional) |
| `tools/bench.py` | 2 → **0** | 1 → **0** |
| `tools/gen_proofs.py` | 0 → 0 | 0 → 0 (fixed 3 `sympy.simplify` errors) |
| `src/gacalc/nbplotutils.py` | 27 → **0** | 13 → **0** |

Details:
- **astbuild.py:** added AST-DSL signatures (`ast.expr`/`ast.stmt`/`Sequence`/`Iterable`/`Callable`).
  Real fixes the annotations surfaced: list **invariance** — `fn`/`cls` `body` typed `Sequence[ast.stmt]`
  (covariant) + `list(body)` internally; `lit` casts at the ast.Constant boundary (typeshed's value type
  omits the blade tuples it accepts at runtime); `isinstance_` narrowed to `list[ast.expr] | ast.expr`;
  `bool_or`/`bool_and` `values=list(tests)`.
- **gen_specialized.py:** typed every helper signature (`TypeSpec`/`sympy.Expr`/`Callable[[Gn,Gn],Gn]`/
  blade `Sequence[tuple[int, ...]]`/cast callables, product/unary `-> tuple[TypeSpec, list[sympy.Expr]]`,
  the full `dispatch_method` param list, and the nested `bilinear`/`linear`/`grade_copy`/`scalar_*`).
  One real narrowing: `term_grade_key` guards `isinstance(sym, sympy.Symbol)` before `sym.name`
  (`free_symbols` types as `set[Basic]`).
- **gen_proofs.py:** the 3 pre-existing `no-matching-overload` errors fixed by `sympy.simplify(sympy.sympify(...))`.
- **bench.py:** `to`/`time_ms`/`widen_sym` typed (added `MultiVectorBase` + `Callable` imports, `from __future__`).
- **nbplotutils.py:** signatures for the plotting helpers — `fn: InvertibleFunction`, RGB color triples,
  `graph_bounds: tuple[int, int]`, `width`/`height: int`, `_coef_as_float(coef: Coef)`, Figure/Generator
  returns. Caught that `generategridlines`/`generate_circle` are generators and `create_graphs` is a
  `@contextmanager` (typed `Generator[Axes, None, Figure]`, no logic change).
- **format.sh:** added `ty check /gacalc/tools` so `tools/` stays type-checked.

**Emitted generated-method annotations: deliberately NOT done.** The generated `g*.py`/`scalar.py`
methods' remaining untyped params are the polymorphic operands (`rhs`/`other`/`lhs`) that `match` on any
operand type; `ty check src` is already clean (a missing annotation is `Unknown`, not an error), so
annotating them broadly (`object`/wide union) would add noise without catching anything. The generated
**return** types are already precise (the whole point of the graded subtypes).

**Verified:** `ruff` + `ty check src tests tools` clean on every file touched; generated
`scalar/g1/g2/g3.py` **byte-identical** to baseline (generator-internal edits only); **226 tests pass**.

**Pre-existing issue flagged (NOT mine, NOT fixed):** `tools/gen_proofs.py:247` trips `ruff` `T201`
(`print` found) — present at HEAD (the in-progress latex-book work), unrelated to typing. Left for the
latex-book task to resolve.

## (original plan below)

## Goal

Extend type-annotation coverage across the codebase "as much as reasonably possible," focusing on
**function signatures (parameters + return types)** and the under-typed modules. This builds on the
completed **local-variable** pass (`tasks/archive/2026/06/06/add-python-types.md`, 2026-06-06), which
was a deliberately light-touch pass over *locals* in `src/` and a few generator locals; this task
picks up the **signature** coverage and the areas that pass left out.

## Current coverage (measured 2026-06-27)

Untyped non-self/cls params per module (params_untyped / total, and functions with no return type):

| module | untyped params | no return type | notes |
| --- | --- | --- | --- |
| `tools/gen_specialized.py` | 72 / 112 | 8 | biggest gap — the generator |
| `tools/astbuild.py` | 39 / 44 | 2 | the node-builder DSL (returns mostly typed `-> ast.X`) |
| `tools/bench.py` | 2 / 10 | 1 | minor |
| `src/gacalc/base.py` | 5 / 52 | 3 | already strong |
| `src/gacalc/gn.py` | 1 / 4 | 2 | already strong |
| `src/gacalc/transforms.py` | 2 / 34 | 4 | already strong |
| `src/gacalc/nbplotutils.py` | 27 / 44 | 13 | notebook helpers — moderate gap |
| `src/gacalc/g1/g2/g3/scalar.py` | many | several | **generated** — fix via the emitter, not by hand |
| `notebooks/display*.py` | a few | a few | demo scripts — low priority |

So the high-value targets are **`tools/gen_specialized.py`**, **`tools/astbuild.py`**, the
**generator's emitted annotations** (which is how the generated `g*.py`/`scalar.py` get typed), and
**`nbplotutils.py`**. The hand-written algebra core (`base`/`gn`/`transforms`) is already well typed.

## Scope / policy

- **Light-touch, same spirit as the prior pass:** annotate where it adds clarity or lets `ty` catch
  real errors; don't stamp noise on obvious throwaways. The AST-DSL builders in `astbuild.py` have
  clear, mechanical types worth adding (`ast.expr`, `ast.stmt`, `list[ast.stmt]`, `str`, `bool`,
  `Iterable[...]`), so that module is a good high-yield target.
- **Generated code is typed via the generator, never by hand** (CLAUDE.md "Code generation"). To type
  a method on `G2`/`Vector2`/`Scalar`, change what `tools/gen_specialized.py` *emits* (e.g. the
  `__add__`/`is_close`/product-dispatch parameter annotations). Caveat: the product/dispatch methods
  accept any operand (`Scalar`/`Vector2`/number/…), so their `rhs`/`other` params can't be narrowed to
  one type — annotate honestly (a union or leave intentionally broad) rather than wrongly.
- The generator's **own** signatures (`expr_to_ast(expr, rename)`, `term_grade_key(term)`,
  `dispatch_method(self_spec, method, gn_product, n, …)`, `generate_class(n, name)`, the nested
  helpers, etc.) are fair game — types here are static `ast`/`TypeSpec`/`sympy.Expr`/`int`/`str`.

## Decision needed — bring `tools/` under `ty`?

`ty check src` and `ty check tests` are **clean**, but **`ty check tools` is NOT** (today it reports
`no-matching-overload` on `sympy.simplify`, among others), and `tools/` is **not** in the project's
`ty` scope — `entrypoint/format.sh` runs only `ty check /gacalc/src`. Adding signatures to `tools/`
only pays off if we also type-check it. Options (pick one before starting):
1. **Bring `tools/` under `ty`** (add `ty check tools` to `format.sh`/CI) and resolve or narrowly
   suppress the pre-existing sympy-overload errors. Most value; most work.
2. **Annotate `tools/` but leave it out of `ty` scope** — signatures improve readability even without
   enforcement. Cheaper; no enforcement against drift.
3. **Skip `tools/`**, do only `nbplotutils.py` + the emitted generated annotations. Smallest.

Recommend **option 1** if the sympy errors are a handful and suppressible; otherwise **option 2**.

## Hard invariants / verification

- **Two different output contracts** depending on what's touched:
  - Editing the generator's **own** (non-emitted) signatures **must not change generated output** —
    verify byte-identical vs. a pre-change baseline of `src/gacalc/{scalar,g1,g2,g3}.py`.
  - Editing the generator's **emitted** annotations **will change generated output** (expected — like
    the slots task). There the gate is: `make check-generated` (determinism) + full suite + `ty`
    clean, **not** byte-identity.
- After each batch: regenerate, run `make test` (full suite, currently **226 passed**),
  `ruff check` clean, `ty check` clean on the chosen scope.
- Generated modules are gitignored, so the git diff is `tools/` + `src/gacalc/base.py`/`gn.py`/
  `transforms.py`/`nbplotutils.py` + maybe `format.sh`/CI — nothing under the generated `g*.py`.

## Plan (once approved + option chosen)

- [ ] Decide the `tools/`-under-`ty` option above.
- [ ] Snapshot the generated-file baseline (for the byte-identity checks on generator-internal edits).
- [ ] `astbuild.py` signatures (high-yield, mechanical AST types).
- [ ] `gen_specialized.py` own signatures (params + returns).
- [ ] Emitted annotations in the generator (type generated methods honestly; mind the broad-operand
      dispatch params) — regenerate, expect an output diff, run the determinism + suite gates.
- [ ] `nbplotutils.py` signatures + return types; `bench.py` (small).
- [ ] notebooks/display*.py (optional, low priority).
- [ ] If option 1: add `ty check tools` to `format.sh` (+ CI) and clear/scope the sympy errors.
- [ ] Final: `make test` (226+), `ruff`, `ty` (chosen scope) all clean; `make check-generated`.

## Notes / cross-refs

- `tasks/archive/2026/06/06/add-python-types.md` — the prior local-variable pass (what's already done,
  and what it deliberately scoped out: `cse` temporaries stay unannotated; repetitive notebook-demo
  locals skipped).
- `tasks/archive/2026/06/06/future-annotations-drop-forward-ref-quotes.md` — related annotation work.
- Coefficient typing is settled as `Coef = int | float | sympy.Expr` (CLAUDE.md Architecture); reuse
  it rather than `numbers.Real`, which `ty` rejects for arithmetic.
