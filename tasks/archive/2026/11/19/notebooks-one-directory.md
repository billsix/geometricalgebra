# One notebook directory that students open, and the book draws from

**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>), the implementation plan from
`tasks/archive/2026/11/19/unify-demo-and-book-notebooks.md`.
**Done:** 2026-11-19, branch `notebooks-one-directory`.

Every notebook (the book's 32 companions and the 11 explorations) now lives in `notebooks/`, the
directory `make jupyter` opens. The book renders all of them, the explorations as a new Part IV,
and no notebook edits `sys.path`. The state and the reasons are in
`tasks/reference/demo-and-book-notebooks.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-19)

1. All 11 demo notebooks are in the book, as Part IV — Explorations. A notebook can leave the book
   through `conf.py`'s `exclude_patterns`.
2. Every notebook carries the LGPL-2.1-only header in a code cell tagged `remove-cell`.
3. `make jupyter` lands in `notebooks/`, with the rest of the repository browsable.
4. The generic ePiX helpers are the `gacalc.epixscene` subpackage, shipped in the wheel.
5. (During the work) pyright excludes the 31 notebooks that draw live ePiX figures, because ePiX
   ships no type information. Fixing that was split off: epix-mirror's
   `tasks/archive/2026/11/19/ship-python-type-information.md` (staged there, not committed), and
   `tasks/epix-type-stubs-for-pyright.md` here, blocked on it being pushed. Once it is, the
   excludes go (the maintainer agreed, 2026-11-19).

## What was done, by commit

- `71ffa20`: the seven generic helpers moved from `book/figures/epix/_*.py` to
  `src/gacalc/epixscene/`, and the 31 `sys.path` cells were removed. Added an import-boundary
  test, a root `conftest.py` that skips the package where `epix` is missing, and ty's
  `allowed-unresolved-imports = ["epix", "epix.**"]`. The `contextmanager` returns became
  `Generator`, the docstrings were rewrapped to 88 columns, and each module keeps its CC0
  dedication (not relicensed).
- `44741a7`: the 32 companions moved to `notebooks/`. `docs.sh` writes their `.ipynb` to
  `book/docs/notebooks/`, so the toctree entries are unchanged. Every header asks for `python3`.
  The tools, gates, config and docs were repointed. `line_scene`'s `Color` alias became a `type`
  statement (the one new `check_annotations` row).
- `36f3db5`: Part IV in `index.rst`, a front-page "Running the notebooks yourself" section, and
  the license cells. The explorations' titles write `$\mathcal{G}_n$`, and XITS Math became the
  second LaTeX fallback font. Only FreeSerif's upright face has 𝒢, so the bold headings and
  italic code comments had been losing it: 6 missing glyphs before this branch, 36 with Part IV
  added, 0 after.
- `3061801`: `jupyter.sh` lands in `notebooks/` (`--LabApp.default_url`; the `ServerApp` setting
  is overridden by `jupyter lab`'s own) with `python3` as the default kernel, and the `gacalc`
  kernelspec is gone. Added `notebooks/README.md` (each notebook with its page) and a README
  "Notebooks" section. The teaching-style guide now states the two kinds by role; `CLAUDE.md` and
  the pipeline doc describe the one directory.

## Verification

- Every prebuilt figure's eepic was the same before and after the helper move (49 figures,
  `tasks/adhoc/notebooks-one-directory/dump_eepic.py`). Two renders of unchanged code had shown
  that the rendered PDF and PNG bytes differ from run to run, so files could not be compared.
- The 32 companions were executed before the move and again from `notebooks/`. Their outputs
  matched (`compare_outputs.py`, with memory addresses normalised and PNGs compared by decoded
  pixels). All 43 notebooks executed.
- `make format` exited 0, `pyright notebooks/` reported 0 errors, `make test` passed
  (1393 passed, 3 skipped), and `check_annotations.py` gave 63 findings, the same as master. With
  `epix` blocked, pytest collected `src` with no errors.
- `make docs` exited 0 with no warning that was not already in the baseline build. No rendered
  notebook page shows the license text.
- A headless `jupyter.sh` redirected `/` to `/lab/tree/notebooks`, listed 44 entries there, and
  offered only the `python3` kernel.

## Ad-hoc scripts

All in `tasks/adhoc/notebooks-one-directory/`, one-shot, removed in the archive commit:
`discover.sh` and `data/helper-references.txt` (the helper references found), `move_helpers.py`,
`repoint_notebook_paths.py`, `add_license_cells.py` (the codemods, each run twice to prove
idempotence), and `dump_eepic.py` and `compare_outputs.py` (the verification harnesses).
