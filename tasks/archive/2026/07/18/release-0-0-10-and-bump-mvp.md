# Cut gacalc 0.0.10 and bump mvp to it

**Created:** 2026-07-18 · **Completed:** 2026-07-18

gacalc **0.0.10** was released (tagged `v0.0.10`, pushed, live on PyPI) and modelviewprojection was
bumped to `gacalc>=0.0.10` with its image rebuilt.

## Why

`InvertibleFunction.__matmul__` was fixed (2026-07-18) to preserve invertibility in the *type*, not
just at runtime, but modelviewprojection consumes gacalc from PyPI (then `gacalc>=0.0.9`), so it could
not see the fix until a release.

### The bug that was fixed

`compose()` was correctly overloaded (`list[InvertibleFunction] -> InvertibleFunction`), but
`__matmul__` was declared once on `ComposableFunction` returning `ComposableFunction`. Since
`__matmul__` delegates to `compose()`, composing two invertible functions returned an
`InvertibleFunction` at runtime while typing as a bare `ComposableFunction`, so this correct line was a
type error:

```python
p1_to_ndc: InvertibleFunction[Vector2] = world_space_to_ndc @ p1_space_to_world_space
```

It was fixed with `@typing.overload`s on `InvertibleFunction.__matmul__` — invertible @ invertible →
invertible; invertible @ composable → composable — the same shape `compose()` already used and the same
narrowing `InvertibleFunction.at()` already did.

**Rejected: a generic bounded by the superclass** (the maintainer asked, 2026-07-18). Tested; recorded
so nobody retries it:

1. `def __matmul__[T: Composable[V]](self: T, f2: T) -> T` does not type-check: ty rejects it with
   `invalid-type-variable-bound: TypeVar upper bound cannot be generic`. Bounding by the bare
   unparameterized `Composable` severs the link to `V`, so the value type stops propagating.
2. It is unsound for subclasses: `self: T, f2: T -> T` binds `T` to the most-derived common type, so a
   user's `class Rotation(InvertibleFunction)` would get `Rotation @ Rotation -> Rotation`, while
   `compose()` only returns a plain `InvertibleFunction`. ty accepted that false claim in a probe.

Overloads state exactly what is true and nothing about subclasses.

## What was done

1. gacalc's `version` in `pyproject.toml` was bumped 0.0.9 → 0.0.10 first (PyPI and TestPyPI
   permanently reject a re-used version).
2. `make dist`, `make upload-test` (rehearsal), then `make release` (build + upload + host-side
   `git tag`).
3. mvp's `requirements.txt` was bumped to `gacalc>=0.0.10` and its image rebuilt.

## Verification

The affected mvp sites were 4 ty errors, its only non-glfw diagnostics:
`src/modelviewprojection/demos/demo06.py:135`, `:151` and `demo07.py:146`, `:162`. Installing this
repo's gacalc over the PyPI one in a throwaway container had already shown both files going to "All
checks passed!" with no mvp source change — the right outcome, since demo06/07 are book chapters
teaching invertible-function composition and the code was always correct.

After the release, mvp's `make format` went from **15 diagnostics to 10**, with no mvp source edits:
the 4 `ComposableFunction` → `InvertibleFunction` errors cleared, and a 5th (`to_matrix` at
`modelview2d.py:159`) cleared as a side effect. The 10 remaining were all the glfw/PyOpenGL stub class,
deliberately left (the maintainer: "leave them"), so mvp's `make format` still exited 1 by design;
that gate was tracked in github.com/billsix/modelviewprojection
`tasks/archive/2026/07/24/make-format-gate-is-red.md`.
