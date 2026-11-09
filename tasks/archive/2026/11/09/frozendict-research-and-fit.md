# `frozendict`: is it released, can gacalc use it, and would it improve the code?

**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** conversation, 2026-11-09 (William Emerison Six <billsix@gmail.com>: "regarding
frozendict, research online to see if it's out, and if it's in the version of python we use. And
then, analyze the whole codebase here and see if using it, let's say for bladereal, or gn, or
anything, would make our codebase better. after that's done, then reanalyze the other task we just
made.")

## Summary

`frozendict` is a built-in in Python 3.15.0, the version the sandbox and the image run. In gacalc,
one place benefits: `Gn`'s coefficient storage. Storing a `frozendict` makes the shared-state bug
fixed earlier on 2026-11-09 (`Gn.to_blade_dict()` handing out its internal dict, so a caller could
corrupt `e_1`) impossible by construction, and lets `to_blade_dict()` return the stored mapping with
no copy. Measured, this costs nothing: every `Gn` operation, the code generator and the test suite
ran within noise of the baseline, and `to_blade_dict()` itself got 4× faster. Nothing else in the
codebase gains from it. The adoption is scaffolded as
`tasks/archive/2026/11/09/gn-frozendict-coefficient-storage.md`. The `Frame` task needs no change.

## Decisions

1. **If gacalc adopts `frozendict`, raise `requires-python` to `>=3.15`, with no fallback** (William
   Emerison Six <billsix@gmail.com>, 2026-11-09: "update the task to upgrade pyproject.toml for
   python 3.15.0, if we decide to implement frozendict in our codebase"). It is breaking for
   consumers on 3.13 and 3.14, so the adoption carries a `CHANGELOG.md` BREAKING entry.
2. **Making `Gn`'s storage immutable is the wanted outcome** (the same, 2026-11-09: "regarding the
   concrete use, that sounds like a win!"). The measurements below found no cost that argues
   against it.

## Phase 1: is it released? Yes, in 3.15.0

- **PEP 814, "Add frozendict built-in type"** (Victor Stinner, Donghee Na): Status **Final**,
  Python-Version 3.15, accepted by the Steering Council on 2026-02-11
  (https://peps.python.org/pep-0814/, checked 2026-11-09). Real Python's March 2026 news covered the
  acceptance (https://realpython.com/python-news-march-2026/) and wrote up the type
  (https://realpython.com/python315-frozendict/).
- **Python 3.15.0** was released on 2026-10-09. The secondary source is
  https://braindetox.kr/en/posts/python_3_15_release_utf8_frozendict_sentinel_2026.html; the
  interpreters here agree, reporting `3.15.0 (3.15.0-1.fc45.x86_64, Oct  9 2026)`.
- **Both interpreters have it** (2026-11-09): the sandbox's `python3` and the image's `/venv`
  Python both print `<class 'frozendict'>` for the bare name, with no import needed.
- **Semantics, tried directly:**
  - It is not a `dict` subclass (its MRO is `frozendict, object`), but it is a
    `collections.abc.Mapping`, and it compares equal to a `dict` with the same items.
  - It is hashable when its values are, and sympy values are.
  - `f[k] = v` raises `TypeError`; `f | {...}` returns a new `frozendict`.
  - `frozendict(f) is f` and `f.copy() is f`, so re-wrapping or "copying" an existing one is free.
- **Micro-costs** (8 entries, best of 5): `frozendict(d)` 83.5 ns against `dict(d)` 82.1 ns;
  lookups are identical (22 ns). Wrapping a comprehension adds about 80 ns
  (`frozendict({...})` 360 ns against `{...}` 279 ns).
- **Type-checking:** `ty` 0.0.91 knows the type, but only once `requires-python` allows it: with
  `>=3.13` it reports `unresolved-reference: frozendict`.

## Phase 2: where it helps gacalc, and where it doesn't

The discovery is `tasks/adhoc/frozendict-research-and-fit/discover.sh`, and its output is in that
folder's `data/`: 23 `dict[` annotations, 63 `BladeReal` uses, 13 `coefficient_of_blade` sites and 5
module-level dict constants.

### `Gn.coefficient_of_blade`: adopt

- `Gn` (`src/gacalc/gn.py`) is a mutable dataclass. `__post_init__` rebuilds the dict twice (simplify,
  then drop zeros), and `to_blade_dict()` returns `dict(self.coefficient_of_blade)`, a copy, so
  callers can't corrupt shared constants.
- **Nobody needs a mutable result.** Of the 24 sites that bind a `to_blade_dict()` result, only
  `tests/test_multivector.py::test_to_blade_dict_is_a_copy` writes into it, and that write exists
  to prove the copy protects `e_1`. Every other site only reads.
- **Typing design that works** (tried in a scratch worktree with `requires-python = ">=3.15"`):
  - make `BladeReal = Mapping[Blade, Real]`, the read-only interchange type that both a `dict`
    and a `frozendict` satisfy;
  - keep the `Gn` field typed `BladeReal`, so `Gn({...})` with a dict literal still type-checks
    (the dataclass constructor takes the field's type);
  - store `frozendict(...)` in `__post_init__`, and return it from `to_blade_dict()`.

  With that, `ty` passes on `src/`, `tools/` and `book/docs/notebooks/`. The only `tests/` error is
  the deliberate write at `test_multivector.py:444`. Typing the field as `frozendict[...]` instead
  produced 13 errors in `src/` and 16 in `tests/`, because every `Gn({...})` call would then have to
  pass a `frozendict`.
- **The one builder that writes into a `BladeReal`:** `nbplotutils._expand_numerators_dict`
  (`out: BladeReal = {}`, then `out[blade] = …`). `ty` let it pass because it narrows the local to
  the assigned `dict`, but its declaration should become `dict[Blade, Real]` to say what it is. The
  other annotated builders are test literals that are never written to
  (`data/bladereal-builders.txt`).
- **Hashing is not on the table.** A `frozendict` of sympy values is hashable, but `Gn` must not
  gain a `__hash__`: its `__eq__` is value equality (it simplifies the difference), so two
  structurally different but equal values would hash differently, which breaks the hash contract.
  `Gn` stays unhashable, as every multivector class is today.

### Everything else: leave as is

- **The specialized `g*.py` classes** store coefficients in fields, and their generated
  `to_blade_dict()` builds a fresh dict per call, which already satisfies a `Mapping` return type.
  Nothing to change in the generator.
- **`base._blade_display_symbols`**, the session display-symbol registry, is changed in place by
  `set_blade_symbols` (`clear()` then `update()`). A `frozendict` would mean rebinding the global
  through `global`, for no gain: it is private and already snapshots its input.
- **The tools' lookup tables** (`gen_specialized.DOCSTRINGS`, `CUSTOM_METHOD_DOCS`, `GRADE_NAMES`,
  `check_epix_keywords.KNOWN`, `bench.SPECIALIZED`) are internal to scripts that never mutate them
  and that no consumer imports. A `frozendict` would guard against a mutation nobody makes.
- **Function parameters** already take `Mapping[...]` where they only read (`from_blade_dict`,
  `set_blade_symbols`, `blade_latex`), which accepts a `frozendict` as it is.

### The measurements

Harness: `tasks/adhoc/frozendict-research-and-fit/run_all.sh` drives `bench_gn.py` (best of 5 per
operation), the code generator (best of 3), and the host `pytest -m "not slow"` (best of 3) for each
variant. It applies the variant's patch to `src/gacalc/gn.py` and restores `HEAD` on exit. The raw
numbers are in `data/results.csv`, and each variant's pytest summary is in `data/pytest-*.log`.
Host: the sandbox's Python 3.15.0 and sympy 1.14.0, run 2026-11-09 with nothing else running.

- **baseline:** `HEAD`, a `dict` stored and copied by `to_blade_dict()`.
- **A** (`variant-a-frozen-storage.patch`): store a `frozendict`, keep the copy.
- **B** (`variant-b-frozen-storage-no-copy.patch`): store a `frozendict`, return it with no copy.
  This is what adoption would ship.

| Measure | Baseline | A | B |
|---|---|---|---|
| `to_blade_dict()`, 8 blades | 0.13 µs | 0.09 µs | **0.03 µs** |
| `from_blade_dict`, numeric, 8 blades | 10.7 µs | 11.4 µs | 11.1 µs |
| add, numeric 3D | 15.2 µs | 15.2 µs | 14.9 µs |
| geometric product, numeric 3D | 1.26 ms | 1.23 ms | 1.22 ms |
| geometric product, symbolic 3D | 2.31 s | 2.24 s | 2.27 s |
| code generator, g1–g3 | 37.4 s | 37.7 s | 38.1 s |
| generator output vs baseline | — | byte-identical | byte-identical |
| `pytest -m "not slow"` | 70.7 s, 775 pass | 70.3 s, 775 pass | 69.6 s, 774 pass, 1 fail |

**Reading it:**
- Only `to_blade_dict()` moves past noise. It is 4× faster under B, because returning the stored
  mapping skips the copy.
- Every other difference is within run-to-run noise: about 3% on the symbolic product, 2% on the
  generator, 1–2% on pytest, and the numeric operations move both ways.
- The container cost is lost next to `sympy.simplify`. One symbolic 3D product takes 2.3 s; the
  dict work is in microseconds.
- B's one failure is the expected one: `test_to_blade_dict_is_a_copy` writes into the result and
  now gets `TypeError: 'frozendict' object does not support item assignment`. That is the
  protection working; the adoption rewrites the test to check exactly this.

## Phase 3: the `Frame` task, re-analyzed

`tasks/archive/2026/11/09/frame-derived-orthogonal-set-and-tuple-field.md` is unchanged in substance:
- `frozendict` has no sequence counterpart, so the tuple field stays the idiomatic immutable
  sequence;
- `Frame` stays unhashable: its elements are multivectors, and `Gn` won't gain a `__hash__` even
  with frozen storage (phase 2).

The one link: once `Gn` stores a `frozendict`, a `Frame` of `Gn` vectors holds values whose
contents can't be changed, which strengthens "frozen" on its side. A note recording this was added
to that task's Context.

## What was done

- The phase 1 sources and runtime checks above.
- The phase 2 survey (`discover.sh` and `data/`), the scratch-worktree typing trials, and the
  measurement harness, patches and results under `tasks/adhoc/frozendict-research-and-fit/`.
- Scaffolded `tasks/archive/2026/11/09/gn-frozendict-coefficient-storage.md` (the adoption, `proposed — needs
  go-ahead`).
- Added an "Immutable storage" section to `tasks/reference/blade-dict-interchange.md` with the
  durable findings.
- No source change: `src/gacalc/gn.py` is back at `HEAD` (the driver's `trap` restores it, checked
  with `git status`).
- **`tasks/adhoc/frozendict-research-and-fit/` was kept at this archive** so the maintainer could
  review the performance metrics, and removed with `git rm` when the adoption task
  (`tasks/archive/2026/11/09/gn-frozendict-coefficient-storage.md`) was archived, 2026-11-09. The
  numbers are in the table above. Recover the harness, patches and raw `data/results.csv` from git
  history: `git log --diff-filter=D --name-only -- tasks/adhoc/frozendict-research-and-fit`.
