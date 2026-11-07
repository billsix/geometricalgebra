# `Frame` dataclass and its `InvertibleFunction` — done-record

**Completed:** 2026-11-04. Requested and decided by William Emerison Six <billsix@gmail.com>;
implemented by the agent.
**Resolved:** the "representation decision" in `tasks/define-frame.md`: a dedicated `Frame` class.
**Math and design rationale:** `tasks/reference/frames-qr-and-reciprocal-frames.md`.
**Follow-ups:** `tasks/frame-notebooks-epix.md` (the 2D/3D ePiX notebooks; blocked on the ePiX reset),
`tasks/lean-frame-class-invertible-function.md` (Lean equivalents; on hold),
`tasks/reciprocal-frame-hestenes.md` (on hold), `tasks/frame-svd-investigation.md`, and
`tasks/archive/2026/11/07/frame-prefix-blades-graded-zero-seed.md` (a pre-existing bug found along the way).

## What was built

`gacalc.frame.Frame` (`src/gacalc/frame.py`) is a frozen dataclass constructed from a frame's vectors.
It raised `ValueError` on a non-frame. It stores:

- `orthogonal_vectors`: the `w_j`, from the maintainer's rejection orthogonalization
  (`make_orthogonal_frame`);
- `coefficients[i][j] = (w_j · v_i) / |w_j|²`, so `v_i = Σ_j coefficients[i][j] * w_j`. The table is
  triangular with a unit diagonal.

`iter(frame)` rebuilds the original vectors, and `orthonormal_vectors()` returns the `u_j` on demand.
`to_invertible_function()` returns a `LINEAR` `InvertibleFunction`:

- forward: `f(x) = Σ (x · e_i) * v_i`;
- inverse: dot with each `w_j`, divide by `|w_j|²`, then back-substitute from the last coordinate.

It raises `ValueError` unless the frame spans the space. A private `_exact_quotient` keeps exact input
exact (`int / int` becomes a `Rational`). The construction is the QR decomposition with the lengths
factored out.

`tests/test_frame_class.py` has 20 tests:

- fully symbolic 2D and 3D frames on `Gn`, concrete oblique frames on the graded `g2`/`g3` types, and one
  float check;
- coverage: orthogonality, the triangular coefficients with unit diagonal, the rebuild, the span-volume
  ratios `|w_i|² * |A_{i-1}|² = |A_i|²`, `f(e_i) = v_i`, the `to_matrix` columns, the last reciprocal
  vector, and `k < n` raising;
- the maintainer's requirement: `(f⁻¹ ∘ f)(x) == x` and `(f ∘ f⁻¹)(x) == x` for a symbolic `x`, composed
  with `@`, in 2D and 3D.

## Chronology (harvested from the four commits on this work, 2026-11-04)

1. **Task created.** The maintainer asked for a dataclass that took a frame, stored an orthonormalized
   ordered set plus per-vector coefficients that rebuild the originals, exposed the originals through
   `__iter__`, and offered `to_invertible_function()`: forward `e_i ↦ v_i`, inverse by dotting with the
   orthonormal set. They also asked for 2D and 3D symbolic sympy tests, a Lean follow-up if sympy
   worked, an SVD attempt, and prior-art research. The agent identified the construction as the QR
   decomposition, standard in numerical linear algebra for solving systems and least squares. A web
   search found no source presenting it as a GA linear transformation built from rejections. The agent
   also showed that dotting with the orthonormal set gives `Qᵀ y`, so a triangular back-substitution is
   still needed. `define-frame.md`'s representation decision was marked decided.
2. **First answers.** `k < n`: `Frame` accepts it, and `to_invertible_function()` raises. Originals are
   not stored, and float inexactness is accepted. The SVD question became its own task. The maintainer
   also asked for a reference doc of the explanation (because "I remembered the name QR, but I had no
   idea what it was") and for 2D/3D ePiX notebooks.
3. **Notebook placement:** book notebooks (option (a), over standalone `notebooks/` demos), followed by
   the "implement" go-ahead.
4. **Implementation.**
   - *Orthonormal storage, rejected.* A prototype of the requested orthonormal storage did not decide the
     fully symbolic 3D rebuild within 10 minutes on `Gn`. The lazy `g3.Vector` built the frame in
     0.08 s, but its expressions grew too large for either `simplify` or `cancel` to decide equality.
     The cause was the `sqrt` of large symbolic polynomials.
   - *Orthogonal storage, adopted* (the maintainer's suggestion). Store the orthogonal `w_j` and divide
     by `|w_j|²`. Everything stayed rational, and 3D became decidable on `Gn` (151 s for the prototype's
     rebuild and both round trips).
   - *Hestenes orthogonalizations, rejected for `Frame`.* Both returned zeros on graded types (the
     `prefix_blades` bug). The `inverse` variant was slightly faster on `Gn`, but not enough to give up
     the rejection method, which the maintainer wrote and which works on every representation.
   - The maintainer stated that correctness mattered more than runtime, so the slow symbolic 3D tests
     stayed in the default suite.
   - The maintainer added the `(f⁻¹ ∘ f)(x) == x` symbolic round-trip requirement, and asked for the
     reciprocal-frame task, written as an explainer.
5. **Notebooks deferred.** The maintainer wanted figures rendered live in the notebook, not prebuilt.
   A spike showed two `epix.figure()` blocks in one process leaked state: the second figure's eepic was
   byte-identical to the first's. Resetting pen, line style, fill and labels by hand fixed the drawing
   but not the palette. A gacalc-side workaround was rejected in favour of an upstream fix
   (github.com/billsix/epix-mirror `tasks/reset-global-state-between-figures.md`; the maintainer
   accepted the explicit `reset_state()` recommendation), and the notebooks moved to
   `tasks/frame-notebooks-epix.md`, blocked until that fix is pushed.
6. **Later decisions.** The reciprocal-frame page/equation question and the Lean scope question were put
   on hold by the maintainer ("hold off on that for now").

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-04)

1. `k < n`: accepted by `Frame`; `to_invertible_function()` raises unless `k = n`.
2. Originals are not stored; `__iter__` rebuilds them. Usage is mainly symbolic, and float inexactness
   is accepted.
3. Stored orthogonal, not orthonormal (see the chronology, step 4, and the reference doc's section
   "Why gacalc's `Frame` is stored orthogonal, not orthonormal").
4. Correctness over runtime: the slow fully symbolic 3D tests stay in the default suite.
5. The three-forms rule (`CLAUDE.md`) was overridden: sympy first. Lean and the prose + LaTeX page are
   follow-ups.
6. The notebooks are book notebooks with figures rendered live, after the ePiX reset lands.
7. The SVD question is its own task.

## Verification

- The container `format.sh` gate passed: ruff, `ty`, the changelog check, and the ePiX keyword check.
  `tools/check_annotations.py` reported 0 findings for both new files.
- The `Frame` doctests passed.
- The full container `pytest` suite, with doctests: **714 passed** in 4 min 55 s.

## Docs touched

`CHANGELOG.md` `[Unreleased]` "Added: `Frame`"; the `CLAUDE.md` module-layout entry for `frame.py`;
`tasks/reference/frames-qr-and-reciprocal-frames.md` (new); `tasks/define-frame.md` (representation
decided, sweep unblocked); `tasks/lean-frame-coverage.md` (cross-link).
