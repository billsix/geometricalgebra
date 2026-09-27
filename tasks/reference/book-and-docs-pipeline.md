# The gacalc Sphinx book — build pipeline & decisions

**What this is:** how gacalc's Sphinx book ("Geometry 2") is
built, and the decisions/gotchas behind it. Stood up 2026-08-02 as an empty-but-
building skeleton (work record: `tasks/archive/2026/08/02/sphinx-book-pipeline.md`).
Modelled on `github.com/billsix/modelviewprojection`'s book, minus the parts gacalc
doesn't need.

## What exists

- **`book/docs/`** — the Sphinx source: `conf.py`, `index.rst`, `api.rst`,
  `_static/custom.css`, and the stock quickstart `Makefile`. The **outline skeleton is
  scaffolded** (2026-08-03): one `.rst` prose page per section + `api.rst` (autodoc over
  every package module — `gacalc.base`/`gn`/`functions`/`transforms`/`measure`/`vectorcalc`/
  `frame`; expanded from the original three 2026-09-26 so cross-refs resolve), and
  **percent-format notebook stubs** under
  `book/docs/notebooks/*.py`. Structure and the prose-vs-notebook split live in
  `book-outline.md`; content fills in later.
- Builds to **HTML and PDF** (no EPUB).
- **Licensing:** the book *prose* is **GFDL-1.3** (GNU Free Documentation License,
  Version 1.3 — matching mvp's book), declared in a header on each ported `.rst`
  (`rotate.rst`, `proof-rotate.rst`, `geometric-product.rst`, …). This is distinct from
  gacalc's **LGPL-2.1-only** *code*. Source: `tasks/archive/2026/08/03/port-rotation-explanation-from-mvp.md`.

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

## Notebook PDF export (nbconvert — separate from the Sphinx PDF)

Jupyter's "Save and Export As → PDF" (nbconvert) is a **different** pipeline from the Sphinx
book above, and its toolchain is installed **unconditionally** (not gated by `BUILD_DOCS`) by
`entrypoint/03-install-notebook-tex.sh`:

- **XeLaTeX**, chosen over the WebPDF route — WebPDF needs Chromium, which the image doesn't
  ship.
- **`texlive-soul`** (`soul.sty`) — nbconvert's default LaTeX template needs it, and it is
  **not** pulled in by the recommended TeX Live collections, so it must be requested
  explicitly (a non-obvious gotcha found empirically). Source:
  `tasks/archive/2026/06/28/notebook-pdf-export.md`.

## conf.py essentials

- Theme **furo**; `html_css_files = ["custom.css"]`.
- Extensions: `autodoc`, `napoleon`, `viewcode`, `mathjax`, `imgconverter`,
  `nbsphinx`, `myst_nb`.
- **`latex_engine = "lualatex"`** + `latex_use_xindy = False`; `latex_elements["preamble"]`
  for figure placement/width **and a luaotfload fallback to DejaVu Sans (referenced by file)
  for glyphs FreeSerif lacks — notably `ₙ` (U+2099)**.
- `autodoc_default_options` (members, bysource, the `__init__`/`__call__`/operator
  special-members), **`autodoc_typehints = "none"`** (annotations are NOT rendered as cross-refs
  — the types live in the Google `Args:`/`Returns:` prose — which keeps unresolved-reference
  warnings out of the PDF), `mathjax3_config` (`$…$`/`$$…$$` delimiters).

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

## Autodoc rendering warnings — RESOLVED 2026-09-26

The follow-ups that were open here are fixed (work record: the archived
`docstrings-for-sphinx` task; the cross-project recipe in the shared
`sphinx-book-conventions.md`):

1. **`|A|`-style RST warnings** — there were far fewer than the ~12 predicted (most `|A|` are
   already inside `` `` `` code-spans or `::` literal blocks, which RST doesn't parse). The
   genuinely-bare `|`/`` ` `` tokens (in `magnitude`/`magnitude_squared`/`inverse`/`cosine`/`exp`/
   `normalize`, one `versor_from_vectors` prose line, a stray `` ``Rational``s ``, and `measure.py`)
   were wrapped in the `` `` `` code-role. `make docs` → **0** substitution warnings.
2. **`ₙ` (U+2099) missing from FreeSerif** — a luaotfload fallback to DejaVu Sans (by file)
   supplies it, FreeSerif kept as main (it has 𝒢). **0** `Missing character`.
3. **Undefined hyperrefs 169 → 0** — `autodoc_typehints = "none"` + `api.rst` now `automodule`s
   every package module. (Earlier notes said "~7 residual"; a converged build measures **0**.)
4. **Full Google/napoleon docstrings across the hand-written AND generated API** (done 2026-09-26):
   every `MultiVectorBase` method, the `gn.py` methods, the public module-level functions, AND the
   ~185 grade-specialized generated docstrings (`CUSTOM_METHOD_DOCS` + the 7 `_*_doc` callables in
   `tools/gen_specialized.py`) now carry `Args:`/`Returns:`/`Raises:`/`Yields:` with any doctest
   under `Example:`. With `autodoc_typehints = "none"`, the `Returns:` prose IS the rendered type
   info. Only base/gn/functions/transforms/measure/vectorcalc/frame are autodoc-rendered (api.rst);
   g1/g2/g3 are read as source + run as `--doctest-modules`, not rendered.

**Gotcha — re-exported names need a qualified type in `Returns:`.** `ComposableFunction` and
`InvertibleFunction` are defined in `gacalc.functions` and **re-exported** by `gacalc.transforms`;
`api.rst` automodules both, so a *bare* `ComposableFunction`/`InvertibleFunction` type token in a
napoleon `Returns:` field resolves to two targets → `WARNING: more than one target found for
cross-reference` (Sphinx `[ref.python]`). Fix: write the **canonical** `gacalc.functions.<Name>` in
those `Returns:` tokens (in `base.py`'s `project`/`reject`/`reflect`/`identity`). Bare is fine
inside the generated `g*` docstrings (not autodoc-rendered).

**Warning-measurement recipes** (the log accumulates EVERY latexmk pass, so naive greps over- or
under-count): substitution `grep -ic 'start-string without end-string\|undefined substitution'`;
missing glyph `grep -c 'no ₙ\|Missing character'`; ambiguous xref `grep -c 'more than one target
found for cross-reference'`; undefined hyperrefs `grep -oE "Hyper reference .api:[^' ]+" | sort -u |
wc -l` (a plain `grep -c 'undefined'` UNDERCOUNTS — LaTeX wraps the word to the next line).

Still cosmetic (left as-is): ~28–42 `Font shape ... scit undefined` warnings (FreeSerif lacks the
small-caps-italic shape; LaTeX auto-substitutes — no content lost), plus benign Jupyter-kernel TCP
notices and `picte`/`ellipse` rounded-box package notices. Verified 2026-09-26: `make docs` in the
`BUILD_DOCS` image → exit 0, 102-page `geometry2.pdf`, 0 substitution / 0 missing-glyph / 0
undefined-hyperref / 0 ambiguous-xref; the ~14 remaining warnings are all in this benign set.

## Linking API names from docstrings (clickable cross-references)

To make a docstring name another API symbol as a **clickable hyperlink** in the HTML book, use a
Sphinx domain cross-reference role, not bare text: `` :func:`~gacalc.base.pseudoscalar_squared_sign` ``
(functions), `` :class:`~gacalc.functions.ComposableFunction` `` (classes), `:meth:`/`:attr:` for
members. The leading **`~`** shows only the last component as the link text. It resolves **iff the
target is autodoc'd** — i.e. its module is `automodule`d in `api.rst` (base/gn/functions/transforms/
measure/vectorcalc/frame are; g1/g2/g3 are NOT). Prefer these over restating a formula/type when the
goal is to send the reader to the canonical definition (e.g. `reverse`/`exp`/`unit_pseudoscalar_squared`
link `pseudoscalar_squared_sign` rather than spelling out `(−1)^(r(r−1)/2)`). Two gotchas already
recorded: qualify a **re-exported** name (below) to avoid ambiguity, and remember these roles show as
literal text (not links) in the **generated `g*` copies**, which aren't autodoc-rendered.

## conf.py E501 exemption

`book/docs/conf.py`'s only over-88 line is inside the `r"""..."""` `latex_elements["preamble"]`
string (the `\directlua{luaotfload.add_fallback(...)}` line, 89 cols). An inline `# noqa: E501` is
impossible there — it would inject text into the LaTeX preamble and break lualatex — so it is
exempted via `pyproject.toml` `[tool.ruff.lint.per-file-ignores]` `"book/docs/conf.py" = ["E501"]`
(same class as the `tools/gen_specialized.py` exemption: un-reflowable string-literal content).
`ruff check .` passes repo-wide.

## JupyterLab settings baked into the image (harvested from CLAUDE.md, 2026-09-13)

`make image` then `make shell`; Jupyter on port 8888. The image bakes two JupyterLab
settings:

- `jupytext-config set-default-viewer python` — a single click opens `py:percent` files as
  notebooks (the trade-off is `.py` no longer opens as plain text).
- `jupyter labextension disable @jupyterlab/apputils-extension:announcements` — kills the
  "Jupyter news" prompt; locked at sys-prefix so it can't be re-enabled.

Refresh the vendored Emacs packages (maintainer-only, rarely) with
`make update-emacs-packages` — full rationale in
`tasks/archive/2026/06/07/emacs-package-install-strategy.md`. (The vendored tree itself is
off-limits.)
