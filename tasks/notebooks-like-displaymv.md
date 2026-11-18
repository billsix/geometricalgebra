# Bring the notebooks up to `notebooks/displaymv.py`, and sharpen the guidance from it

**Status:** proposed — questions answered 2026-11-18; needs the go-ahead to start
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com>: "I love notebooks/displaymv.py …
figure out why I like it so much … update the guidance, and update all other notebooks to be
similar as reasonable")

## BLUF

`notebooks/displaymv.py` is the notebook the maintainer likes best.
`tasks/reference/book-notebook-teaching-style.md` already takes its opening as the model ("The
model: the opening of `notebooks/displaymv.py`", eight rules, plus "What to avoid"). The book
notebooks were swept to that doc on 2026-11-16, and the demo notebooks under `notebooks/` never
were. This task has two parts:
1. Study the whole of `displaymv.py` and add to the guidance what the doc does not yet say.
2. Bring the other notebooks to it, as far as is reasonable.

Done means:
- the reference doc states the confirmed qualities;
- each notebook in scope is rewritten to them;
- `make check-notebooks` (pyright over `notebooks/`), `make format` and a headless run of each
  notebook pass.

## Context (read first)

- `notebooks/displaymv.py`: the model (679 lines, 67 code cells, 58 Markdown cells).
- `tasks/reference/book-notebook-teaching-style.md`: the current guidance ("What a notebook is",
  "The model", "What to avoid", "Mechanics", "Symbolic notebooks", the checklist).
- `tasks/reference/book-outline.md` ("Structural conventions"): the book notebooks' structure.
- `tasks/archive/2026/11/16/book-notebooks-teaching-style-sweep.md`: the earlier sweep, on book
  notebooks only.
- `CLAUDE.md` › "Math notation for readers", and the notebook carve-outs under "Conventions the agent
  must obey" (`displayg2`/`displayg3` may alias full-class constants; `displayvectorcalc` binds
  `i, j, k`).

## What is good about `displaymv.py` (agent's reading, 2026-11-18; to confirm)

Already captured in the reference doc:
1. It starts from algebra the student knows: `(x + 2)(x + 3)`, collecting `2x + 3y + 5x`, the
   imaginary `i`.
2. One idea per cell: a Markdown cell states one rule in plain words, and a one-line code cell
   confirms it.
3. An optional formal layer, labelled skippable ("The same rules, written as math").
4. Hand reductions as chains of equalities with a reason on each line, followed by the code that
   computes the same product.
5. The question comes from the student's own step: "we quietly *re-grouped* … were we *allowed*
   to?", then three groupings computed, then the property named.
6. Numbers before symbols (`3 * e_1 + 4 * e_2`, Pythagoras) in the demo notebooks.
7. `show_mult` makes the distribution visible. As of 2026-11-18, `show_cancellation` makes a proof's
   cancellation visible.
8. One sentence pointing at the implementation (`decrease_grade` in `gn.py`).

**Not yet in the doc**, which this study found:

9. **Sentences run across cells.** "The plain-number part is the dot product," → code → "and the
   plane part is the wedge:" → code. The prose reads as one continuous sentence, and each output
   lands where its clause ends.
10. **Plain names before jargon.** "Plain-number part", "plane part", "arrows", "letters" come
    first; "scalar", "bivector", "grade" come later or in the optional layer.
11. **Headings are questions or claims**, not topics: "Where do the plain numbers go? Scalars
    first.", "A longer example, and why grouping is about to matter".
12. **The recipe grows one step at a time.** Three rules, then "putting the rules together", then
    "the recipe grows just one opening step" (scalars first). Each section adds exactly one move to
    a procedure the student already holds.
13. **Prediction prompts:** "Before running the next cell, predict its result", used a handful of
    times at the points where a student can genuinely predict.
14. **It ends in a proof.** General symbolic multivectors, both groupings term by term, and a
    difference that is zero. Not one example: a proof for every element, and it says so.
15. **Zero developer noise:** no `pyright: ignore`, no typing workarounds in sight, short cells
    (mostly one expression).

## Where the other notebooks stand (measured 2026-11-18)

A code cell that directly follows another code cell has no prose of its own; the "after code" column
counts those.

| Notebook | Code cells | After code | `pyright: ignore` |
| --- | --- | --- | --- |
| `displaymv.py` (model) | 67 | 11 | 0 |
| `displayg2.py` | 86 | 50 | 26 |
| `displayg3.py` | 59 | 35 | 22 |
| `displaygraded.py` | 40 | 17 | 1 |
| `displayrotations.py` | 20 | 2 | 9 |
| `displaytransforms.py` | 18 | 3 | 0 |
| `displayvectorcalc.py` | 6 | 0 | 2 |
| `displayproofs.py` | 7 | 1 | 1 |
| book notebooks, total | 725 | 81 (11 %) | (swept 2026-11-16) |

`displayg2.py` and `displayg3.py` are the clear gaps. Each runs long stretches of code with no
narrative, carries developer noise, and covers many subjects in one file.

## Plan

1. Settle the open questions. Write the confirmed qualities into
   `tasks/reference/book-notebook-teaching-style.md` (extend "The model" and the checklist, and say
   the doc covers the demo notebooks as well as the book's).
2. Rewrite the notebooks in scope, one per commit, in order of need: `displayg2`, `displayg3`,
   `displaygraded`, then the small ones. For each:
   - a Markdown lead-in for every code cell;
   - plain names first;
   - question or claim headings;
   - prediction prompts where they fit;
   - developer noise moved out of the student's path;
   - a proof section where the notebook's subject has a law to prove (`show_cancellation`);
   - the bold-arrow notation in the Markdown (`\vec{\mathbf{e}}_1`, `\mathbf{e}_{12}`), including
     in `displaymv.py` itself (decision 4).

   `displayg2.py` and `displayg3.py` are split into one-subject notebooks first (decision 5). After
   the demo notebooks, re-sweep the book notebooks (`book/docs/notebooks/*.py`) against qualities
   9–15 (decision 1). Unifying the two kinds of notebook is the separate, not-yet-authorized
   `tasks/unify-demo-and-book-notebooks.md`.
3. Gates for each notebook: a headless run (Agg), `make check-notebooks`, `make format`, and
   `tools/check_annotations.py` (no new rows).
4. When splitting, fix every link to the old files (README, `CLAUDE.md`, other notebooks, the
   `make notebooks-ipynb` list if any).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. **Scope: (b), the book notebooks too.** Why the demo and book notebooks differ, and a plan to unify them while they stay in the book, is a separate task, `tasks/unify-demo-and-book-notebooks.md`. That one is NOT started until the maintainer says so explicitly.
2. **Qualities 9–15 confirmed** ("sure").
3. **Prediction prompts as `displaymv.py` has them:** a handful per notebook, where a student can genuinely predict.
4. **The bold-arrow notation applies to every notebook, wherever it lives**, `displaymv.py` included. `CLAUDE.md` › "Math notation for readers" now says so.
5. **Split `displayg2.py` and `displayg3.py`** into one-subject notebooks.
6. **Keep `displaymv.py`'s grams-to-moles aside as it is.** The guidance's "one notebook, one subject" allows a short, labelled aside like it.

## Open questions

None.
