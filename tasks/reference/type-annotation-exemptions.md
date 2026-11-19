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

**`python tools/check_annotations.py`** — the auditor built for the sweep, promoted out of
`tasks/adhoc/` because it answers "has coverage regressed?" on any future change. It walks
`src/`, `tools/`, `tests/` and `notebooks/` (the demo and book notebooks alike) with `ast`
reporting: `def`s without a return
annotation, params without one, unannotated assignments (to a bare name, or each name of an
unpacking such as `a_1, a_2 = sympy.symbols(...)`), `for`-targets, bare generics,
`Any`, and invariant `dict`/`list`/`set` params. A name counts as annotated only within its own
scope (the module, a class body, or one `def`). It excludes the generated
`src/gacalc/g*.py` (the generator owns their annotations — fix
`tools/gen_specialized.py`, never the output) and anything gitignored, and classifies type
aliases, `Enum` members and `_` discards out of the count, since annotating one of those changes
what it means.

`--full` prints every row, `--kind` and `--path` narrow it.

**It is a report, not a gate**: it always exits 0 and no `make` target runs it, because
deciding whether a row is an exemption needs a human (the maintainer's decision, William
Emerison Six <billsix@gmail.com>, 2026-11-09).

**Floor (re-baselined 2026-11-18):** the auditor reports **63 rows in 19 files** — every one
either a listed exemption below or a *classified-out* row (a type alias or an `Enum` member,
which the auditor prints but does not treat as a gap). The split: **45 classified-out** (14
type aliases, 31 enum members, most of them from the GL and Cayley modules moved in from
modelviewprojection) and **18 listed exemptions** (9 `Any` §1, 2 returns §2, 1 param §3, 3
invariant params §4, 3 locals and loop targets §5). Anything *not* on this list is a genuine
gap: annotate it, or add it here with its reason. Records:
`tasks/archive/2026/10/09/re-baseline-annotation-auditor.md` (the earlier 32-row floor),
`tasks/archive/2026/11/09/annotation-auditor-floor-drift.md` (the per-scope and unpacking
detection, and the 66 gaps it found and fixed),
`tasks/archive/2026/11/18/re-baseline-annotation-auditor-after-gl-move.md` (the moved-in GL and
Cayley modules, 97 rows, annotated; one generator parameter widened to `Mapping`), and
`tasks/archive/2026/11/18/notebooks-like-displaymv.md` (the 6 notebook symbol unpacks of §6,
now declared).

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

- **`MultiVectorBase.__iter__`** (`src/gacalc/base.py`) — annotating it `Generator[Real]`
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

### 4. Three container params that must stay invariant

- **`astbuild._method_label(seen: set[str])`** — an *out*-parameter (`seen.add(label)`),
  not a read-only container, so the covariant `AbstractSet` would be wrong.
- **`astbuild.module_source(body: list[ast.stmt])`** — read-only here, so house style
  wants `Sequence`, but it is handed straight to `ast.Module(body=...)`, whose stdlib
  signature demands an invariant `list[stmt]`. Widening moves the error one line down.
- **`check_annotations.check_function(out: list[Finding])`** — the auditor's own
  accumulator, appended to. Same out-parameter case as `_method_label`.

### 5. Locals whose declared type would lose information

- **`tests/test_graded.py`** — `cases`, the loop's `val`/`expected` drawn from it, and the
  `d` derived from `val` (2 LOCAL rows and 1 LOOP row). The inferred concrete union keeps
  `val.dual()` (dimension-defaulting) and `val.DIMENSION` resolvable; `MultiVectorBase` does
  not. Same root cause as §2 and §3.

The `test_graded` rows share their shape with §2 and §3: **the abstract base is less capable
than every concrete subclass**, because dimension-defaulting overrides drop a required
parameter. Any exemption of this family traces back to that.

### 6. (gone 2026-11-18) `sympy.symbols` unpacks in the pyright-checked notebooks

The demo notebooks used to leave their `a_1, a_2 = sympy.symbols(...)` names undeclared: pyright
resolved `a_1 * e_1` through sympy's `Expr.__mul__` once `a_1` was declared `sympy.Symbol`. The
2026-11-18 notebook rewrite (`tasks/archive/2026/11/18/notebooks-like-displaymv.md`) writes the
coefficient through the scalar constructor instead (`Scalar(a_1) * e_1`, `Gn.from_real(v1) * e_1`,
as `CLAUDE.md` asks), so the names are declared and the rows are gone.

## What is NOT an exemption

Type aliases (`Real`, `Blade`, `MultiVectorFn`, `MultiVector = Gn`), `TypeVar`
definitions, `Enum` members, and `_` discards are not annotation candidates at all —
annotating one changes what it means. They are excluded from the audit rather than
exempted from it.

## Cross-links

- `CLAUDE.md` › "Coding standard (Python)" › "(b) Judgment calls" — the governing rule.
- `tasks/reference/conditional-refactoring-rules.md` — the sibling discretionary-sweep
  discipline (never churn what is already clear; protect what matters).
- `tasks/reference/generated-product-typing.md` — why the generated types are shaped as
  they are, which is what makes §5's abstract-vs-concrete gap exist.
