# Stand up a Sphinx book pipeline for gacalc (HTML + PDF)

**Status:** proposed — decisions settled; **awaiting Bill's go-ahead to execute**.
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-08-02 (Bill)

## Goal

Give geometricalgebra (gacalc) a Sphinx-based book that builds to **HTML and PDF**
(no EPUB), the way `github.com/billsix/modelviewprojection` (mvp) does. The
Dockerfile, Makefile, and entrypoint must support building it. **No hand-written
book content yet** — the deliverable is a skeleton that builds: `sphinx-quickstart`
output, configured to resemble mvp, plus an **autodoc `api.rst`** so the build has
gacalc's own docstrings in it for context.

Book identity (Bill): project **"Plotting On Crappy Graph Paper"**, author
**William Emerison Six**, version **0.0.1**.

## Ownership & workflow (Bill, 2026-08-02)

1. **Now:** Claude updates this task doc. **Bill commits it.**
2. **Then:** Bill gives the go-ahead. **Claude does the work; Bill commits it.**
3. **At archive time:** Bill says "archive." Claude then:
   - looks through the scaffold folder (`tools/scaffold-book/`) for the temporary work;
   - checks whether anything in there actually deserves **extracting into `tools/`**
     as durable;
   - **flags any files in that folder that don't look like they belong to this task**
     and tells Bill;
   - **deletes the temporary work.** Bill commits the deletion.

Claude stages, never commits (per "Git: I commit, you don't — but you DO stage").

## Settled decisions

