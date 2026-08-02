#!/usr/bin/env bash
#
# 01-quickstart.sh  —  create the empty Sphinx book for gacalc
# =============================================================================
#
# WHAT THIS DOES
#   Runs `sphinx-quickstart`, the official tool that creates a brand-new,
#   empty documentation project. It writes a few files into  book/docs/ :
#
#       conf.py     the book's settings   (title, theme, add-ons, ...)
#       index.rst   the front page and table of contents
#       Makefile    a convenience wrapper so you can type `make html`
#       _static/    a folder for your own CSS and images
#       _build/     the folder Sphinx writes the finished HTML/PDF into
#
#   Left to itself, sphinx-quickstart stops and asks you about ten questions.
#   We answer all of them up front with the command-line options below, so the
#   script runs all the way through without stopping to ask anything. That is
#   what the `-q` ("quiet") option and the `-p` / `-a` / `-v` options are for.
#
# HOW TO RUN
#   Stand in the top folder of the geometricalgebra repository and run:
#
#       bash tasks/adhoc/sphinx-book-pipeline/01-quickstart.sh
#
#   Then run its companion, 02-configure.sh, to turn this bare project into
#   one that looks like the modelviewprojection book.
#
# IMPORTANT: this script is TEMPORARY scaffolding. Once the book builds, the
#   whole  tasks/adhoc/sphinx-book-pipeline/  folder is deleted. The files it PRODUCES
#   (everything under book/docs/) are what we keep.
# =============================================================================

# Stop the script the moment any command fails, and complain if we ever use a
# variable that was never set. (Belt and suspenders — keeps a half-finished
# project from being left behind.)
set -eu

# The folder the book will live in. Every path in this script is written
# relative to the repository's top folder, so that is where you must run it.
BOOK_DIR="book/docs"

# --- Safety checks before we touch anything ---------------------------------

# Landmark check: pyproject.toml sits at the top of the repo. If it is not
# here, we are in the wrong folder and should not scatter files around.
if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: run this from the TOP folder of the geometricalgebra repo."
    exit 1
fi

# sphinx-quickstart refuses to overwrite an existing project, and so do we.
# If you want a clean start, delete book/docs by hand first, then re-run.
if [ -e "$BOOK_DIR/conf.py" ]; then
    echo "ERROR: $BOOK_DIR already exists. Delete it first to regenerate."
    exit 1
fi

# --- Create the empty project -----------------------------------------------

# Each option, explained:
#   book/docs          where to create the project
#   -q                 "quiet": use our answers, ask no questions
#   --no-sep           keep source and build together (book/docs and
#                      book/docs/_build), rather than splitting them into
#                      separate source/ and build/ folders. This matches the
#                      modelviewprojection book.
#   --makefile         create a Unix Makefile (so `make html` works) ...
#   --no-batchfile     ... but skip the Windows .bat equivalent, we don't use it
#   -p "<name>"        the project (book) title
#   -a "<name>"        the author
#   -v 0.0.1           the short version, shown in the docs
#   -r 0.0.1           the full release string (same as the version here)
#   -l en              the language: English
sphinx-quickstart "$BOOK_DIR" \
    -q \
    --no-sep \
    --makefile --no-batchfile \
    -p "Plotting On Crappy Graph Paper" \
    -a "William Emerison Six" \
    -v 0.0.1 \
    -r 0.0.1 \
    -l en

echo
echo "Done. Created an empty Sphinx project in $BOOK_DIR/"
echo "Next: bash tasks/adhoc/sphinx-book-pipeline/02-configure.sh"
