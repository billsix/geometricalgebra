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
- [ ] **Final step: inline `BladeReal` (decision 2).** Delete `BladeReal = Mapping[Blade, Real]` from
  `src/gacalc/base.py` and write `Mapping[Blade, Real]` at every use. Scope, measured 2026-11-09
  (`git grep -c BladeReal`, outside the generated `g*.py`):
  - `src/` 27 (`base.py` 17, `gn.py` 4, `transforms.py` 3, `nbplotutils.py` 3);
  - `tools/gen_specialized.py` 18 and `tools/derive_lean_algebra.py` 2;
  - `tests/` 16 (`test_blade_dict.py` 11, `test_multivector.py` 3, `test_conformance.py` 2);
  - docs: `CLAUDE.md`, `README.md`, and `tasks/reference/` (`blade-dict-interchange.md` 7, plus one
    each in `type-annotation-exemptions.md` and `scalar-vs-real-naming.md`).

  How:
  - **The generator:** it emits `BladeReal` 26 times per generated module (`g2.py`), in
    annotations (`name_ref("BladeReal")`), `Returns:` docstring text (`"BladeReal: the grade-2 blade
    -> coefficient mapping."`) and its `from gacalc.base import … BladeReal …`. Change it to emit
    the subscript `Mapping[Blade, Real]` and import `Mapping` from `collections.abc` (and `Blade`
    from `gacalc.base`) in the generated header. Never edit `g*.py`; regenerate. Confirm that the
    only change in g1–g3 is the alias spelled out, using a diff against the pre-change output (the
    pinned "same output" bar is equivalence, so record what changed).
  - **The alias's documentation:** base.py's `#:` comment above the alias is the authoritative
    interchange contract (canonical keys, zero omission, graded silent-drop, read-only). Move it to
    the abstract `MultiVectorBase.to_blade_dict`/`from_blade_dict` docstrings (or the module
    docstring), so the contract survives the alias, and repoint
    `tasks/reference/blade-dict-interchange.md`'s "Where it lives" and "Sources", which cite the
    `BladeReal` docstring.
  - **Docstrings:** `Returns:` sections that name `BladeReal` say `Mapping[Blade, Real]`; prose that
    calls the format "the `BladeReal` interchange" says "the blade-dict interchange".
  - **Imports:** each file that drops `BladeReal` imports `Mapping` (`collections.abc`) and `Blade`
    and `Real` where it doesn't already. ruff's `F401` catches leftovers.
  - **Consumers:** `BladeReal` is importable from `gacalc.base`, so removing it is breaking. Add a
    `CHANGELOG.md` `[Unreleased]` BREAKING entry ("`BladeReal` removed; write `Mapping[Blade,
    Real]`"), and fold it into this task's other BREAKING entry if that reads better. mvp has no
    `BladeReal` (re-check with `git grep`).
  - Gates again: `make test`, `make format`, `make check-notebooks`, `make check-generated`,
    `make docs`.

## Decisions

1. Go ahead, as part of a committed batch with `tasks/frame-derived-orthogonal-set-and-tuple-field.md`
   (William Emerison Six <billsix@gmail.com>, 2026-11-09: "make a branch do the
   gn-frozendict-coefficient-storage task, commit it, archive it"). The research task made the two
   design decisions (raise `requires-python` to 3.15 with no fallback; immutable `Gn` storage).
2. **As the final step, remove the `BladeReal` alias and write `Mapping[Blade, Real]` everywhere it
   was used** (William Emerison Six <billsix@gmail.com>, 2026-11-09: "as a final step, remove the
   'BladeReal = Mapping[Blade, Real]', and just inline 'Mapping[Blade, Real]' everywhere 'BladeReal'
   is used"). See the plan's last step.

## Open questions

None.
