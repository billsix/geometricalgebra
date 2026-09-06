# Compile-once matrix templates: make `to_matrix` over symbols a library feature (a method on the function types)

**Status:** done — implemented 2026-09-06 (Fable session) on the maintainer's go-ahead ("go ahead and
… implement the composition of functions to matrix task. Make sure to make plenty of unit tests, and
this function should work in 2d, 2d affine (rotation and translation 3x3), 3d, and 3d affine (4x4)").
Gates green; ships in 0.0.20 (`CHANGELOG.md` `## [0.0.20]` › Added / Changed).
**Priority:** 6
**Difficulty:** 4
**Consumer:** `github.com/billsix/modelviewprojection` `tasks/ctc-use-gacalc-matrix-template.md`
(deletes ten hand copies of the same code from its Code-the-Classics games once a release carries this).

## BLUF

`gacalc.transforms` now has `to_matrix_template(fn, cls, params, n=None)` returning a
`MatrixTemplate`, plus method forms `fn.to_matrix(...)` and `fn.to_matrix_template(...)` on
`ComposableFunction`. A template is `to_matrix(fn, cls, backend="sympy")` read off once: constants
stored, bare-parameter entries recorded as `(row, col, k)` slots, compound entries lambdified together.
`fill(*numbers)` copies the constants and assigns the slots (and, only if there are expression entries,
evaluates them in one call), returning a fresh `(n+1)×(n+1)` `np.float32` with translation in the last
column. Verified in 𝒢₂ linear + affine (3×3), 𝒢₃ linear + affine (4×4), and `Gn` with explicit `n`.

## Context

- Filed 2026-09-06 at the maintainer's request after modelviewprojection measured the pattern
  (`to_matrix` per call ≈ 514 µs; compile-once fill 0.47 µs; hand-built numpy 3.19 µs — its
  `tasks/reference/gacalc-transforms-in-the-renderer.md`). The consumer's `MatrixTemplate`
  (constants + slots + `fill`) was the code to lift; it was verified bit-identical to hand-built numpy
  on 5000 inputs and gated frame-identical in all ten games.
- The map of this layer: `tasks/reference/transform-and-composable-function-layer.md`.

## Decisions

The task's four open design questions were resolved by the agent under the maintainer's blanket
go-ahead; each is reversible cheaply.

1. **Where it lives — both a free function and a method.** `to_matrix_template` + `MatrixTemplate`
   sit in `transforms.py` next to `to_matrix` (the free-function form, like `to_matrix`). The method
   forms live on **`ComposableFunction`** (so `InvertibleFunction` inherits them) rather than on
   `InvertibleFunction` alone, because a matrix needs only the forward map and the `linearity` tag;
   for the same reason `to_matrix`'s parameter was **widened** from `InvertibleFunction[Any]` to
   `ComposableFunction[Any]` (a hand-built linear `ComposableFunction` is now matrix-able). A
   `to_matrix` method was added alongside, since the maintainer's ask was "the to-matrix work … as a
   method on the function type". The methods import `gacalc.transforms` **inside their bodies**
   (with `TYPE_CHECKING`-guarded imports for annotations) so `functions.py` remains an import-free
   leaf at load time — recorded as the one deliberate exception in the reference doc's layering
   section.
2. **Expression entries are supported, not rejected.** The maintainer required "2d affine (rotation
   and translation 3x3)" to work; a symbolic rotation angle produces `cos`/`sin` entries, which a
   bare-symbols-only v1 would have refused. All expression entries of a template are compiled into
   ONE `sympy.lambdify(params, [exprs], "math")` and evaluated per fill; templates with no such
   entries never touch sympy in `fill` (the fast path the renderer uses). Expressions are kept exactly
   as `to_matrix` built them (no `simplify` — unpredictable compile latency for no per-fill gain).
3. **Output.** A fresh `np.float32 (n+1)×(n+1)` per fill, matching `to_matrix(backend="numpy")`.
   No `fill_into(out)` — the allocation was not measured to matter; add it if a consumer measures it.
4. **Names.** `MatrixTemplate` / `constants` / `slots` / `fill` kept from the consumer so its call
   sites (`MODEL.fill(tx, ty, w, h)`) do not change; new public fields `params`,
   `expression_cells`, `expressions`, `evaluate_expressions`, and `shape`; `__call__` = `fill`.
   Built only via `to_matrix_template` (frozen, slotted dataclass).
5. **Errors.** `ValueError` for a non-linear function (the `to_matrix` guard), for a symbol the
   matrix depends on that is not in `params` (named in the message), and for a repeated parameter;
   `TypeError` for the wrong number of `fill` arguments. A listed-but-unused parameter is ignored.

## What shipped

- `src/gacalc/transforms.py`: `MatrixTemplate`, `to_matrix_template`, `to_matrix` widened; `__all__`;
  doc-region markers `matrix template class` / `matrix template fill` / `to matrix template function`.
- `src/gacalc/functions.py`: `ComposableFunction.to_matrix` and `.to_matrix_template`.
- `tests/test_matrix_template.py` (24 tests): 𝒢₂ linear scale and the parameter-free quarter turn;
  𝒢₂ affine translate∘scale **bit-identical** to `to_matrix` over 27 parameter sets (incl. zeros);
  𝒢₂ rotation+translation via expression entries (`allclose`, and θ = π/2 equals the quarter turn);
  𝒢₃ scale (4×4 diagonal), rotation about e₂, the sprite model matrix bit-identical, rotation +
  translation, and composition ≡ matrix product; `Gn` with explicit `n` and the missing-`n` error;
  the method forms; a plain `ComposableFunction`; fresh-array, `__call__`, parameter order, unused
  parameter, int values, frozen; the four error paths.
- Docs: `CHANGELOG.md`, `CLAUDE.md` (transforms bullet + the leaf-module paragraph), `README.md`,
  `tasks/reference/transform-and-composable-function-layer.md`.
- Gates (modelviewprojection image, 2026-09-06): ruff check/format clean, ty clean, full suite
  passes (451), the new docstring examples pass under `python -m doctest`, doc-region markers OK.
