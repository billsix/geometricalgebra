# `Frame`: derive the orthogonal set instead of storing it, and make `vectors` a tuple field

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** conversation, 2026-11-09 (William Emerison Six <billsix@gmail.com>: "investigate what
it would take to 1) not store orthogonal vectors as an instance variable, but instead make it a
derived property, or whatever is standard python, like a method. 2) given this in the post init,
`object.__setattr__(self, "vectors", tuple(self.vectors))`, I'd like to get rid of that call. If the
field on the class should be a tuple, make that the type of the object, and update all callers to
make it a tuple")

## BLUF

`Frame` (`src/gacalc/frame.py`) is a frozen dataclass whose `__post_init__` makes two
`object.__setattr__` calls. One stores the computed `orthogonal_vectors`; the other turns the
caller's `vectors` sequence into a tuple. This task first investigates, then removes both:

- **(1)** derive the orthogonal set (a method or a cached property, whichever the investigation
  picks) instead of storing it in a field;
- **(2)** declare `vectors: tuple[MultiVectorBase, ...]` and make every caller pass a tuple.

Done means `__post_init__` has no `object.__setattr__`, there is no `orthogonal_vectors` field, the
chosen accessor is used everywhere, every `Frame(...)` call passes a tuple, and `make test` and
`make format` pass.

## Context

Read first:
- `src/gacalc/frame.py` › `class Frame`: the docstring, `__post_init__`, `coefficients`,
  `orthonormal_vectors`, `reciprocal_vectors` and `to_invertible_function`.
- `tasks/reference/frames-qr-and-reciprocal-frames.md` › "Why gacalc's `Frame` is stored orthogonal,
  not orthonormal". That section is about orthogonal versus orthonormal, not about storing versus
  deriving, so it stays true either way. Check its wording, though.

**The code today:**

```python
@dataclasses.dataclass(frozen=True)
class Frame:
    vectors: Sequence[MultiVectorBase]
    orthogonal_vectors: tuple[MultiVectorBase, ...] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        # make_orthogonal_frame raises ValueError on a non-frame.
        orthogonal_vectors: tuple[MultiVectorBase, ...] = tuple(
            make_orthogonal_frame(self.vectors)
        )
        object.__setattr__(self, "vectors", tuple(self.vectors))
        object.__setattr__(self, "orthogonal_vectors", orthogonal_vectors)
```

**`__post_init__` does a second job: validation.** Building the orthogonal set is what rejects a
non-frame (`make_orthogonal_frame` raises `ValueError`). With no stored set, `__post_init__` needs
an explicit check. Use the shared guard from `tasks/require-frame-guard.md`
(`require_frame(self.vectors, "Frame")`), so do that task first.

### (1) The orthogonal set: the standard Python options

| Option | Spelling at use sites | Cost | Notes |
|---|---|---|---|
| **Method** `orthogonal_vectors()` | `frame.orthogonal_vectors()` | recomputed per call | Matches the class's two other derived sets, `orthonormal_vectors()` and `reciprocal_vectors()`, which are already methods "computed on demand". |
| **`@property`** | `frame.orthogonal_vectors` | recomputed per access | Use sites keep their spelling, but a property hides an O(k²) symbolic orthogonalization behind attribute syntax, which a reader would expect to be cheap. |
| **`functools.cached_property`** | `frame.orthogonal_vectors` | computed once, on first access | Works on a frozen dataclass without `slots=True`: it writes the instance `__dict__` directly, bypassing the frozen `__setattr__`. It is not a field, so it doesn't change `__eq__`, `__hash__` or `__repr__`. Nothing in `src/` uses it yet. |

**Where recomputing would cost:**
- `coefficients()` reads `self.orthogonal_vectors` inside a nested comprehension, once per row
  (k recomputations).
- `to_invertible_function`'s "peel" inverse closes over `zip(self.orthogonal_vectors, self.vectors)`,
  once per application of the inverse.

