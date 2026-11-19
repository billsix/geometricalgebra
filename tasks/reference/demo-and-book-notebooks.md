# The notebooks: one directory, two kinds

Every gacalc notebook is a jupytext percent-format `.py` in `notebooks/`, the directory
`make jupyter` opens and `notebooks/README.md` indexes. The maintainer's aim (William Emerison Six
<billsix@gmail.com>, 2026-11-19): the book is for learning from, and a student also runs its
notebooks like a graphing calculator, so there is one place to find them. The book's 32 companion
notebooks and the 11 demo notebooks were two directories (`book/docs/notebooks/` and `notebooks/`)
until `tasks/archive/2026/11/19/notebooks-one-directory.md` merged them.

## Two kinds, by role

| | Companion ("book notebook") | Exploration ("demo notebook", `display*.py`) |
| --- | --- | --- |
| Role | goes with one book page, named after it | tours one part of the library |
| In the book | a sub-page of its page's toctree | a page of Part IV — Explorations (`index.rst`) |
| Values | symbolic throughout; numbers only in one plot-values cell and the figures | numbers before symbols |
| Figures | live ePiX, through `gacalc.epixscene` | matplotlib, through `gacalc.nbplotutils` |
| Classes | the graded `g2`/`g3` types | the full `G` classes, with bare-name aliases (the `CLAUDE.md` carve-out) |

The differences are the notebook's role, not its location: the teaching rules for each kind are in
`tasks/reference/book-notebook-teaching-style.md`. The two sets began apart because of history,
not design. The demo notebooks came with the first Jupyter image (2025-12-01). The book, set up
the way modelviewprojection has it, came on 2026-08-02 and put its notebooks beside its `.rst`
pages.

## What every notebook shares

- **Kernel:** each header asks for `python3`, the image's `/venv` Python
  (`/venv/share/jupyter/kernels/python3`), which imports the editable gacalc. `make jupyter`
  defaults to it.
- **License:** the LGPL-2.1-only header, in a code cell tagged `remove-cell` so myst-nb leaves it
  off the page.
- **Gates:** `ty check notebooks` in `make format`; `tools/check_notebook_prose_width.py` (E501 is
  exempt for `notebooks/*.py`); `tools/check_annotations.py`; `tools/check_epix_keywords.py` for
  the ePiX calls. pyright (`make check-notebooks`) checks all but the 31 notebooks that draw live
  ePiX figures (below).
- **In the book:** `entrypoint/docs.sh` converts every `notebooks/*.py` into
  `book/docs/notebooks/<name>.ipynb`, which is build output (gitignored), and myst-nb executes each
  one, failing the build on an error. A notebook the book should leave out goes in `conf.py`'s
  `exclude_patterns`. All 11 explorations run headless in about 95 s (measured 2026-11-19;
  `displaytransforms.py` is the slowest at 31 s). None opens a window or reads a file.

## Imports: installed packages only

A notebook imports nothing by path, so it runs from any working directory: the kernel JupyterLab
starts in `notebooks/` and the one myst-nb starts in `book/docs/notebooks/` both work.

- **The ePiX scene helpers are the `gacalc.epixscene` package**, not files found through
  `sys.path`. The book notebooks used to push `../../figures/epix` onto `sys.path`. That path
  resolved against the kernel's working directory, not the file, so it worked only where both
  tools happened to start the kernel. **Package data would not have been the fix:**
  `[tool.setuptools.package-data]` (the `gacalc.gl` shaders) ships non-Python files read with
  `importlib.resources`. Importable code belongs in a package.
- **The split.** The seven generic helpers are in the package: `scene2d`, `scene3d`,
  `frame_scene`, `bootstrap_live`, `line_scene`, `paper_scene` and `venn_scene`. The six that hold
  one prebuilt figure set's constants stay beside their figures in `book/figures/epix/`,
  `_`-prefixed: `_addition_scene`, `_bootstrap_scene`, `_graphpaper_scene`, `_projection_scene`,
  `_rotate_ab_scene` and `_rotation_scene`. `tools/render_epix_figures.py` runs each figure from
  that directory, so they import as siblings.
- **ePiX is not a PyPI dependency.** The image builds it from github.com/billsix/epix-mirror and
  installs its Python package editable from `/opt/epix-src/python`. So `gacalc.epixscene` imports
  only where ePiX is installed. `import gacalc` never loads it
  (`tests/test_epixscene_import_boundary.py`), and the root `conftest.py` skips its doctest
  collection where `epix` is missing (the lean CI image).

## ePiX and the type checkers

ePiX ships no `.pyi` stub and no `py.typed`. Its editable install is a setuptools import hook
(`__editable___epix_*_finder.py`), which static checkers cannot follow even in the full image. So:

- ty is told `epix` and its submodules may be unresolved (`pyproject.toml`,
  `[tool.ty.analysis] allowed-unresolved-imports`). The ePiX-derived names are then Unknown and
  raise no errors.
- pyright reports every name imported from a module it cannot resolve, re-exports included
  ("is unknown import symbol", 91 errors over the live-figure notebooks), so
  `pyrightconfig.json` excludes those 31 notebooks.

Lifting both is `tasks/epix-type-stubs-for-pyright.md`, blocked on epix-mirror's
`tasks/ship-python-type-information.md`.
