# Bring the notebooks up to `notebooks/displaymv.py`, and sharpen the guidance from it

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; overnight batch
`overnight-batch-2026-11-18`)
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-11-18 (the maintainer: "I love notebooks/displaymv.py … figure out why I like it
so much … update the guidance, and update all other notebooks to be similar as reasonable")

## Outcome

**The guidance.** `tasks/reference/book-notebook-teaching-style.md` now:
- says it covers every notebook, the book's and the demo ones under `notebooks/`;
- adds the seven qualities this study found in `displaymv.py`, as rules 9–15 under "The model":
  - sentences that run across cells;
  - plain names before jargon;
  - headings as questions or claims;
  - a recipe that grows one step at a time;
  - a handful of prediction prompts;
  - ending in a proof, with `show_cancellation` when it is readable;
  - zero developer noise;
- extends its checklist and records the sweep.

**The demo notebooks.**
- **Split into one-subject notebooks and rewritten** to the rules (lead-ins, plain names, question
  headings, prediction prompts, checks shown as a zero difference instead of `==` / `assert`,
  bold-arrow notation, no typing workarounds in sight):
  - `displayg2.py` (718 lines) became `displayg2.py` (the product in the plane, now ending in a
    `show_cancellation` proof of associativity), `displayg2areas.py` (the sine formula, area,
    signed area, and the projection/rejection split of the product) and `displayg2transforms.py`
    (transforms on `g2.G` and the graph paper);
  - `displayg3.py` became `displayg3.py` (the product in space) and `displayg3measures.py` (area,
    volume, signed volume, the sine formula in space).
- **`displaymv.py` itself** has the bold-arrow notation in its Markdown and lead-ins for its 10 bare
  code cells. Its units aside is kept (decision 6).
- **`displaygraded.py`:**
  - its 17 bare cells got lead-ins, most made from the code comment that had described the cell;
  - the inline comments that gave a cell's answer before it ran are gone;
  - the "versor sandwich equals `projection_rotation`" `==` is now a zero difference.
- **The small notebooks:**
  - `displayproofs.py`: capitals for its general multivectors (`A`, `B`, `C`, per the notation rule)
    and one value per cell;
  - `displayrotations.py`: bold vectors, lead-ins, no `typing.cast` (the annotations are widened to
    `MultiVectorBase` instead);
  - `displaytransforms.py`: lead-ins;
  - `displayvectorcalc.py`: the scalar constructor for symbolic coefficients.
- **No `pyright: ignore` trailers remain.** All 60 were redundant: `pyrightconfig.json` already turns
  `reportUnusedExpression` off.

**The book notebooks.** Every bare code cell (81 across 20 notebooks) got a lead-in. A live figure
gets "Drawn at the plot values:", and a second vector continues the sentence ("and
$\vec{\mathbf{b}}$:"). The notebooks had no developer noise to remove.

**Tooling and docs:**
- `notebooks/*.py` are now exempt from E501 like the book notebooks, and
  `tools/check_notebook_prose_width.py` checks them by default (`pyproject.toml`, the tool's
  docstring, `CLAUDE.md`).
- `CLAUDE.md` lists the new notebooks and extends the full-`G` aliasing carve-out to
  `displayg2transforms`. `tasks/reference/design-decisions.md` says the same.
- References to the moved sections are repointed: `src/gacalc/base.py` (a comment),
  `proofs/GacalcProofs/Lagrange.lean` (a doc comment), `tasks/archive/2026/11/19/notebook-dot-wedge-projection-demo.md`.
- `tasks/reference/type-annotation-exemptions.md`: §6 (the notebook symbol unpacks) is gone, now that
  the names are declared, and the floor is 63 rows.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. Scope: the book notebooks too. Unifying the two sets is the parked
   `tasks/unify-demo-and-book-notebooks.md`.
2. Qualities 9–15 confirmed.
3. Prediction prompts as `displaymv.py` has them.
4. Bold-arrow notation in every notebook, `displaymv.py` included.
5. Split `displayg2.py` and `displayg3.py`.
6. Keep `displaymv.py`'s units aside.

## What was done "as reasonable", and what was not

- **Book notebooks: lead-ins only.** They got the mechanical part of the re-sweep. Their headings
  (quality 11) and prediction prompts (quality 13) were not rewritten. The headings mirror their
  `.rst` pages' sections, and rewriting thirty pages' prose to the new qualities is a review-sized
  job of its own. File it as a follow-up if you want it.
- **The 64-row `show_mult` table in `displayg3.py`** is kept, with a sentence saying it shows the
  method scales. Its associativity check is a zero difference, not `show_cancellation`, because each
  blade would have sixty-four terms a side (quality 14's own limit).

## How

`tasks/adhoc/notebooks-like-displaymv/`, all one-shot and deleted at archive:
- `blades.py` rewrote the basis blades in Markdown math. It is idempotent (a second run changed
  nothing), and its `bold_vectors` helper did the per-notebook vector letters.
- `book_leadins.py` added the book lead-ins by pattern. It stops on any cell no rule covers, and is
  idempotent.

The notebook rewrites themselves were done by hand.

## Verification

- Every demo notebook ran headless (Agg). The difference cells were checked cell by cell with
  `tools/run_notebook_cells.py`: every one is `0`, or displays as `0` through the lazy class's
  simplifying LaTeX.
- `ty check notebooks/` was clean.
- ruff and `tools/check_notebook_prose_width.py` were clean on every notebook.
- `tools/check_annotations.py` reported 63 rows, all classified out or listed.
- In the container against the existing image:
  - `entrypoint/format.sh` was clean (ruff, ty over `src`/`tests`/`tools`/`book/docs/notebooks`,
    the changelog, epix-keyword and prose-width checks);
  - `pyright notebooks/` (the `make check-notebooks` gate) gave 0 errors, after fixing one it found
    in `displayrotations.py`;
  - `pytest -m "not slow"` passed: 1913 passed, 2 skipped.
- **Not run: `make docs`.** The book notebooks' changes are Markdown lead-ins only, so their
  execution is unchanged; the next book build renders them.
