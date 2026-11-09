# `Frame`: derive the orthogonal set instead of storing it, and make `vectors` a tuple field

**Created:** 2026-11-09
**Completed:** 2026-11-09, on branch `gn-frozendict-and-frame-tuple` (a committed batch)
**Source:** conversation, 2026-11-09 (William Emerison Six <billsix@gmail.com>: "investigate what
it would take to 1) not store orthogonal vectors as an instance variable, but instead make it a
derived property, or whatever is standard python, like a method. 2) given this in the post init,
`object.__setattr__(self, "vectors", tuple(self.vectors))`, I'd like to get rid of that call. If the
field on the class should be a tuple, make that the type of the object, and update all callers to
make it a tuple")

## Outcome

`Frame` (`src/gacalc/frame.py`) is a frozen dataclass with one field,
`vectors: tuple[MultiVectorBase, ...]`. Its `__post_init__` makes no `object.__setattr__` call. It
raises `TypeError` on a non-tuple and then calls `require_frame(self.vectors, "Frame")`, the shared
guard from `tasks/archive/2026/11/09/require-frame-guard.md`. That guard took over the validation
that building the stored orthogonal set used to do.

The orthogonal set is the method `orthogonal_vectors()`, which returns
`tuple(make_orthogonal_frame(self.vectors))`. It is spelled like the class's other two derived
sets, `orthonormal_vectors()` and `reciprocal_vectors()`. `coefficients()`, `orthonormal_vectors()`
and the peel branch of `to_invertible_function` each compute it once and reuse it.

Every caller passes a tuple: the doctests, `tests/test_frame_class.py` (including `Frame(())` and the
new `test_non_tuple_raises`), and the two book notebooks `book/docs/notebooks/frame-qr-2d.py` and
`frame-qr-3d.py`. Also updated:

- the `CHANGELOG.md` `[Unreleased]` › Added entry for `Frame`;
- `CLAUDE.md`'s `Frame` description;
- `book/docs/frames-qr.rst`;
- `tasks/reference/frames-qr-and-reciprocal-frames.md`: its heading is now "Why gacalc's `Frame`
  uses the orthogonal set, not the orthonormal one", and the three citations of it were updated;
- the examples in `tasks/reference/python-coding-standard-gacalc.md` and
  `tasks/reference/symbolic-equality.md`;
- the wording in `tasks/frame-inverse-head-first-recursion.md` and
  `tasks/lean-frame-class-invertible-function.md`.

## Decisions

1. **`Frame` takes a tuple, and every caller passes one explicitly** (William Emerison Six
   <billsix@gmail.com>, 2026-11-09: "make the dataclass Frame take a tuple as an argument, so that
   you don't need to wrap it in a a tuple, and then update all callers to pass in a tuple
   explicitly"). The tuple is there for immutability, not hashing. `Frame` stays unhashable because
   multivectors define `__eq__` without `__hash__`. No Python 3.13–3.15 feature converts a field
   (PEP 712 was rejected), and `frozendict` has no sequence counterpart.
2. **The orthogonal set is a method, not a `property` or a `cached_property`.** A `property` would
   hide an O(k²) symbolic orthogonalization behind attribute syntax. `cached_property` was the
   fallback, kept for the case where the measurement below showed a cost that mattered. It didn't
   (agent's call, 2026-11-09).
3. **`__post_init__` rejects a non-tuple with `TypeError`**, for untyped callers (a notebook, a
   REPL). A list stored in the frame could still be changed through the caller's reference. This is
   a genuine `isinstance` type check, the one case CLAUDE.md reserves `TypeError` for (agent's call,
   2026-11-09).

## Measurement

Host, `python -m pytest tests/test_frame_class.py -m slow --durations=0`, the seven slow 3D cases:

| Test | Before (stored field) | After, first run | After, tests bind once |
|---|---|---|---|
| `inverse_methods_are_equivalent_symbolic[3d]` | 470.5 s | 475.9 s | 468.9 s |
| `composed_round_trip…[3d-peel]` | 410.5 s | 424.4 s | 418.7 s |
| `composed_round_trip…[3d-reciprocal]` | 275.8 s | 279.5 s | 275.5 s |
| `coefficients_are_triangular…[frame_3d]` | 207.5 s | 217.1 s | 214.5 s |
| `squared_lengths…[frame_3d-vectors1]` | 35.9 s | 54.1 s | 44.5 s |
| `orthogonal_vectors_are_mutually_orthogonal[frame_3d]` | 22.1 s | 22.5 s | 22.3 s |
| `coefficients_rebuild_the_vectors[frame_3d]` | 3.8 s | 31.2 s | 13.0 s |
| **Total** | **1426.5 s** | **1505.2 s** | **1457.9 s (+2.2%)** |

The first run's regression came almost entirely from two tests that called
`frame.orthogonal_vectors()` once per row, or twice in one test. Both now bind it once to a local,
as the library methods do. Those two tests still cost about 18 s more than before. With the
stored field, the shared `frame_3d` fixture computed the set once for every test; now each test that
reads the set computes it once. Over a 24-minute run that is not a cost that matters, so
`cached_property` was not adopted. The other five tests changed by under 4%.

Gates, run on commit `92aa57f` plus the ruff reformat:

- `make test-full`: 793 passed, 2 skipped, 27:43;
- `make format`: clean;
- `make docs`: the book built, including both notebooks.

`ruff check` and `ruff format --check` passed on the test rebinding afterwards.
