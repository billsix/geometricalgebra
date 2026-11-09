# Book: restructure into Part I (the plane) and Part II (space), with a second route to the product

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.2, §1.2, and its open questions 1–4
**Decisions** (William Emerison Six <billsix@gmail.com>, 2026-11-09):

1. (b): a chapter that builds the product from projection and rejection, "as long as you can get it
   to work";
2. `blade-square-sign` and `levels-of-abstraction` after `defining-g2`;
3. Part I's 3D material to Part II, and `index.rst` split;
4. no page has had a voice pass; reword as needed, in the modelviewprojection voice.

All four are recorded in `tasks/reference/book-outline.md`.

## What changed

- **The new chapter, `book/docs/product-from-projection.rst`**, sits right after `projection`. It
  rotates `b` onto the x-axis as in `proof-projection`, reads where `a` lands, `(x, y)`, and shows
  `|b| * x = a·b` and `|b| * y` is the signed area. It defines `b * a = |b| * (x + y * e₁₂)`,
  multiplies it out with `geometric-product`'s rules to show the two routes agree, and names the
  parts dot and wedge. All three forms:
  - **Lean:** `G2.mul_eq_magnitude_smul_alignSP` in `proofs/GacalcProofs/StandardPosition2D.lean`
    (no warnings);
  - **symbolic Python:** `book/docs/notebooks/product-from-projection.py`, which runs and is
    ty-clean;
  - **prose**, citing both.

  It reuses the `sp4` figure, and `rotation-from-vectors` hangs off it, since that page relies on
  `a * b = a·b + a∧b`.
- **`geometric-product.rst`** now says it is the first of two routes to the product, and points at
  the second. It also gains the `e₁₂ * e₁₂ = −1` fact (turn by 90° twice), which `blade-square-sign`
  cites. `rotation-from-vectors` left its toctree, and that page's "From geometric-product …" now
  cites `product-from-projection`.
- **`proof-projection.rst`:**
  - its opening (no "As promised in the outline", no "throw the coordinates away" for a product
    already defined);
  - "If you already read projection, you know the slick formula" (`projection` has none);
  - its payoff, which now points at `product-from-projection`, written `\vec{b} * \vec{a}`;
  - its 3D section moved out.
- **`book/docs/index.rst`:** three captioned toctrees. "Part I — The plane" ends `projection`,
  `product-from-projection`, `reflection`, `orthogonal`, `dual`, `defining-g2`,
  `levels-of-abstraction`, `interactive-calculator`. "Part II — Space" is `three-dimensions`,
  `blade-square-sign`, `projection-rejection-3d`, `frames-qr`. "Reference" is `api`. The skeleton
  sentence is replaced by a two-line description of the halves.
- **Part II:**
  - **`proof-projection-3d.rst`** (new) holds `proof-projection`'s 3D section, with
    `notebooks/proof-projection-3d.py`, which got that notebook's 3D cells.
  - **`projection-rejection-3d.rst`**'s toctree holds `proof-projection-3d` and `proof-cross`.
  - **`proof-cross.rst`** cites `proof-projection-3d` for the reduction (it cited
    `projection-rejection-3d`); its notebook toctree is no longer hidden.
  - **`blade-square-sign`** moved whole. It is a general-n argument (grades 1–5), so splitting off
    grades 3–5 would leave no argument.
- **`levels-of-abstraction`** moved after `defining-g2`. Its notebook's 𝒢₃ section moved to
  `notebooks/three-dimensions.py` (which was a stub), and its sine/cosine cells use whole-number
  vectors with exact `sympy.simplify` checks, not `3.0 * …` and `round(…, 10)`.
- **`tasks/reference/book-outline.md`:**
  - the garbled status sentence, rewritten;
  - "Current reading order";
  - the five decisions of 2026-11-09 (including the plain `e_1` spelling);
  - the file lists, "Filled so far", the proof-pages paragraph, and Part II.

**Other tasks' edits carried in these files:** several of them also carry the batch's notation
edits (`tasks/archive/2026/11/09/book-notation-sweep.md`) and Draft notes
(`tasks/archive/2026/11/09/book-cross-references-and-author-notes.md`), because those edits touched
the same lines.

## Verification

- `product-from-projection.py`, `proof-projection.py`, `proof-projection-3d.py`,
  `levels-of-abstraction.py` and `three-dimensions.py` run as scripts; `ty check book/docs/notebooks`
  is clean; `tools/check_annotations.py` reports nothing for them.
- `lake build GacalcProofs.StandardPosition2D`: clean.
- **A scratch HTML build** (Sphinx 9.1 in the sandbox; notebooks converted with jupytext and not
  executed): exit 0, with no undefined documents, labels or orphaned pages. The only warnings were
  the missing ePiX images and three API docstring warnings this task didn't touch.
- **Not run:** `make docs` itself, which executes the notebooks and builds the PDF. It needs the full
  image (`BUILD_DOCS=1 USE_EPIX=1`).
