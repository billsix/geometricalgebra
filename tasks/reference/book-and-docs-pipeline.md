# The gacalc Sphinx book — build pipeline & decisions

**What this is:** how gacalc's Sphinx book ("Plotting On Crappy Graph Paper") is
built, and the decisions/gotchas behind it. Stood up 2026-08-02 as an empty-but-
building skeleton (work record: `tasks/archive/2026/08/02/sphinx-book-pipeline.md`).
Modelled on `github.com/billsix/modelviewprojection`'s book, minus the parts gacalc
doesn't need.

## What exists

- **`book/docs/`** — the Sphinx source: `conf.py`, `index.rst`, `api.rst`,
  `_static/custom.css`, and the stock quickstart `Makefile`. The **outline skeleton is
  scaffolded** (2026-08-03): one `.rst` prose page per section + `api.rst` (autodoc over
  `gacalc.base`/`functions`/`transforms`), and **percent-format notebook stubs** under
  `book/docs/notebooks/*.py`. Structure and the prose-vs-notebook split live in
  `book-outline.md`; content fills in later.
- Builds to **HTML and PDF** (no EPUB).

## How it builds

- **`make docs`** (Makefile) → runs the container → **`entrypoint/docs.sh`**, which:
  generates the gitignored `g*.py` and editable-installs gacalc (so autodoc can
  `import gacalc`); **converts the book's percent notebooks
  `book/docs/notebooks/*.py` → `.ipynb` via jupytext** (so myst_nb executes them);
  then `make html` + `make latexpdf` in `book/docs/`, then copies the result to the
  bind-mounted **`output/gacalc/`** (+ `.nojekyll`).
- **Book notebooks:** the percent-format `.py` are the tracked source; the `.ipynb` are
  build artifacts (gitignored, regenerated each build). A notebook is a sub-page of its
  prose page (`.. toctree:: notebooks/<name>`); label a heading with MyST `(label)=` to
  `:ref:` a subsection from elsewhere (auto heading-anchors are off by design).
- **`BUILD_DOCS`** gates the toolchain: Dockerfile `ARG BUILD_DOCS=0` (bare build stays
  lean), Makefile `BUILD_DOCS ?= 1` (so `make image` builds it in). The gated
  Dockerfile block installs the Sphinx + LaTeX packages (list below).
- **`make clean`** removes `output/*` and `book/docs/_build`.

## Executable notebooks: the Sphinx-in-venv requirement (hard-won, 2026-08-03)

The book's notebooks `import gacalc`, and myst_nb runs them in a Jupyter kernel. For
that kernel to import gacalc, **three things must line up** — each was a real failure
while standing this up, and the symptom is silent (myst_nb does NOT fail the build on a
cell error, so `make docs` exits 0 with empty notebook pages and `ModuleNotFoundError`
only in `_build/html/reports/notebooks/*.err.log`):

1. **Sphinx lives in the VENV, not system — this is the load-bearing one.** myst_nb
   launches its kernel from **Sphinx's own `sys.prefix`**. So `sphinx-build` must run as
   `/venv/bin/python` (`sys.prefix=/venv`) → myst_nb picks the venv `python3` kernel,
   which has the editable-installed gacalc. If Sphinx is a **system (dnf)** package,
   `sphinx-build` runs as `/usr/bin/python3` → the *system* `python3` kernel → gacalc
   not importable → every notebook fails. The Dockerfile therefore installs
   **sphinx/furo/nbsphinx/myst-nb into the venv** (`uv pip install --python
   /venv/bin/python`), NOT via dnf. (This is exactly how modelviewprojection does it;
   gacalc originally used dnf sphinx and every notebook silently failed.)
2. **The notebook sources declare the kernel.** Each `book/docs/notebooks/*.py` carries
   a jupytext header (`kernelspec: name: python3`) so the converted `.ipynb` requests
   `python3`, matching mvp. Belt-and-suspenders with (1).
3. **`docs.sh` generates `g*.py` and editable-installs gacalc into the venv** before the
   build, so the kernel resolves gacalc to `/gacalc/src` with the generated modules
   present.

**Debugging aids** (these cost hours): add `import sys; print(sys.executable)` as a
notebook cell and build — `/venv/bin/python` = correct, `/usr/bin/python3` = the
system-sphinx bug. **`jupyter execute` resolves kernels DIFFERENTLY from myst_nb** —
always test with a real minimal `sphinx-build`, never `jupyter execute`. Check
`which sphinx-build` in the image: `/venv/bin/...` = good, `/usr/bin/...` = the bug.

