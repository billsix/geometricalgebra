# Cite Lagrange's identity everywhere it is used or referenced

**Created:** 2026-09-27 · **Completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>); a
citation-only change, `make format` green.

## Summary

Lagrange's identity, `‖a∧b‖² = ‖a‖²‖b‖² − (a·b)²` (equivalently `‖a‖²‖b‖² = (a·b)² + ‖a∧b‖²`; in 3D
`‖a∧b‖ = ‖a×b‖`), is what makes `‖a∧b‖ = ‖a‖‖b‖sin(θ)` and connects the wedge magnitude to the Gram
determinant. The task was filed 2026-09-27 at the author's request, after he found the identity had a
standard name and source. Every site in the codebase that invokes or names it now carries the name and
the link <https://en.wikipedia.org/wiki/Lagrange%27s_identity>, and the sites that use it under another
name (Gram determinant, area-from-wedge) were audited, each cited or ruled out.

## What was done

- **Already cited before the work** (found by the 2026-10-04 audit): the `MultiVectorBase.abs_sin`
  docstring (`src/gacalc/base.py`) and `proofs/GacalcProofs/Lagrange.lean` (module header; `lagrange_2d`,
  `lagrange_3d`).
- **2026-10-05**, after re-grepping `git grep -niI lagrange` (the inventory had grown with the rotor work):
  - **Notebooks:** the Lagrange cells of `notebooks/displayg2.py` and `displayg3.py` (name + link in the
    markdown).
  - **Source:** the `base.py` `rotor_from_vectors` docstring (the closed form
    `|R|² = 2|a||b|(|a||b| + a·b)`); and, by another name, `measure.py` `content` (`√det(Gram)`, which is
    Lagrange for k = 2) and `vectorcalc.py` `cross` (`|a||b| sin(θ)`).
  - **Tests / book:** `test_signed_sine.py`, `test_multivector.py`, `test_rotor_from_vectors.py`,
    `book/docs/notebooks/levels-of-abstraction.py`, one link each.
  - **Lean:** the `Trig.lean` header and `Rotor.lean`'s `normSq_versorFromVectors` docstrings point at
    `Lagrange.lean`, which carries the link (Lean sites cite the module rather than repeat the URL).
  - **Reference docs:** `tasks/reference/unit-bivector-and-rotors.md` §7, `tasks/reference/symbolic-equality.md`
    "Square roots", the `tasks/reference/lean-ga-proof-architecture.md` inventory line,
    `tasks/reference/lean-for-gacalc.md`, and the Gram-determinant line of
    `tasks/reference/content-area-volume.md`.

## Decisions

- **Ruled out:** `tasks/reference/dot-wedge-projection-rejection.md` has no wedge-magnitude relation, so it
  is not Lagrange. No generated docstring invokes the identity (`magnitude_squared` is "sum of squared
  coordinates"), so `tools/gen_specialized.py` was not changed. `CLAUDE.md` names only the Lean lemmas,
  which is a pointer, and was left as is.
- Only notebook markdown changed, so the notebooks were not re-executed (comment lines cannot affect
  execution).
