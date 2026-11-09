# Lift `prefix_blades` to a top-level reusable function (accumulate form)

**Created:** 2026-10-23 · **Completed:** 2026-10-23 (William Emerison Six <billsix@gmail.com>)

Requested by the maintainer: lift the prefix-wedge helper to module scope so other code (e.g. a
reciprocal frame) can reuse it, and write it with `itertools.accumulate`. A pure extraction, with no
behaviour change and no new math.

The prefix outer products `A_0 := 1`, `A_k := A_{k-1} ∧ v_k` (Hestenes & Sobczyk p. 27, eq 3.1)
were a nested closure `prefix_blades()` inside `make_orthogonal_frame_hestenes`. They became a
public, representation-agnostic, top-level free function `gacalc.frame.prefix_blades(vectors)`
in the `itertools.accumulate` form, and the Hestenes orthogonalization calls it. Output was
symbolically unchanged (the existing equivalence tests still passed).

## What was done

- **`src/gacalc/frame.py`** — added a module-level
  `def prefix_blades(vectors: Sequence[MultiVectorBase]) -> Iterator[MultiVectorBase]`, docstringed
  (H&S p. 27 eq 3.1; yields `A_0 = 1` then each prefix wedge; lazy; O(k)). Body is the maintainer's
  requested form, with the `initial=` keyword and no `chain` (decision 1):
  `accumulate(vectors, operator.xor, initial=type(vectors[0]).one())`. New imports: `operator`,
  `itertools.accumulate`. The nested `prefix_blades()` closure was deleted and
  `make_orthogonal_frame_hestenes`'s `hestenes_vectors` now calls `prefix_blades(vectors)`
  (`vectors` is nonempty there — the `is_frame` guard rejects the empty set first).
- **`tests/test_frame.py`** — added `prefix_blades` to the imports and four direct tests: 2D and 3D
  symbolic prefix blades, that the pairs feed the Hestenes `c_k = reverse(A_{k-1}) A_k` identically,
  and that an empty sequence raises `ValueError` (decision 2).
- **`CHANGELOG.md`** — `[Unreleased] / Added` entry for the new public function (additive, non-breaking).

## Decisions

1. **`initial=` over `chain`** — `accumulate(vectors, operator.xor, initial=type(vectors[0]).one())`.
2. **Empty input raises `ValueError`** — a public function must define the empty case, and there is no
   operand to pick a representation for the scalar `A_0 = 1` from (consistent with the frame functions
   requiring a nonempty linearly independent set).
3. **Name/location** — kept the name `prefix_blades`, in `frame.py` (its only current consumer, a
   frame/blade primitive). `frame.py` has no `__all__`, so a public (no-underscore) name is the export.
4. **Reciprocal frame** — NOT filed. It is new math (would need the Lean + symbolic-Python + prose
   trio) and was left for its own task when the maintainer wanted the design; it was the motivating
   future consumer of `prefix_blades` (later done as `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`).

## Verification (all green, 2026-10-23, in the existing `localhost/gacalc` image)

- `ruff check` + `ruff format --check` on `frame.py` + `test_frame.py` — clean.
- `ty check src/gacalc/frame.py tests/test_frame.py` — clean.
- `tools/check_changelog.py` — clean.
- Full `pytest` after `make generate` (GACALC_DIMS=1,2,3) — **711 passed** (707 + the 4 new), incl.
  the Hestenes/rejection equivalence tests that prove behaviour is unchanged.
- `make lean` was not run — no proof depends on this helper.

## Pointers

- `src/gacalc/frame.py` — `prefix_blades` (eq 3.1) + `make_orthogonal_frame_hestenes` (its consumer).
- `tasks/define-frame.md` — the broader frame-API task.
- `tasks/reference/content-area-volume.md` — `measure.py`'s free-function-over-`MultiVectorBase` style.
