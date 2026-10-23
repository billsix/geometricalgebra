# Consolidate the "arguments must be vectors (grade 1)" check behind one procedure

## BLUF

gacalc already has a procedure that validates a sequence is grade-1 vectors and raises otherwise —
**`_require_vectors`** in `src/gacalc/measure.py`. The same check is **re-implemented inline in
several other modules** (frame, vectorcalc, base, transforms), each with its own message and
sometimes a different exception type or an `assert`. This task: promote the one procedure to a shared
home and route the duplicate checks through it **where it makes sense**, leaving the internal/`assert`
and different-semantics cases alone. "Done" = one canonical vector-grade guard, the real-`raise`
duplicates call it, behaviour preserved (or any exception-type change is deliberate and changelogged),
`make test` + `make format` green. **Proposed — needs go-ahead** (and three decisions below).

## Status

**Status:** proposed — needs go-ahead (see Open questions — they settle the shared signature,
exception-type policy, and assert-vs-raise scope before any edit)
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-10-22 (William Emerison Six <billsix@gmail.com>: "there is some procedure somewhere
that ensures the parameters are vectors … find all references where they do a check like that, and
call the procedure instead, if it makes sense").

## The procedure (the thing to consolidate behind)

`src/gacalc/measure.py` › **`_require_vectors(vectors: Sequence[MultiVectorBase]) -> None`**:

```python
def _require_vectors(vectors: Sequence[MultiVectorBase]) -> None:
    """Raise unless ``vectors`` is a non-empty sequence of grade-1 vectors."""
    if len(vectors) == 0:
        raise ValueError("area/volume/content need at least one vector")
    for v in vectors:
        if not v.is_vector():
            raise ValueError(
                "area/volume/content take vectors (grade 1); got a non-vector: " + repr(v)
            )
```

It is module-private to `measure.py` and its messages are hardcoded to "area/volume/content". Already
called by `measure.area`/`volume`/`content`/`signed_*` (measure.py:113/143/228). The sibling pattern to
copy is `MultiVectorBase._require_scalar_plus_bivector(method_name)` (base.py:1927) — a `_require_*`
guard that takes a **context label** so the message names the caller.

## Where the same check is duplicated (full inventory)

`is_vector()` is `MultiVectorBase.is_homogeneous_of_grade_r(1)` (base.py:1041). Grep: `is_vector()` +
a nearby `raise`/`assert`. Three buckets:

### A. Real user-facing `raise` on a non-vector argument — **convert (makes sense)**
- `frame.are_linearly_independent` (frame.py:62) — loops the frame, `raise ValueError("a frame is a
  set of vectors (grade 1); got a non-vector: …")`. ⚠️ Its **empty** case must stay `return False`
  (frame.py:57), NOT raise — so call the helper only after the existing empty guard, or give the
  helper an `allow_empty` mode (Open Q1).
- `vectorcalc.cross` (vectorcalc.py:80) — loops `(a, b)`, `raise ValueError("cross takes vectors
  (grade 1); got a non-vector: …")`.
- `MultiVectorBase.bivector_from_vectors` (base.py:1964) — `raise TypeError("bivector_from_vectors
  takes two vectors (grade-1); got grades … and …")`. ⚠️ **TypeError, not ValueError**, and the
  message reports grades (Open Q2). `Gn.bivector_from_vectors` (gn.py:155) just delegates to it, so
  fixing the base fixes both; its docstring (gn.py:151) also says "TypeError".
- `transforms` rotation factory (transforms.py:476) — `if not (a.is_vector() and b.is_vector()):
  raise …` (mirrors `bivector_from_vectors`; same TypeError question).

### B. `assert …is_vector()` on public-API parameters — **judgment (Open Q3)**
These are dev-time asserts (AssertionError, silently disabled under `python -O`), and the docstrings
even advertise "Raises: AssertionError if … not a vector". Converting them to `_require_vectors`
upgrades them to a real always-on guard (and a documented exception) — reasonable for public entry
points, but it is a behaviour change:
- `MultiVectorBase.inner_product` / `outer_product` (base.py:1100–1101, 1149–1150).
- `MultiVectorBase.versor_from_vectors` (base.py:1802–1803).
- `transforms` factories (transforms.py:213–214, 224).

### C. Leave alone (do **not** convert)
- `MultiVectorBase.reject` / `reflect` inner asserts with `# TODO - can this be generalized?`
  (base.py:1470, 1531; transforms.py:224 mirror) — the assert marks a known scope limit, not an input
  guard. Leave until the TODO is resolved.
- `nbplotutils.py:322` `assert v1.is_vector() and v2.is_vector()` — a notebook plotting helper; an
  internal assert is fine.
- `g3.py:9261` `if not self.is_vector(): raise(... "Odd_3 is not a Vector …")` — **generated code**
  (`g*.py` are generated + gitignored — never hand-edit), AND it is a *different* check (an Odd_3→Vector
  cast, not "this parameter is a vector"). Exclude entirely.

## Proposed design (pending the Open questions)

1. **Move `_require_vectors` to `base.py`** — the lowest shared module (frame/vectorcalc/transforms/
   measure all import `base`; base imports none of them, so no cycle). Either a module-level function
   or a `@staticmethod` on `MultiVectorBase`. Add an optional **`context: str`** label (à la
   `_require_scalar_plus_bivector`) so each site keeps a meaningful message, and decide the empty-case
   policy (Open Q1). `measure.py` then imports it from `base` and drops its local copy; its callers are
   unchanged.
2. Replace each bucket-A inline check with a call to the shared procedure (preserving each site's
   message via `context`, and the frame empty-case).
3. Bucket B only if Open Q3 says so.

## Verification gate

- `make test` green (the ~650 suite; several tests assert on these raises — e.g. frame's
  `test_non_vector_input_raises`, measure/cross/bivector tests — so they pin the behaviour; if Open Q2
  standardises the exception type, update those tests deliberately and note it).
- `make format` clean (ruff + ty).
- If any exception type changes (Q2), add a `CHANGELOG.md` `[Unreleased]` entry — a consumer catching
  `TypeError` from `bivector_from_vectors` would be affected (breaking).
- No `src/gacalc/g*.py` edits (generated); the diff should be in `base.py` + `measure.py` + `frame.py`
  + `vectorcalc.py` + `transforms.py` only.

## Open questions
1. **Shared signature + empty policy.** **DECIDED 2026-10-22 (William Emerison Six
   <billsix@gmail.com>): the procedure lives in `base`, not `measure`** (lowest shared module; no
   import cycle). Remaining sub-question, your call: exact form — a `base` **staticmethod**
   `MultiVectorBase.require_vectors(vectors, context="")` (matches the `_require_scalar_plus_bivector`
   sibling) vs a module-level `base.require_vectors(...)` function — and the empty policy: keep the
   "at least one vector" check but make it opt-in (`require_nonempty=True` default) so
   `frame.are_linearly_independent`, which must return `False` not raise on empty, calls it with
   `require_nonempty=False` after its own guard. Recommend the staticmethod + opt-in empty check.
2. **Standardise the exception on `ValueError`?** `bivector_from_vectors` (and the `transforms` mirror,
   and `gn`'s delegating docstring) raise **`TypeError`** today; `_require_vectors`/frame/cross raise
   **`ValueError`**. Converging on `ValueError` is cleaner but changes the type a consumer might catch
   and drops the "got grades …" detail — a breaking change to changelog. Standardise to `ValueError`,
   or make the helper preserve the caller's chosen type/message?
3. **Convert the bucket-B `assert` sites too, or only the real `raise` sites?** Recommend converting
   the asserts on **public** parameters (`inner_product`/`outer_product`/`versor_from_vectors` and the
   `transforms` factories) to the real guard so grade misuse fails loudly even under `-O`, but leaving
   bucket C (the `# TODO` reject/reflect asserts, the notebook helper, generated code) as-is. Agree, or
   keep asserts as asserts and convert only bucket A?

## See also
- `src/gacalc/measure.py` — `_require_vectors` (the procedure) + `_require_scalar_plus_bivector` sibling in `base.py`.
- `tasks/reference/conditional-refactoring-rules.md` — the dedup (Rule B) / judgment-call conventions this follows.
