# `src/` low cleanup: present-tense docstrings, docstring notation, dead code, moved-task citations

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §4.3, §2.4

## What changed

- **History narration rewritten to describe current behaviour:**
  - `base.py`: the `pseudoscalar_squared_sign` proof comment ("Phase 1 …"), `normalize`'s "already
    raised / without this guard", `inverse`'s "This replaces the older … flag", the `__rmul__`
    comment's "the previous …", `exp`'s "An earlier version …", `isclose`'s "the tests used to
    re-roll", and `_require_canonical_blades`' "replacing two old … failure modes";
  - the `transforms.py` module docstring: "backward compatibility" became what the re-export
    enables, and the "removed long before" parenthetical became a present-tense statement;
  - `frame.py` and `measure.py`: the "contrast the blade-square-sign task" asides are gone;
  - `nbplotutils.py`: `_to_xy` ("Was written inline …"), `_current_axes` ("this replaced …") and the
    `_axes` comment ("no longer clobber").
- **Docstring notation** (`CLAUDE.md` › "Math notation for readers"):
  - `prefix0 * 1 + prefix1 * e₁`, `(-1)^(n * (n-1)/2)`, `|R|² = 2 + 2 * cos(θ) = 4 * cos²(θ/2)`,
    `cosh(|A|) + sinh(|A|) * Â` (twice), `(A · B) * B⁻¹` (twice) and `A * k + c` in `base.py`;
  - `a_1 * b_2 - a_2 * b_1` in `measure.py`;
  - `reverse(A_{k-1}) * A_k`, `(-1)^(k-1) * (…) * A_n⁻¹` and `R⁻¹ * Qᵀ * y` in `frame.py`;
  - `A * x` (twice) in `functions.py`;
  - `versor_from_vectors` no longer says products are juxtaposition.

  The `⟨a b⟩` the review cited in `vectorcalc.py` was already gone. Docstrings in `base.py` reach the
  generated `g*.py` through the docstring injection.
- **Dead code removed:** `_coerce`'s `case sympy.Expr()` arm (identical to its default arm), the
  discarded `np.array(…buffer_rgba())` and its two now-unused imports, and the commented-out
  `ax.annotate` block.
- **Wrong text fixed:**
  - `gn.py`'s "G and G will be specialized" now names `g1.G`/`g2.G`/`g3.G`;
  - `measure.py`'s comment says `max_grade()` is 0 on zero, not that it raises;
  - "additon" became "addition";
  - `gn.py`'s `decrease_grade` uses a plain `if` instead of selecting `identity()` as a function.
- **Moved-task citations** now point at `tasks/reference/contraction-and-dot-definitions.md` (in place
  of the archived `investigate-dot-product-grade-0.md`) and `tasks/archive/2026/07/29/validate-blade-dict-keys.md`.

## Deliberately not changed

- **`MultiVectorBase.identity`** is public API (documented in `api.rst`). It duplicates
  `functions.identity`, but deleting it would break a consumer for no behaviour gain.
- **The unused `xcolor`/`ycolor` on `create_basis` and `color` on `draw_ndc`/`draw_screen`** are
  public keyword parameters the demo notebooks pass (`notebooks/displayg2.py`, `displaymv.py`).
  Removing them would break those calls.
- **`draw_ndc` duplicating `_draw_labelled_triangle`:** left for a plotting pass of its own.

## Verification

`ruff check` and `ruff format --check` are clean, and every `tasks/…` path cited in `src/` exists.
Container gates: `make test` (775 passed, 2 skipped), `make format`, `make check-generated`,
`make check-regions`, `make check-notebooks` and `make docs` all pass.
