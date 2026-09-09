# Where gacalc deliberately does NOT annotate, and why

**What this is:** the standing list of every place in gacalc that skips a type annotation
on purpose, with the reason each one survives review. Written 2026-09-09 when the
repo-wide annotation sweep (`tasks/archive/2026/09/09/add-more-type-annotations.md`)
brought `src/`, `tools/`, `tests/` and `notebooks/` to the point where **every**
unannotated site is one of these.

**Why it exists:** without this list, each exemption looks like an oversight, and the next
sweep re-derives the same four dead ends. The governing rule is `CLAUDE.md` › "Coding
standard (Python)" › "(b) Judgment calls" › **"Type annotations — annotate generously"**,
including its escape hatch: *don't fight the checker* — a locally-correct annotation that
forces edits to unrelated logic, or breaks flow-narrowing, is not worth it.

## How to see the current state

`tasks/adhoc/` scripts are removed at archive time, so the auditor that produced these
counts is in the work commit's history rather than the tree. To regenerate the list, walk
the four directories with `ast` looking for: `def`s without a return annotation, params
without one, assignments to a bare name, `for`-targets, bare generics, `Any`, and
invariant `dict`/`list`/`set` params. Exclude the generated `src/gacalc/g*.py` (the
generator owns their annotations — fix `tools/gen_specialized.py`, never the output), type
aliases, `Enum` members, and `_` discards.

As of 2026-09-09 that walk returns **24 rows, all of them listed below**: 9 `Any`,
7 aliases, 3 enum members, 3 locals, 2 returns, 2 invariant params, 1 param, 1 loop target.

## The exemptions

### 1. `InvertibleFunction[Any]` on the plotting entry points (9 sites)

`src/gacalc/nbplotutils.py` — `create_basis`, `create_unit_circle`, `create_x_and_y`,
`_draw_labelled_triangle`, `draw_isoceles_triangle`, `draw_second_right_triangle`,
`draw_right_triangle`, `draw_ndc`, `draw_screen` all take `fn: InvertibleFunction[Any]`.

`CLAUDE.md` blesses `[Any]` for **a polymorphic parameter that accepts any transform and
applies it internally**. These functions plot whatever representation the caller hands
them; the transform generic is *invariant*, so any concrete parameter would reject a
caller passing a different representation. Note this is a *parameterized* `Any`, not a
bare generic — a bare `InvertibleFunction` would degrade the parameter to implicit `Any`
silently, which is the thing the rule is against.

The same reasoning covers `notebooks/displaymv.py`'s `S` alias for `scale_non_uniform`,
which is additionally **variadic** (`*factors: float`), hence `Callable[..., ...]`.

### 2. Returns left inferred (2 sites)

- **`MultiVectorBase.__iter__`** (`src/gacalc/base.py`) — annotating it `Generator[Coef]`
  makes ty treat a multivector as a destructurable iterable, so the `case [*sequence]:`
  patterns in project/reject/reflect match a lone multivector and widen the bound element
  type. A false positive: at runtime a multivector is not a `Sequence`. The docstring
  already states that iteration yields the coefficient values.
- **`to(cls, g)`** (`tests/test_conformance.py`) — callers invoke dimension-defaulting
  methods (`dual()`, `unit_pseudoscalar()`) on the result, which only the concrete
  specialized classes provide; `-> MultiVectorBase` would report missing-argument on those.

### 3. The dimension-defaulting test (1 param, and it is the only one)

`test_implicit_dimension_methods(n, cls)` in `tests/test_conformance.py` is the **only**
parametrized `cls` in the repo left inferred. Its subject is precisely the classmethods
that default `n` — and on the abstract `MultiVectorBase` that `n` is *required*, so
`cls: type[MultiVectorBase]` produces four missing-argument errors on the very calls under
test.

**Correcting an older, broader claim:** `to()`'s docstring used to say the parametrized
`cls` params were all deliberately unannotated. That was never measured. Annotating all 22
of them produced errors in exactly one test; the other 21 are now typed.

### 4. Two container params that must stay invariant

- **`astbuild._method_label(seen: set[str])`** — an *out*-parameter (`seen.add(label)`),
  not a read-only container, so the covariant `AbstractSet` would be wrong.
- **`astbuild.module_source(body: list[ast.stmt])`** — read-only here, so house style
  wants `Sequence`, but it is handed straight to `ast.Module(body=...)`, whose stdlib
  signature demands an invariant `list[stmt]`. Widening moves the error one line down.

### 5. Three locals whose declared type would lose information

- **`tests/test_graded.py`** — `cases`, and the `val`/`d` derived from it. The inferred
  concrete union keeps `val.dual()` (dimension-defaulting) and `val.DIMENSION` resolvable;
  `MultiVectorBase` does not. Same root cause as §2 and §3.
- **`tests/test_odd3.py`** — `conjugated`. Declaring `g3.Odd_3` is correct at runtime (the
  next line asserts exactly that), but it widens `coeff_e_123` to the full
  `Coef = int | float | sympy.Expr`, and sympy's stubs have no `simplify` overload taking
  a bare `int`/`float`.

Note the shape these share: **the abstract base is less capable than every concrete
subclass**, because dimension-defaulting overrides drop a required parameter. Any
exemption of this family traces back to that.

## What is NOT an exemption

Type aliases (`Coef`, `Blade`, `BladeCoef`, `MultiVectorFn`, `MultiVector = Gn`), `TypeVar`
definitions, `Enum` members, and `_` discards are not annotation candidates at all —
annotating one changes what it means. They are excluded from the audit rather than
exempted from it.

## Cross-links

- `CLAUDE.md` › "Coding standard (Python)" › "(b) Judgment calls" — the governing rule.
- `tasks/reference/conditional-refactoring-rules.md` — the sibling discretionary-sweep
  discipline (never churn what is already clear; protect what matters).
- `tasks/reference/generated-product-typing.md` — why the generated types are shaped as
  they are, which is what makes §5's abstract-vs-concrete gap exist.
