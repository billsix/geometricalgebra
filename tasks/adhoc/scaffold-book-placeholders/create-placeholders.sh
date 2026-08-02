#!/usr/bin/env bash
#
# create-placeholders.sh  —  scaffold the book's blank pages & notebook stubs
# =============================================================================
#
# WHAT THIS DOES
#   Creates the empty skeleton of the book described in
#   tasks/reference/book-outline.md: one placeholder page per section, in reading
#   order, plus a percent-format Python notebook stub for the sections whose
#   payoff is running gacalc and showing a symbolic/plotted result.
#
#   Two kinds of file per section:
#     book/docs/<name>.rst            the prose page (the narrative / the "use")
#     book/docs/notebooks/<name>.py   a Jupyter notebook in "percent" format,
#                                     editable as a plain script, that the book
#                                     build converts and executes
#   Each notebook stub holds just a "1 + 1" cell for now, so we can confirm the
#   notebooks actually execute in the build. Prose pages that have a notebook
#   link to it with a small table-of-contents (a Sphinx "toctree").
#
#   The reading order lives in book/docs/index.rst (written at the end). Because
#   order is controlled there, rearranging sections later never needs a rename.
#
# HOW TO RUN
#   From the top of the geometricalgebra repository:
#       bash tasks/adhoc/scaffold-book-placeholders/create-placeholders.sh
#
# TEMPORARY: this is one-time scaffolding. It is removed when the
#   scaffold-book-placeholders task is archived; the files it PRODUCES
#   (book/docs/*.rst and book/docs/notebooks/*.py) are what we keep.
# =============================================================================

set -eu

# Landmark check: run from the repo root.
[ -f pyproject.toml ] || { echo "ERROR: run from the geometricalgebra repo root."; exit 1; }

BOOK="book/docs"
mkdir -p "$BOOK/notebooks"

# SLUGS collects the page names in the order they are created, so index.rst can
# list them in that same reading order at the end.
SLUGS=()

# --- helper: write one prose page --------------------------------------------
# Arguments: 1=name  2=Title  3=one-line description  4=has-notebook (yes/no)
make_prose() {
    name="$1"; title="$2"; desc="$3"; has_nb="$4"

    # An RST page title is underlined by a row of '=' at least as long as the
    # title. This builds a row of '=' exactly the length of the title.
    underline=$(printf '=%.0s' $(seq ${#title}))

    {
        printf '%s\n%s\n\n' "$title" "$underline"
        printf 'Placeholder — content to come. %s\n' "$desc"
        # If this section has a companion notebook, link it as a sub-page.
        if [ "$has_nb" = "yes" ]; then
            printf '\n.. toctree::\n   :maxdepth: 1\n\n   notebooks/%s\n' "$name"
        fi
    } > "$BOOK/$name.rst"
}

# --- helper: write one notebook stub (percent format) ------------------------
# Arguments: 1=name  2=Title
make_nb() {
    name="$1"; title="$2"
    cat > "$BOOK/notebooks/$name.py" <<PYEOF
# %% [markdown]
# # $title — calculations
#
# Placeholder notebook — content to come. The cell below only confirms the
# notebook executes in the book build.

# %%
1 + 1
PYEOF
}

# --- helper: create a page (prose, plus its notebook if any) and remember it -
# Arguments: 1=name  2=Title  3=description  4=has-notebook (yes/no)
page() {
    make_prose "$1" "$2" "$3" "$4"
    [ "$4" = "yes" ] && make_nb "$1" "$2"
    SLUGS+=("$1")
}

# =============================================================================
# The book, in reading order. The 4th argument says whether the section gets a
# companion notebook (yes = running gacalc / showing a symbolic or plotted
# result is the point; no = prose only for now).
# =============================================================================

# -- Framing -----------------------------------------------------------------
page hook              "Preview: Rotation, Projection, Reflection" \
     "Open with what geometric algebra lets you do — before any definitions." yes
page canonical-form    "Exact Answers, Not Decimals" \
     "``1 + √2`` is the answer; we keep things exact and let a computer give a decimal only if we ever truly need one." yes

# -- Part I: two dimensions --------------------------------------------------
page one-dimension     "One Dimension: m·x + b" \
     "Start in 1D: input value on the left, output value on the right, on overlaid graph paper." yes
page multiplication    "Multiplication You Already Know" \
     "Integers, signed integers, fractions, exponents — a warm-up to 'multiplication can mean different things.'" no
page trigonometry      "Sine and Cosine" \
     "Define sine and cosine from geometry, then how precalculus extends them." no
page sets              "Sets and Notation" \
     "Sets and their notation — integers, fractions, and what the notation means." no
page vectors-as-number-lines "Vectors as Relative Number Lines" \
     "A vector is a relative number line." yes
page relative-graph-paper    "Relative Graph Paper" \
     "Two vectors make relative graph paper (kept at 90° for most of the book): coordinates, the natural basis, and why a ruler only means something relative to something else." yes
page vector-addition   "Vector Addition" \
     "Vector addition, in pictures, in 2D." yes
page rotate            "Rotate" \
     "Define rotate the way modelviewprojection does: from the direction of vec 1 to vec 2, and magnitudes don't matter." yes
page geometric-product "The Geometric Product" \
     "Define it from rotate; see it produce a rotation as an action." yes
page projection        "Projection" \
     "Rotate, then take the components — shown equivalent, in coordinates, to the geometric-product implementation." yes
page reflection        "Reflection" \
     "The same treatment as projection." yes
page orthogonal        "Orthogonal" \
     "Define orthogonal, related to angles." no
page dual              "The Dual" \
     "The dual." yes
page defining-g2       "Defining the Algebra: G2" \
     "The formal algebra: G2, the basis blades as constants, and the rules for addition, subtraction, and multiplication (including how ``e₁e₂`` resolves when we plot)." yes
page interactive-calculator "An Interactive Calculator" \
     "Something that works like a graphing calculator — vector addition, rotate, translate. (θ is a property we show, not something we solve for.)" no

# -- Part II: three dimensions (fleshed out much later) ----------------------
page three-dimensions  "Into Three Dimensions" \
     "The second half of the book: restart from the geometric product in 3D." yes
page projection-rejection-3d "Projection and Rejection in 3D" \
     "Projection and rejection in three dimensions." yes

# -- A proof kept out of the main reading flow (its own .rst) ----------------
cat > "$BOOK/proof-rotate.rst" <<'RSTEOF'
Proof: Rotate
=============

Placeholder — content to come. The precalculus-level proof of rotate, kept out of
the main reading flow (linked from "Rotate" and "The Geometric Product").
RSTEOF

# =============================================================================
# Write index.rst: the reading order (the prose pages, then the API reference),
# plus a hidden entry for the proof page so Sphinx doesn't warn that it is
# unreferenced.
# =============================================================================
{
    cat <<'HEADER'
Plotting On Crappy Graph Paper
==============================

The gacalc book. This is the skeleton — prose, graphs, and notebooks fill in
later, and sections may be written out of order.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

HEADER
    for s in "${SLUGS[@]}"; do
        printf '   %s\n' "$s"
    done
    printf '   %s\n' "api"
    cat <<'FOOTER'

.. toctree::
   :hidden:

   proof-rotate
FOOTER
} > "$BOOK/index.rst"

echo "Done. Created ${#SLUGS[@]} prose pages, their notebook stubs, proof-rotate.rst, and index.rst."
echo "Convert the notebooks and build with the repo's  make docs  target."
