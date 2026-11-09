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

## Context

**Versions in play** (re-check; these are snapshots):
- The sandbox and the image run **Python 3.15.0** (`python3 --version`, 2026-11-09).
- `pyproject.toml` says `requires-python = ">=3.13"`. gacalc is published on PyPI, so a 3.15-only
  built-in in the library either needs `requires-python` raised to `>=3.15` (a consumer-visible,
  breaking change, which needs a `CHANGELOG.md` BREAKING entry) or a fallback for 3.13 and 3.14
  (`types.MappingProxyType`, or a small read-only `Mapping` subclass). Weigh this in phase 2.

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
- [ ] For each candidate, judge what it fixes (a bug class, an invariant), what it costs (a copy per
  operation, a `requires-python` bump, API churn for consumers who build `BladeReal` dicts), and the
  alternative available today (`Mapping` in signatures, `MappingProxyType`, `Final`).
- [ ] If anything is worth adopting, scaffold it as its own `proposed — needs go-ahead` task.

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

None yet. Phase 1's answer decides whether phase 2 is about adopting now, or about a fallback until
`requires-python` can rise.
