# `frozendict`: is it released, can gacalc use it, and would it improve the code?

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** conversation, 2026-11-09 (William Emerison Six <billsix@gmail.com>: "regarding
frozendict, research online to see if it's out, and if it's in the version of python we use. And
then, analyze the whole codebase here and see if using it, let's say for bladereal, or gn, or
anything, would make our codebase better. after that's done, then reanalyze the other task we just
made.")

## BLUF

A built-in `frozendict` (PEP 814) may be coming in Python 3.15. This task has three phases, each
reporting before the next starts:

1. Find out from primary sources whether `frozendict` is released, and in which version.
2. Survey gacalc's dict use (`BladeReal`, `Gn.coefficient_of_blade`, the blade-dict interchange, the
   generator's tables) and say where an immutable mapping would make the code better, and where it
   would not.
3. Re-analyze `tasks/frame-derived-orthogonal-set-and-tuple-field.md` in that light.

Done means a recommendation is written into this doc for each phase, a reference-doc entry holds
the durable findings, and any adoption is scaffolded as its own `proposed` task. This task changes
no code.

## Decisions

1. **If gacalc adopts `frozendict`, raise `requires-python` to `>=3.15`.** There is no fallback
   for 3.13/3.14 (William Emerison Six <billsix@gmail.com>, 2026-11-09: "update the task to upgrade
   pyproject.toml for python 3.15.0, if we decide to implement frozendict in our codebase").
   Dropping 3.13 and 3.14 is a breaking change for consumers, so the adoption task carries a
   `CHANGELOG.md` `[Unreleased]` BREAKING entry for it, and checks the CI workflows and
   `entrypoint/` for anything that assumes an older Python.
2. **Making `Gn`'s storage immutable is the wanted outcome** (the same, 2026-11-09: "regarding the
   concrete use, that sounds like a win!"). Phase 2 still measures its cost, but it starts from
   "adopt unless the cost is prohibitive", not from a neutral survey.

## Context

**Versions in play** (re-check; these are snapshots):
- The sandbox and the image run **Python 3.15.0** (`python3 --version`, 2026-11-09).
- `pyproject.toml` says `requires-python = ">=3.13"`. gacalc is published on PyPI. Decision 1
  settles the floor: adopting `frozendict` raises it to `>=3.15`, with no fallback.

**What was said in conversation (unverified; phase 1 checks it):** PEP 814 ("Add frozendict built-in
type") was believed accepted for 3.15, but this was not checked against a source. Only a dict
version is proposed; there is no frozen list. PEP 712 (dataclass field converters) was rejected.

**Where an immutable mapping might help** (pointers for phase 2, not conclusions):
- `src/gacalc/base.py`: `Blade = tuple[int, ...]` and `BladeReal = dict[Blade, Real]`. This alias is
  the interchange type (`to_blade_dict`/`from_blade_dict`). `from_blade_dict` already accepts a
  `Mapping[Blade, Real]`. See `tasks/reference/blade-dict-interchange.md` for its contract
  (canonical keys, zero omission, the eager/lazy split).
- `src/gacalc/gn.py`: `Gn.coefficient_of_blade: BladeReal` is the mutable storage of the general
  multivector. Earlier today (`CHANGELOG.md` `[Unreleased]` › Fixed, "`Gn.to_blade_dict()` returns
  a copy") a shared-state bug was fixed: `to_blade_dict` handed out its internal dict, and a caller
  editing it corrupted the shared `e_1` constant. The fix copies on every call. An immutable storage
  type would rule that bug class out instead, and could make the copy unnecessary. Weigh that
  against the cost of building one per operation.
- **Hashability:** multivectors are unhashable today (they define `__eq__` without `__hash__`; see
  `tasks/frame-derived-orthogonal-set-and-tuple-field.md`). A `frozendict` of hashable values is
  hashable, but sympy expressions are hashable and floats compare inexactly, so whether
  multivectors *should* hash is a design question for phase 2, not a free side effect.
- `tools/gen_specialized.py` and `tools/astbuild.py`: module-level lookup tables that are never
  mutated after they are built (candidates for a frozen mapping, or for `Final`).
- The generated `g*.py` classes store fields, not dicts, so they are likely unaffected. Confirm,
  and change the generator, never the output.

## Plan

### Phase 1: is it released?

- [ ] Read the primary sources: PEP 814 on peps.python.org (its Status and Python-Version headers),
  the "What's New in Python 3.15" page on docs.python.org, and the CPython changelog for the 3.15.0
  release. Record what each says, with its URL and the date checked.
- [ ] Confirm in the image: `podman run … python -c "print(frozendict)"` (use the gate's
  `podman run` line, not a `: image` target), and the same in the sandbox.
- [ ] Record: released or not, the version, its semantics (hashability, `|` merge, the constructor,
  whether it subclasses `dict`), and what `ty` and the stubs make of it.

### Phase 2: would it improve gacalc?

- [ ] Survey with `git grep` (not by reading every file): `dict[` annotations, `BladeReal` uses,
  `coefficient_of_blade` reads and writes, and module-level dict constants in `src/` and `tools/`.
  Save the discovery command and its output under
  `tasks/adhoc/frozendict-research-and-fit/` (the bulk-op convention).
- [ ] **`Gn.coefficient_of_blade` first** (decision 2). Make it a `frozendict[Blade, Real]`, then
  check three things:
  - every write site in `gn.py` builds a new mapping instead of mutating one;
  - `to_blade_dict()` can return the stored mapping with no copy, and its return type and
    `BladeReal`'s meaning are settled: does `BladeReal` become the frozen type, or stay `dict` for
    what callers build?
  - the cost: time `make test` and the 3D symbolic frame tests before and after, since `Gn`
    builds a new dict per operation.
- [ ] For each other candidate, judge what it fixes (a bug class, an invariant), what it costs (a
  copy per operation, API churn for consumers who build `BladeReal` dicts), and the alternative
  available today (`Mapping` in signatures, `MappingProxyType`, `Final`).
- [ ] Scaffold the adoption as its own `proposed — needs go-ahead` task (or one per independent
  part). Its plan includes the `requires-python = ">=3.15"` bump in `pyproject.toml`, the
  `CHANGELOG.md` BREAKING entry for dropping 3.13 and 3.14, and a check of `.github/workflows/`
  and `entrypoint/` for older Python versions (decision 1). It also includes removing the copy in
  `Gn.to_blade_dict()`, keeping `test_to_blade_dict_is_a_copy`'s guarantee: a caller still cannot
  corrupt `e_1` (the test then checks that the mapping is immutable).

### Phase 3: re-analyze the `Frame` task

- [ ] Re-read `tasks/frame-derived-orthogonal-set-and-tuple-field.md` against phases 1–2. Did
  anything change about the tuple field, hashability, or how `Frame` stores derived data? Write the
  conclusion into that task, and update its plan if it changes.

### Close-out

- [ ] Write the durable findings (what `frozendict` is, which version has it, and where gacalc does
  and does not want it) into a reference doc, most likely `tasks/reference/blade-dict-interchange.md`
  or a new `tasks/reference/immutable-containers.md`.
- [ ] Rewrite this task into a done-record and archive it.

## Open questions

None. If phase 1 finds `frozendict` is not in 3.15.0, stop after phase 1 and report; the
decisions above assume it is.
