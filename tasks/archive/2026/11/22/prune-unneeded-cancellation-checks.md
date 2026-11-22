# Prune the cancellation checks that add nothing

**Status:** done 2026-11-22
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## What this did

The maintainer read the book's PDF and found many "Terms with the same number cancel:" displays
(`show_difference` / `show_cancellation`) proving equalities that need no proof. Of the 171 calls in
the notebooks, 38 were removed and 133 remain. Each removed display lost its code cell, and its
lead-in sentence ("Their difference:") became a plain statement of the claim, or was dropped where
the page's own prose already made it. `displayg2.py`'s associativity section, whose cell also bound
`G2_3`, now points to `displaymv.py`, which shows the same display beside its Lean twin. The helpers
in `src/gacalc/nbdisplay.py` are unchanged; only calls went. A notebook left with no call dropped
its `nbdisplay` import names.

Four reasons made a check unneeded: **definition** (both sides are one computation, or one names the
other), **inverse round trip**, **repeat** (shown earlier in the notebook or an earlier chapter), and
**property restated** (linearity or length-preservation proved again for each new way of writing the
same rotation). A check stayed when it is the page's result, ties a hand construction to gacalc's own
method for the first time, or has a Lean twin. Those rules are now item 14 of
`tasks/reference/book-notebook-teaching-style.md` and one sentence in `CLAUDE.md`.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22: the 23 borderline checks stay, except
`bootstrap-rotation-from-product.py` (46 lines, close to the check before it) and `dual-3d.py`'s
`product_r` against `swapped_r` (84 lines), which were removed for their length.

## Verification

`tasks/adhoc/prune-unneeded-cancellation-checks/prune.py` made the edit: run once on the unmodified
notebooks it reproduced the final diff byte for byte, and a second run changed nothing. `discover.sh`
then counted 133 calls. `make format`, `make check-notebooks`, `make test` (1407 passed, 3 skipped)
and `make docs` (exit 0, no overfull boxes) all passed.