## SVG figures in the PDF need ImageMagick

`sphinx.ext.imgconverter` shells out to **`convert` (ImageMagick)** to turn the rotation
`.svg` figures into PDF for the LaTeX build. **ImageMagick must be dnf-installed** in the
BUILD_DOCS block — it used to arrive transitively with the system `python3-sphinx`, so
when Sphinx moved to the venv (above), ImageMagick had to be requested explicitly, or
the PDF build dies with `LaTeX Error: Unknown graphics extension: .svg`. Note: a
`imgconverter_converters` setting in `conf.py` is **not** respected — the default
`convert` is what runs, so the fix is the package, not config.

## conf.py essentials

- Theme **furo**; `html_css_files = ["custom.css"]`.
- Extensions: `autodoc`, `napoleon`, `viewcode`, `mathjax`, `imgconverter`,
  `nbsphinx`, `myst_nb`.
- **`latex_engine = "lualatex"`** + `latex_use_xindy = False`; a small
  `latex_elements["preamble"]` for figure placement/width.
- `autodoc_default_options` (members, bysource, the `__init__`/`__call__`/operator
  special-members), `mathjax3_config` (`$…$`/`$$…$$` delimiters).

## Decisions & rationale

- **No EPUB, no `inlinetex`/`texExpToPng`.** Standard Sphinx math is enough:
  `sphinx.ext.mathjax` renders math in HTML, native LaTeX renders it in the PDF. mvp
  only added `inlinetex` to fix *EPUB* math (its commit `e682de30`, "inline latex in
  sphinx, for embedding in epub"); with no EPUB there is no reason for it.
- **lualatex is REQUIRED for the PDF, and this is why:** autodoc pulls gacalc's
  docstrings into the LaTeX build, and those docstrings are full of Unicode math
  (`√ ∧ · e₁ ² ⁻¹ Ã ≙`). **pdflatex aborts on those characters; lualatex typesets
  them.** Verified: the PDF built under lualatex with every such character rendered.
  This is about literal Unicode in docstrings, *not* math rendering.
- **`nbsphinx` + `myst_nb` both enabled**, mirroring mvp. Known footgun (from mvp's
  notes): both register `.ipynb` and `myst_nb` wins the handler; no issue hit here,
  kept as-is.
- **Stock quickstart `book/docs/Makefile`, NOT mvp's.** mvp's book Makefile has an
  `aspell` catch-all (`%: Makefile spellcheck`) that runs interactively and **hangs
  any TTY-less build** — deliberately not copied. Add spellcheck later if wanted.
- **Autodoc from the start** (an `api.rst`) so the empty book carries real context.

## Gotchas (verified while standing it up)

- **`lualatex` is provided by `texlive-luahbtex`, NOT `texlive-luatex`.** Wrong name =
  broken image build. (mvp uses the same package.)
- **Sphinx's generated LaTeX needs a support set** beyond base texlive:
  `fncychap`, `wrapfig`, `capt-of`, `needspace`, `tabulary`, `framed`, `titlesec`,
  `varwidth`, `fancyhdr`, `multirow`, `threeparttable`, `eqparbox` — install them
  explicitly (the recommended collections alone don't cover `wrapfig`/`capt-of`/…).

## Package set (Dockerfile `BUILD_DOCS` block)

`python3-sphinx`, `python3-furo`, `python3-nbsphinx`, `myst-nb`, `latexmk`,
`texlive-luahbtex`, `texlive-luatex85`, `texlive-lualatex-math`, `texlive-fontspec`,
`texlive-gnu-freefont`, plus the support set above. (gacalc already installs the
`collection-latexrecommended`/`-fontsrecommended` collections unconditionally for
nbconvert.) The same set was added to `runClaudeInContainer` so the sandbox can build
the book directly.

## Open follow-ups (gacalc docstring polish, surfaced by autodoc — not pipeline bugs)

1. **`|A|` in docstrings** reads as RST's `|substitution|` syntax → 12 "undefined
   substitution" warnings on `magnitude`/`inverse`/`cosine`/`normalize`/
   `rotor_from_vectors`. Fix by escaping (`\|A\|`) or using math/code roles.
2. **`ₙ` (U+2099) is missing from GNU FreeSerif** → that one glyph drops from the PDF.
   Fix via a font with U+2099 coverage, or avoid `ₙ` in docstrings. All other Unicode
   renders.
