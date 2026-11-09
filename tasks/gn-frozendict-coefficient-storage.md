# Store `Gn`'s coefficients in a `frozendict`, and raise `requires-python` to 3.15

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** `tasks/archive/2026/11/09/frozendict-research-and-fit.md` (the research and
measurements; the harness and raw numbers are in `tasks/adhoc/frozendict-research-and-fit/`)

## BLUF

Make `Gn.coefficient_of_blade` an immutable `frozendict` (a built-in since Python 3.15, PEP 814),
so the shared-state bug class fixed on 2026-11-09 (a caller editing a `to_blade_dict()` result and
corrupting `e_1`) becomes impossible, and `to_blade_dict()` returns the stored mapping with no copy.
`BladeReal` becomes the read-only `Mapping[Blade, Real]`, and `requires-python` rises to `>=3.15`.
Measured, there is no performance cost (the research task's table). Done means the change is in,
`test_to_blade_dict_is_a_copy` checks the mapping is immutable, the CHANGELOG has the BREAKING
entries, and `make test`, `make format`, `make check-notebooks`, `make check-generated` and
`make docs` pass.

## Context

Read first: the research task's "Phase 2" (the typing design and why it was chosen) and its
measurements table; `tasks/reference/blade-dict-interchange.md` › "Immutable storage".

**The change, as prototyped and measured** (the research task's variant B):
- `src/gacalc/gn.py`:
  - `__post_init__` stores `frozendict({...})`, wrapping the zero-pruning comprehension:

    ```python
            # prune zero coefficient_of_blade
            self.coefficient_of_blade = frozendict(
                {
                    blade: self.coefficient_of_blade[blade]
                    for blade in self.coefficient_of_blade.keys()
                    if self.coefficient_of_blade[blade] != 0
                }
            )
    ```

  - `to_blade_dict()` returns `self.coefficient_of_blade`, and its docstring says it is the
    stored, immutable mapping;
  - the field stays typed `BladeReal`, so `Gn({...})` with a dict still type-checks.
- `src/gacalc/base.py`: `BladeReal = Mapping[Blade, Real]`, with its docstring (the authoritative
  contract) updated to say the mapping is read-only.
- `src/gacalc/nbplotutils.py` › `_expand_numerators_dict`: declare `out: dict[Blade, Real] = {}`
  (it writes into the dict it builds).
- `tests/test_multivector.py` › `test_to_blade_dict_is_a_copy`: becomes a test that writing into
  the result raises `TypeError` and that `e_1` is unchanged, renamed to match
  (e.g. `test_to_blade_dict_is_immutable`).
- `pyproject.toml`: `requires-python = ">=3.15"`. Then check:
  - the `ruff` `target-version` and any `ty` Python-version setting in `pyproject.toml`;
  - `.github/workflows/*` for a pinned older Python;
  - `entrypoint/` and the README's install notes for a stated minimum version.

**What it breaks for consumers** (`CHANGELOG.md` `[Unreleased]`, both marked BREAKING):
- Python 3.13 and 3.14 are no longer supported (`requires-python >= 3.15`).
- `Gn.to_blade_dict()` returns an immutable `frozendict`. Code that wrote into the result gets
  `TypeError`; copy it first with `dict(...)`. `BladeReal` is now the read-only
  `Mapping[Blade, Real]`.

The specialized classes' generated `to_blade_dict()` still builds a fresh `dict`, which satisfies
the `Mapping` return type, so the generator needs no change. Confirm with `make check-generated`
and a byte comparison of g1–g3 before and after.

**Not in scope:** hashing. `Gn` must not gain a `__hash__`: its `__eq__` is value equality, so a
structural hash would break the hash contract. See the research task.

## Plan

- [ ] Make the `gn.py` change, then the `base.py`, `nbplotutils.py`, test and `pyproject.toml`
  edits above.
- [ ] Re-check for writes into a `to_blade_dict()` result outside the repo's own code. As of
  2026-11-09 there are none: mvp (github.com/billsix/modelviewprojection), the in-house consumer, has
  no `to_blade_dict` or `coefficient_of_blade` in its Python (`git grep`). The book notebooks run
  under `make docs`.
- [ ] `CHANGELOG.md` `[Unreleased]`: the two BREAKING entries. Update
  `tasks/reference/blade-dict-interchange.md` (drop "copy", say "immutable") and `CLAUDE.md` if it
  mentions the copy.
- [ ] Gates: `make test`, `make format`, `make check-notebooks`, `make check-generated`, `make docs`.

## Open questions

None. Both decisions were made in the research task (William Emerison Six <billsix@gmail.com>,
2026-11-09).
