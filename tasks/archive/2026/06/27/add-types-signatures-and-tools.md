# Add Python type annotations as broadly as reasonable (signatures + tools + emitted)

**Created:** 2026-06-27 · **Completed:** 2026-06-27

## What it was

Signature coverage (parameters and return types) was extended across the under-typed modules, building
on the light-touch local-variable pass of `tasks/archive/2026/06/06/add-python-types.md` (which had
scoped out `cse` temporaries and repetitive notebook-demo locals). The measurement on 2026-06-27 showed
the hand-written algebra core (`base`/`gn`/`transforms`) already well typed; the gaps were the generator,
`astbuild.py` and `nbplotutils.py`. The policy stayed light-touch: annotate where it adds clarity or lets
`ty` catch real errors.

## Decision: bring `tools/` under `ty` (option 1)

`ty check src` and `tests` were clean, but `tools/` was outside the `ty` scope (`format.sh` ran only
`ty check /gacalc/src`) and reported `no-matching-overload` on `sympy.simplify`. Annotating `tools/`
pays off only if it is checked, so of the three options — (1) bring `tools/` under `ty`, (2) annotate
it but leave it unchecked, (3) skip `tools/` — option 1 was chosen, the sympy errors being few.
`format.sh` gained `ty check /gacalc/tools`.

## What was done (2026-06-27)

| module | untyped params before → after | no-return before → after |
| --- | --- | --- |
| `tools/gen_specialized.py` | 72 → 0 | 8 → 0 |
| `tools/astbuild.py` | 39 → 0 | 2 → 1 (`__init__`, conventional) |
| `tools/bench.py` | 2 → 0 | 1 → 0 |
| `tools/gen_proofs.py` | 0 → 0 | 0 → 0 (3 `sympy.simplify` errors fixed) |
| `src/gacalc/nbplotutils.py` | 27 → 0 | 13 → 0 |

- **astbuild.py:** AST-DSL signatures (`ast.expr`/`ast.stmt`/`Sequence`/`Iterable`/`Callable`). Real
  fixes the annotations surfaced: list invariance (`fn`/`cls` `body` typed `Sequence[ast.stmt]`, with
  `list(body)` inside); `lit` casts at the `ast.Constant` boundary (typeshed's value type omits the
  blade tuples it accepts at runtime); `isinstance_` narrowed to `list[ast.expr] | ast.expr`;
  `bool_or`/`bool_and` use `values=list(tests)`.
- **gen_specialized.py:** every helper signature typed (`TypeSpec`, `sympy.Expr`,
  `Callable[[Gn, Gn], Gn]`, blade `Sequence[tuple[int, ...]]`, cast callables, product/unary
  `-> tuple[TypeSpec, list[sympy.Expr]]`, the full `dispatch_method` parameter list, and the nested
  helpers). One real narrowing: `term_grade_key` guards `isinstance(sym, sympy.Symbol)` before
  `sym.name`, since `free_symbols` types as `set[Basic]`.
- **gen_proofs.py:** the 3 `no-matching-overload` errors were fixed with
  `sympy.simplify(sympy.sympify(...))`.
- **bench.py:** `to` / `time_ms` / `widen_sym` typed.
- **nbplotutils.py:** `fn: InvertibleFunction`, RGB colour triples, `graph_bounds: tuple[int, int]`,
  `_coef_as_float(coef: Coef)`, Figure/Generator returns. It showed that `generategridlines` /
  `generate_circle` are generators and `create_graphs` is a `@contextmanager`
  (`Generator[Axes, None, Figure]`), with no logic change.

**Emitted generated-method annotations were deliberately not added.** The remaining untyped parameters
of the generated `g*.py`/`scalar.py` methods are the polymorphic operands (`rhs`/`other`/`lhs`) that
`match` on any operand type; `ty check src` was already clean (a missing annotation is `Unknown`, not an
error), so a broad `object`/union annotation would add noise and catch nothing. The generated return
types were already precise. The optional `notebooks/display*.py` pass was not done.

## Verification

`ruff` and `ty check src tests tools` were clean on every file touched; the generated
`scalar/g1/g2/g3.py` were byte-identical to the pre-change baseline (generator-internal edits only); 226
tests passed.

A pre-existing `ruff` `T201` (`print` found) in `tools/gen_proofs.py`, from the in-progress latex-book
work, was flagged and left for that task.
