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
