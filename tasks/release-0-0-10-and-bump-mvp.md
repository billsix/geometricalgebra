# Cut gacalc 0.0.10 and bump mvp to it

**Status:** **in progress 2026-07-18** — Bill is cutting the release. History squashed
(17 commits -> 2). Pre-flight verified: 286 tests pass, ruff/ty clean on src+tests+tools,
generator output byte-identical across two runs, no public API removed or added. **One
breaking change to note in the release:** `nbplotutils.generategridlines`'s first
parameter was renamed `graphBounds` -> `graph_bounds` by the naming pass; every caller in
both repos is positional, and mvp has its own copy of that function, so nothing breaks in
practice. Version chosen: **0.0.10** (Bill: "nobody but me uses this library right now").
**Created:** 2026-07-18

## Why

`InvertibleFunction.__matmul__` was fixed (2026-07-18) to preserve invertibility in the
*type*, not just at runtime. The fix is in this repo's working tree / history, but
**modelviewprojection consumes gacalc from PyPI** (`requirements.txt`: `gacalc>=0.0.9`,
0.0.9 installed), so mvp cannot see it until a release lands.

### The bug that was fixed

`compose()` was correctly overloaded (`list[InvertibleFunction] -> InvertibleFunction`),
but `__matmul__` was declared once on `ComposableFunction` returning
`ComposableFunction`. Since `__matmul__` delegates to `compose()`, composing two
invertible functions *returned* an `InvertibleFunction` at runtime while *typing* as a
bare `ComposableFunction`. So this was a type error despite being correct:

```python
p1_to_ndc: InvertibleFunction[Vector2] = world_space_to_ndc @ p1_space_to_world_space
```

Fixed by adding `@typing.overload`s on `InvertibleFunction.__matmul__` — invertible @
invertible -> invertible; invertible @ composable -> composable. Same shape `compose()`
already used, and the same narrowing `InvertibleFunction.at()` already did.

**Design note (Bill asked 2026-07-18 whether a generic bounded by the superclass would
be better than overloads).** Tested, and it does not work — recorded so nobody retries it:

1. `def __matmul__[T: Composable[V]](self: T, f2: T) -> T` **does not type-check at all**
   — ty rejects it with `invalid-type-variable-bound: TypeVar upper bound cannot be
   generic`. Bounding by the bare unparameterized `Composable` instead severs the link to
   `V`, so the value type stops propagating through composition.
2. Even ignoring that, it is **unsound for subclasses**. `self: T, f2: T -> T` binds `T`
   to the most-derived common type, so a user's `class Rotation(InvertibleFunction)`
   would get `Rotation @ Rotation -> Rotation` — accepted by the checker, but
   `__matmul__` delegates to `compose()`, which only ever returns a plain
   `InvertibleFunction`. Verified: ty accepted that false claim in a probe.

Overloads state exactly what is true and nothing about subclasses.

## What downstream needs it

**modelviewprojection**, 4 ty errors, currently the only non-glfw diagnostics in its
gate (see mvp's `tasks/make-format-gate-is-red.md`):

- `src/modelviewprojection/demos/demo06.py:135`, `:151`
- `src/modelviewprojection/demos/demo07.py:146`, `:162`

**The demos need no edits.** Verified by installing this repo's gacalc over the PyPI one
in a throwaway container: both files go from 4 errors to "All checks passed!" with no
change to mvp source. That is the right outcome — demo06/07 are book chapters teaching
invertible-function composition, and the code was always correct.

## Steps

1. **gacalc:** bump `version` in `pyproject.toml` (0.0.9 -> 0.0.10). PyPI and TestPyPI
   both permanently reject a re-used version, so this must happen first.
2. `make dist`, then `make upload-test` to rehearse, then `make release` (build + upload
   + host-side `git tag`). All run in the container; the only host step is `git tag`.
   `release` refuses if a `v<version>` tag already exists.
3. **mvp:** bump `requirements.txt` to `gacalc>=0.0.10`, rebuild the image so the venv
   picks it up.
4. **mvp:** re-run `make format` and confirm the 4 `invalid-assignment` errors are gone.
   The 11 glfw/PyOpenGL stub diagnostics will remain — those are a separate decision,
   tracked in mvp's gate task.

## Gate

mvp's `make format` shows 11 diagnostics instead of 15, all of them the glfw stub class,
with zero changes to mvp source.