With a method or a plain property, bind the set once to a local in each of these. Measure the 3D
symbolic case (`tests/test_frame_class.py`'s slow 3D cases, and `book/docs/notebooks/frame-qr-3d.py`)
before and after, and record the timings here.

**Users of `orthogonal_vectors` outside the class** (`git grep -n orthogonal_vectors`, excluding
`tasks/archive/`):
- `tests/test_frame_class.py`: 5 sites;
- `book/docs/notebooks/frame-qr-2d.py:67, 298` and `frame-qr-3d.py:69`, which unpack it
  (`w_1, w_2 = frame.orthogonal_vectors`). These pages are rendered in the book
  (`book/docs/frames-qr.rst`);
- the class docstring and its doctest (`frame.orthogonal_vectors == (2 * e_1, 3 * e_2)`);
- `tasks/reference/python-coding-standard-gacalc.md:103, 127` quotes it in examples;
- `tasks/frame-inverse-head-first-recursion.md` (open) discusses storing a second set "beside
  `orthogonal_vectors`". Update its wording to match whatever this task decides.

**Preliminary recommendation (the investigation confirms or overturns it):** make it a method,
`orthogonal_vectors()`, so all three derived sets are spelled the same way and are equally visible
as computations. Bind it once to a local where `coefficients()` and the peel inverse need it.
`cached_property` is the fallback if the measured cost of recomputing matters.

### (2) `vectors` as a tuple field

- Declare `vectors: tuple[MultiVectorBase, ...]` and drop the `object.__setattr__` conversion.
- **What the tuple is for: immutability, not hashing.** `Frame` is not hashable, with or without the
  tuple. Every multivector class defines `__eq__` without `__hash__`, so Python sets their `__hash__`
  to `None`, and the dataclass's generated hash fails on the elements. Checked 2026-11-09:
  `hash(Frame([2 * e_1, 1 * e_1 + 3 * e_2]))` raises `TypeError: unhashable type: 'Gn'`, and a `g2`
  frame raises it for `'Vector'`. The conversion protects the frozen frame from its caller instead.
  A stored list could still be changed through the caller's reference (`vs.append(...)`,
  `vs[0] = ...`), leaving the frame with vectors that no longer match its orthogonal set, or that no
  longer form a frame at all. Making the orthogonal set derived (part 1) removes the mismatch, but
  the vectors themselves could still change underneath the frame.
- **No newer Python feature does this conversion for you** (checked against 3.13–3.15). Field
  converters for `dataclasses` (PEP 712) were rejected; only the third-party `attrs` has them. There
  is no built-in frozen list. So the tuple annotation, with callers passing tuples, is the idiomatic
  shape, and `ty` catches a list passed by typed code. Decide whether `__post_init__` should also
  raise on a non-tuple, for untyped callers.
- **Callers that pass a list today** (`git grep -n "Frame(" -- src tests notebooks book`):
  - `src/gacalc/frame.py` doctests: 3;
  - `book/docs/notebooks/frame-qr-2d.py`: 3; `frame-qr-3d.py`: 1;
  - `tests/test_frame_class.py`: about 12. These include `Frame([])` in `test_non_frame_raises`,
    and `list(Frame(vectors_3d)) == vectors_3d`, which compares against a list variable that becomes
    a tuple.
  - `nbplotutils.py`'s match is a `pd.DataFrame(`, not a caller.
- **Changelog:** `Frame` is in `CHANGELOG.md` `[Unreleased]` › Added (not released yet), so no
  BREAKING entry is needed. Correct the Added entry instead: it shows `Frame([v_1, …, v_k])`, and
  should name the tuple argument and the accessor chosen in (1).

## Plan

- [ ] Do `tasks/require-frame-guard.md` first (`require_frame` replaces the validation that
  building the orthogonal set did).
- [ ] Measure the current cost of the 3D symbolic `Frame` cases.
- [ ] (1) Replace the `orthogonal_vectors` field with the chosen accessor. In `__post_init__`, call
  `require_frame(self.vectors, "Frame")`. Bind the set to a local in `coefficients()` and in the
  peel inverse. Update the docstring, its doctest, the tests, the two book notebooks and
  `python-coding-standard-gacalc.md`'s examples. Re-measure.
- [ ] (2) Annotate `vectors: tuple[MultiVectorBase, ...]` and delete the
  `object.__setattr__(self, "vectors", …)` line (with (1), the whole `object.__setattr__` pair goes).
  Make every caller listed above pass a tuple.
- [ ] Update the `CHANGELOG.md` `[Unreleased]` › Added entry for `Frame`, the wording in
  `tasks/frame-inverse-head-first-recursion.md`, and the reference doc's `Frame` description if it
  names the field.
- [ ] Gates: `make test`, `make test-full` (the slow 3D frame tests), `make format` (ruff + ty), and
  `make docs` (the two book notebooks run).

## Open questions

None yet. The investigation's choice between a method and `cached_property`, and whether to
reject a non-tuple at run time, will come back as questions if the measurements don't settle them.