1. **No `texExpToPng` / no `inlinetex`, and no EPUB.** Use standard Sphinx math:
   `sphinx.ext.mathjax` renders math in **HTML**, native LaTeX renders it in **PDF** —
   the setup mvp used before commit `e682de30` ("inline latex in sphinx, for embedding
   in epub"). inlinetex existed *only* to fix EPUB math; dropping EPUB removes the
   entire reason for it. (mvp reference config: `git show e682de30~1:book/docs/conf.py`
   in `github.com/billsix/modelviewprojection`.)
2. **Keep `nbsphinx` + `myst_nb` exactly as mvp has them** (both enabled). Known
   footgun from mvp's `tasks/reference/notebook-sphinx-integration.md`: both register
   `.ipynb` and `myst_nb` wins the handler — Bill hasn't hit an issue, so keep it.
3. **Autodoc now** (`api.rst` pulling gacalc's docstrings) — gives the empty book real
   context. **Caveat, and the one reason we keep lualatex:** gacalc's docstrings are
   heavily non-ASCII (`√ ≙ e₁ ∧ · ∗ Ã ⁻¹ ²`, confirmed across `base.py`, `gn.py`,
   `g1/2/3.py`, `functions.py`). Autodoc puts those characters into the LaTeX build, and
   **pdflatex aborts on them** — so PDF uses `latex_engine = "lualatex"` (+
   `latex_use_xindy = False`), matching current mvp. This is about literal Unicode in
   docstrings, NOT about math rendering (mathjax/native-LaTeX handle the math fine).

**Extension set** (final): `sphinx.ext.autodoc`, `sphinx.ext.napoleon`,
`sphinx.ext.viewcode`, `sphinx.ext.mathjax`, `sphinx.ext.imgconverter`, `nbsphinx`,
`myst_nb`. **Excluded** (content-dependent, add later if needed): `inlinetex`,
`sphinxcontrib.bibtex` (no `references.bib` yet).

## Package handling (Bill: "dnf install them, you're in a container")

The extras needed to *build* the docs are `dnf install`ed **into this sandbox** during
the work (so Claude can scaffold + smoke-test here) **and added to
`/foo/opt/runClaudeInContainer`'s Dockerfile** so they're baked into the sandbox image
for later sessions. Candidate list (verify exact Fedora-44 names when installing):
`python3-furo`, `python3-nbsphinx`, `myst-nb`, `latexmk`,
`texlive-luahbtex`/`texlive-fontspec`/`texlive-gnu-freefont` (lualatex fonts).
`sphinx-quickstart`/`sphinx-build`/`lualatex` are already present in the sandbox;
`latexmk` and furo are not.

These are the sandbox-side tools. The **gacalc image** gets the same toolchain via the
Dockerfile `BUILD_DOCS` block below — that is the permanent, committed dependency.

## Tooling reality (checked 2026-08-02)

- **Sandbox:** `sphinx-quickstart`, `sphinx-build`, `lualatex` present; `latexmk`
  absent; furo/nbsphinx/myst-nb not installed. So scaffold + an **HTML smoke build** run
  here after the dnf installs; the **full PDF** build is confirmed in the gacalc
  container (nested with `--cgroups=disabled`) or by Bill.
- **gacalc today:** no `book/` or `docs/`. Dockerfile has **no `BUILD_DOCS` arg**, no
  sphinx/furo, but already installs a `texlive-xetex` + collections block (for nbconvert
  notebook→PDF) — audit and reuse the overlap. Makefile `.DEFAULT_GOAL := help`;
  `FILES_TO_MOUNT` has **no output mount**; no docs target. `entrypoint/entrypoint.sh`
  just activates the venv and execs bash.

## Plan

### Phase 1 — scaffold (temporary scripts under `tools/scaffold-book/`)

1. `01-quickstart.sh` (flat layout like mvp — source and `_build` in one dir):
   ```sh
   sphinx-quickstart book/docs -q --no-sep --makefile --no-batchfile \
       -p "Plotting On Crappy Graph Paper" -a "William Emerison Six" \
       -v 0.0.1 -r 0.0.1 -l en
   ```
2. `02-configure.sh` — `sed`/heredoc edits to the generated `conf.py`:
   `html_theme = "furo"`; the extension set above; `latex_engine = "lualatex"` +
   `latex_use_xindy = False` + a `latex_elements["preamble"]` (image placement/width,
   as mvp); `autodoc_default_options`; `mathjax3_config`; `exclude_patterns`. Write
   `book/docs/_static/custom.css`. Add an `api.rst` with `automodule` over the gacalc
   package and reference it from `index.rst`.
   - **Do NOT copy mvp's `book/docs/Makefile`** — its `%: Makefile spellcheck`
     catch-all runs `aspell` interactively and hangs any TTY-less build. Keep the stock
     quickstart Makefile.
3. Stage the two scripts + generated `book/docs/`. Bill commits.

### Phase 2 — permanent build wiring (kept)

4. **Dockerfile:** add `ARG BUILD_DOCS=0`; under it `dnf install` sphinx + furo +
   nbsphinx + myst-nb + texlive/lualatex/fontspec/gnu-freefont + latexmk, reusing the
   existing texlive block where it overlaps.
5. **Makefile:** `BUILD_DOCS ?= 1`; pass `--build-arg BUILD_DOCS=$(BUILD_DOCS)` in
   `image`; add `-v ./output/:/output/:Z` to `FILES_TO_MOUNT`; add a `docs`/`html`
   target (container run → **html + pdf** → `output/`) and a `clean` target.
6. **Docs build script** (`entrypoint/docs.sh` or a make recipe): `sphinx-build -M html`
   then `-M latexpdf`; copy artifacts to `/output/gacalc/`; `touch .nojekyll`. **No epub
   target.**

### Phase 3 — verify + teardown

7. HTML smoke build in the sandbox; full **html + pdf** build in the gacalc image
   (`BUILD_DOCS=1`, nested or Bill). Confirm both are produced from the empty+autodoc
   skeleton. **Caveat:** `latexmk` is absent in the sandbox, so the sandbox verifies
   HTML only — the PDF gate is the container build.
8. Teardown happens at **archive time** (see Ownership & workflow): scan
   `tools/scaffold-book/`, extract anything durable into `tools/`, flag strays, delete
   the temporary work. Bill commits.

## Notes / conventions in play

- Book at `book/docs/`, `output/` bind-mount — both mirror mvp. (Say if you'd prefer
  `docs/`.)
- gacalc's git remote is the self-hosted box; refer to sibling repos by GitHub URL in
  committed docs (mvp = `github.com/billsix/modelviewprojection`).
- Nested container builds need `--cgroups=disabled` (Bill pre-authorized for that
  transient flag only).
