# Book page + notebook: the reciprocal frame and the two `Frame` inverses

**Done:** 2026-11-14, in the unattended batch on branch `autonomous-batch-2026-11-14`
**Source:** `tasks/archive/2026/11/07/lean-reciprocal-frame-and-frame-inverses.md` (the Lean work
that left the prose and symbolic-Python forms unwritten)

## Outcome

The reciprocal frame and the two `Frame` inverses, already machine-checked in Lean, now exist in all
three forms (repo `CLAUDE.md`, "Every piece of math comes in three forms"):

- **Prose + LaTeX:** `book/docs/proof-reciprocal-frame.rst`, *Proof: The Reciprocal Frame*. It
  opens with the oblique-frame problem, then states and proves theorems 1–8 of the Lean record's
  table: the eq 3.7 definition, each `aᵏ` a vector, the eq 3.5 Kronecker delta, eq 3.4
  reconstruction, the similar-right-triangles reading (`x_k = (m · y) / (m · a_k)`, folded into
  `aᵏ = m / (m · a_k)`), the last reciprocal vector as `w_n / |w_n|²`, both inverses' round trips,
  and their agreement. Each theorem cites its Lean names in
  `proofs/GacalcProofs/ReciprocalFrame2D.lean` / `ReciprocalFrame3D.lean`. It is linked from
  `book/docs/frames-qr.rst`'s toctree, as decided.
- **Symbolic Python:** `book/docs/notebooks/proof-reciprocal-frame.py`, in the page's toctree. It
  checks all eight theorems for a fully general 2D frame (`p, q, r, t` symbols) with a general
  `y = x_1 * a_1 + x_2 * a_2`, and repeats them in 3D for the oblique frame `2 * e_1`,
  `1 * e_1 + 3 * e_2`, `1 * e_1 + 1 * e_2 + 2 * e_3` with a fully general vector. Each check prints
  a difference simplified to zero (or the identity table). It runs in about 8.5 s under myst-nb.
- Gates: the containerized book build (`entrypoint/docs.sh`: HTML + PDF) passed. Both pages built,
  the notebook executed, and the build's only warnings were the duplicate `InvertibleFunction`
  cross-reference target in `Frame.to_invertible_function`'s docstring, which was already there.
  `ty check` and `tools/check_annotations.py` report nothing for the notebook, and the earlier
  `entrypoint/format.sh` run was clean on it.

## Decisions

- **Page placement (William Emerison Six <billsix@gmail.com>, 2026-11-08):** a new
  `book/docs/proof-reciprocal-frame.rst` beside the other `proof-*.rst` pages, linked from
  `book/docs/frames-qr.rst`, which keeps its maintainer-voice TODO for the narrative.

## Judgment calls made during the work

- **3D uses one integer frame, not a symbolic one.** A fully symbolic 3D frame makes the `Frame`
  round trips take minutes (the `slow` frame tests run 150–475 s each), well past the book's 600 s
  notebook timeout. The 3D section keeps the frame exact and the vector `z` general, which still
  exercises every theorem. The 2D section is general in both.
- **The page carries the "Draft. The prose is agent-drafted" note**, like the other agent-written
  proof pages, so the maintainer's voice pass is still owed.
- **No ePiX figure.** The similar-triangles argument would benefit from one (two right triangles
  standing on the face); it was left out to keep the task to its stated scope, and is a natural
  addition during the voice pass.
