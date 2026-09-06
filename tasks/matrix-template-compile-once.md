# Compile-once matrix templates: make `to_matrix` over symbols a library feature (a method on the function types)

**Status:** proposed — filed 2026-09-06 by Fable at the maintainer's request (William Emerison Six <billsix@gmail.com>: "eventually, not today"). Not started; needs the maintainer's go-ahead and the design call in Open questions.
**Priority:** 6
**Difficulty:** 4
**Consumer waiting on it:** `github.com/billsix/modelviewprojection` `tasks/ctc-use-gacalc-matrix-template.md` (blocked on this shipping), which deletes ten hand copies of the same code from its Code-the-Classics games.

## BLUF

`to_matrix(fn, cls, backend="sympy")` already turns an affine `InvertibleFunction` built over sympy
symbols into a symbolic homogeneous matrix. modelviewprojection's game renderers need that matrix
**per sprite per frame** with new numbers in the symbols' places, and `to_matrix` per call costs
~514 µs (it probes the basis with real gacalc arithmetic). What they do instead — and what this task
moves into gacalc — is **compile once, fill per call**: read off, from the symbolic matrix, which
entries are constants and which entry holds which symbol, then produce a fresh `np.float32` matrix
by copying the constants and poking the parameter values in: **0.47 µs**, versus 3.19 µs for the
two hand-built numpy matrices and a matmul it replaces. Ship it as a method on the function type
(`fn.to_matrix_template(params)` or similar — see Open questions), so a consumer writes:

```python
from gacalc import g3
from gacalc.transforms import scale_non_uniform, translate
TX, TY, W, H = sympy.symbols("tx ty w h")
MODEL = (translate(b=TX * g3.Vector.e_1 + TY * g3.Vector.e_2)
         @ scale_non_uniform(W, H, 1)).to_matrix_template(g3.Vector, (TX, TY, W, H))
...
m = MODEL.fill(tx, ty, w, h)      # per draw: a 4x4 np.float32, translation in the last column
```

## Context (cold start — read these first)

- `tasks/reference/transform-and-composable-function-layer.md` — the map of `functions.py`
  (`ComposableFunction[V]` at `functions.py:74`, `InvertibleFunction`, `@` composition, `linearity`)
  and `transforms.py` (`translate` `:148`, `scale_non_uniform` `:558`, `to_matrix` `:611` with the
  non-linear guard at `:661`; the `numpy`/`sympy` backends at `:693`). `to_matrix`'s convention:
  translation in the **last column** (column vectors, premultiply) — the same as modelviewprojection's
  `matrix_stack` and its GL upload with `GL_TRUE` (transpose) — keep it.
- The consumer's working implementation (the code to lift, verified bit-identical to hand-built
  numpy on 5000 random inputs and gated frame-identical in all ten games on 2026-09-06):
  `MatrixTemplate` in any modelviewprojection game engine, e.g.
  `ports/codetheclassics/vol2/eggzy/eggzy.py` (search `class MatrixTemplate`): a frozen dataclass of
  `constants: NDArray[np.float32]` (the matrix with parameter entries zeroed) and
  `slots: tuple[(row, col, parameter index), ...]`, a `compile(fn, params)` classmethod that calls
  `to_matrix(fn, g3.Vector, backend="sympy")`, classifies each entry by `free_symbols`, and a
  `fill(*params)` that copies the constants and assigns the slots. The rationale, numbers and the
  measuring script: modelviewprojection `tasks/reference/gacalc-transforms-in-the-renderer.md` and
  the archived `tasks/archive/2026/09/06/pgzero-gl-renderer-matrix-via-gacalc-perf.md` (its bench script was removed at archive; git history has it).
- The consumer's idiom for the translation vector (house rule in this repo's `CLAUDE.md`): a linear
  combination with every coefficient explicit — `tx * Vector.e_1 + ty * Vector.e_2` — never
  `Vector(tx, ty, 0)`.
- Tests for this layer: `tests/test_transforms.py` (has `to_matrix` cases to extend). Changelog:
  `CHANGELOG.md` `## [Unreleased]` (line 12). Dependencies already include numpy and sympy
  (`pyproject.toml:15`), so no new dependency.

## Design (what to decide before coding — the maintainer's call)

1. **Where it lives.** (a) a method `to_matrix_template(cls, params, *, n=None)` on
   `InvertibleFunction` (recommended: it is a property of the *function*, like `linearity`; reads as
   "this transform, as a fillable matrix"); (b) also on `ComposableFunction`, since a template only
   needs the forward map — `to_matrix` itself takes an `InvertibleFunction` today, so follow whatever
   it does; (c) a free function `to_matrix_template(fn, cls, params)` beside `to_matrix`. *(Recommend
   (a), delegating to a free function so (c) exists too, the way `to_matrix` is free.)*
2. **Parameter entries that are expressions, not bare symbols.** The renderer's model matrix has
   only bare symbols in its varying entries; an ortho over symbolic `w, h` would have `2/w`. Either
   restrict to bare symbols (raise otherwise — the consumer builds ortho once with numbers) or
   lambdify expression entries (`sympy.lambdify` per entry, ~1.45 µs per fill measured for a whole
   lambdified matrix — still 2× faster than hand-built). *(Recommend: bare symbols in v1, a clear
   `ValueError` otherwise; lambdified entries as a follow-on if a consumer needs them.)*
3. **Output dtype/shape.** `fill` returns a fresh `np.float32 (n+1)×(n+1)` (GL-ready), matching
   `to_matrix(backend="numpy")`; consider `fill_into(out)` to avoid the allocation for callers that
   reuse a buffer — measure before adding.
4. **Naming.** `MatrixTemplate` with `constants`/`slots`/`fill` is what the consumer uses today;
   any rename is fine as long as the consumer's blocked task is updated.

## Plan

- [ ] Implement per the design call (`src/gacalc/transforms.py`, next to `to_matrix`; the dataclass
      `frozen=True, slots=True`; a `fill` that never touches sympy).
- [ ] Tests (`tests/test_transforms.py`): the model matrix `translate @ scale_non_uniform` over four
      symbols fills bit-identically to `to_matrix(backend="numpy")` of the same transform with numbers
      substituted (a few random parameter sets, plus zero scale); a rotation over a symbolic angle is
      rejected or lambdified per design 2; a `ValueError` on a non-linear function (the `to_matrix`
      guard applies).
- [ ] Docstring with the consumer's four-line usage; a line in
      `tasks/reference/transform-and-composable-function-layer.md`.
- [ ] `CHANGELOG.md` `[Unreleased]` → Added; ship in the next release; tell modelviewprojection
      (its blocked task's recheck is the import).
- [ ] `ruff` + `ty check src tests` + full suite green.
