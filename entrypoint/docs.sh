#!/usr/bin/env bash
# Build the gacalc Sphinx book (HTML + PDF) inside the container and copy the
# results to the bind-mounted /output tree on the host.
#
# autodoc imports gacalc to read its docstrings, so -- exactly like shell.sh --
# we first generate the specialized algebras (g1/g2/g3.py, which are gitignored)
# and editable-install the package, so `import gacalc` works during the build.
#
# This is a build script, so it fails fast: if the HTML step fails there is no
# point attempting the (slow) PDF step.
set -eu

export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate
cd /gacalc

# Make the package importable for autodoc AND for the notebook kernels. The book's
# notebooks carry a jupytext ``kernelspec: python3`` header, so their .ipynb request
# the image's venv ``python3`` kernel -- which, with this editable install, imports
# gacalc. (Without the header they'd request no kernel and myst_nb would fall back to
# a python that can't see the venv's gacalc.)
python tools/gen_specialized.py
uv pip install --python "$(which python)" --no-deps --no-index --no-build-isolation -e .

# Convert the percent-format notebooks (notebooks/*.py, the one notebook directory) to
# .ipynb inside the book's source tree, so myst_nb can execute and render them as
# book/docs/notebooks/<name>. The .py are the tracked source; the .ipynb are build
# artifacts (gitignored). conf.py's exclude_patterns lists any notebook the book leaves out.
mkdir -p book/docs/notebooks
for f in notebooks/*.py; do
    jupytext --to ipynb -o "book/docs/notebooks/$(basename "${f%.py}").ipynb" "$f"
done

# Render the book's ePiX figures (book/figures/epix/*.py, written with the epix Python
# package the way epix-mirror's notebooks are) to _static/epix/<name>.{pdf,png}; the
# pages reference them as `_static/epix/<name>.*` and Sphinx picks pdf for LaTeX, png
# for HTML. Needs the image's ePiX (USE_EPIX=1, the default); fails loudly otherwise.
python tools/render_epix_figures.py

# Build the two formats. `make html` / `make latexpdf` use book/docs/Makefile,
# which just calls sphinx-build. The PDF goes through LuaLaTeX (set in conf.py).
cd book/docs
make html
make latexpdf

# Copy the finished book to the bind-mounted output tree. `.nojekyll` stops
# GitHub Pages from mangling the _static / _images folders if these are published.
mkdir -p /output/gacalc
rm -rf /output/gacalc/html
cp -r _build/html /output/gacalc/html
# Only the book itself: _build/latex/ also holds every figure the PDF includes (the
# ePiX figures, the notebooks' matplotlib figures, the Graphviz graph).
cp _build/latex/geometry2.pdf /output/gacalc/
touch /output/gacalc/.nojekyll

echo "Book built: /output/gacalc/html/ and /output/gacalc/*.pdf"
