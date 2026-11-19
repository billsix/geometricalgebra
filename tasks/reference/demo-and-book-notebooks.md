# The demo notebooks and the book notebooks: how they differ, and why

gacalc has two directories of jupytext percent-format notebooks. The **demo notebooks** in
`notebooks/` (11 files, `displaymv.py`, `displayg2.py`, …) explore the library. The **book
notebooks** in `book/docs/notebooks/` (32 files) are each the companion of one book page, rendered
into the book by myst-nb. The maintainer wants one directory that students open with `make jupyter`,
with the book able to include any of its notebooks (William Emerison Six <billsix@gmail.com>,
2026-11-19). The plan to get there is `tasks/notebooks-one-directory.md`. This doc records the state
it starts from, measured 2026-11-19.

## The differences

| | Demo `notebooks/` | Book `book/docs/notebooks/` | Essential or history? |
| --- | --- | --- | --- |
| Started | 2025-12-01, with the first Jupyter image | 2026-08-02, with the book scaffolding (myst-nb set up the way modelviewprojection has it) | history: the book came eight months later and got its own directory beside its `.rst` pages |
| Role | an exploration of one part of the library | the companion of one page, named after it | essential, but it is a property of the notebook, not the directory |
| Values | numbers before symbols | symbolic throughout; numbers only in one plot-values cell and the figures | essential to the role (`tasks/reference/book-notebook-teaching-style.md` rule 6) |
| Figures | matplotlib via `gacalc.nbplotutils` | live ePiX via the helpers in `book/figures/epix/` | partly essential: ePiX gives the print-quality figures the PDF needs, and matplotlib needs no extra install |
| Classes | the full `G` classes, with bare-name aliases (the `CLAUDE.md` carve-out) | the graded `g2`/`g3` types | role: the demos show the full class |
| Kernel in the header | `gacalc` (registered by `entrypoint/jupyter.sh`) | `python3` | history. Both are `/venv`'s Python. `entrypoint/docs.sh` registers no `gacalc` kernel, so the book needs `python3` |
| License header | the LGPL-2.1-only cell | **none** in any of the 32, contrary to `CLAUDE.md`'s "every `.py` file" rule | history: an omission |
| Type gate | pyright (`make check-notebooks`, the CI `notebooks` job) | `ty` (`entrypoint/format.sh`) | history: each gate was added for one directory |
| Lint | E501 exempt; prose width by `tools/check_notebook_prose_width.py` | the same, plus an E402 exemption for `frame-qr-*.py` (the `sys.path` line) | the E402 is a symptom of the import paths below |
| Executed | by nobody automatically | by myst-nb at `make docs`, which fails on an error | history |
| `.ipynb` | `make notebooks-ipynb` (`entrypoint/percentToIpynb.sh`), gitignored | `entrypoint/docs.sh`, gitignored | history |

Nothing in the table needs two directories. Every essential difference follows from a notebook's
role, which can be recorded per notebook.

All 11 demo notebooks execute headless under nbconvert: about 95 s in total, `displaytransforms.py`
the slowest at 31 s. None opens a window or reads a file, so myst-nb could execute them as book pages.

## Import paths

- **The demo notebooks** import only the installed `gacalc` (the image's editable install), so they
  run from any working directory.
- **31 of the 32 book notebooks** start with
  `sys.path.insert(0, str(pathlib.Path("../../figures/epix").resolve()))` and then import a helper
  module (`_bootstrap_live`, `_frame_scene`, `_line_scene`, `_paper_scene`, `_venn_scene`). The path
  resolves against the kernel's **working directory**, not the notebook file. It works only because
  JupyterLab and myst-nb both start the kernel in `book/docs/notebooks/`. It breaks if the notebook
  moves, if a kernel is started elsewhere, or if the file runs as a script. It also costs a
  `ty` `extra-paths` entry and the E402 exemption.
- **Package data is not the right mechanism.** `[tool.setuptools.package-data]` (used for the
  `gacalc.gl` shaders) ships non-Python files read with `importlib.resources`. These helpers are
  Python modules, and the standard way to import a module from any directory is to put it in an
  installed package.
- **The helpers split in two.** Seven are generic drawing tools that the notebooks use, directly or
  through each other: `_scene2d`, `_scene3d`, `_frame_scene`, `_bootstrap_live`, `_line_scene`,
  `_paper_scene` and `_venn_scene`. Six hold the constants of one prebuilt figure set and are imported
  only by the figure scripts beside them: `_addition_scene`, `_bootstrap_scene`, `_graphpaper_scene`,
  `_projection_scene`, `_rotate_ab_scene` and `_rotation_scene`. `tools/render_epix_figures.py` runs
  each figure script in a child interpreter whose working directory is the script's directory, so
  sibling imports work there without a path change.
- **ePiX is not a PyPI dependency.** The image builds it from github.com/billsix/epix-mirror and
  installs its Python package editable from `/opt/epix-src/python`. Any module importing `epix` can
  therefore run only in the image (or wherever ePiX was built), the same limit `gacalc.gl` has with
  its `gl` extra, except that `pip` cannot install ePiX at all.

## Facts the plan relies on

- Sphinx finds source files with `os.walk(..., followlinks=True)` (`sphinx.util.matching`), so a
  symlinked notebook directory would be read. The plan does not need a symlink, because
  `entrypoint/docs.sh` already generates every `.ipynb` the book reads.
- `make jupyter` starts JupyterLab rooted at the repository (`cd /gacalc` in
  `entrypoint/jupyter.sh`), and neither the README nor the book says where the notebooks are. The
  book's `interactive-calculator.rst` is still a placeholder.
- The image's `python3` kernelspec (`/venv/share/jupyter/kernels/python3`) runs `/venv`'s Python, the
  same interpreter as the `gacalc` kernel.
