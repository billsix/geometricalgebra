# Notebooks — import basis constants instead of fully-qualified `g3.G.e_1`

**Status:** DONE 2026-08-25 (William Emerison Six <billsix@gmail.com>) — see Outcome below.
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-08-24 (William Emerison Six <billsix@gmail.com>)

## Outcome (2026-08-25)

Done, verified, staged. Two things diverged from the plan below:

1. **`displaygraded.py` was committed-broken and got de-mangled as part of this.** A prior
   blind `e_1 → g2.e_1` / `e_2 → g2.e_2` sed had corrupted the *committed* file into invalid
   attribute access — `g3.Vector.g2.e_1` (there is no `Vector.g2`), which raised
   `AttributeError` at runtime, so the notebook **did not execute** (exit 1). A comment was
   mangled too (`from gacalc.g3 import g2.e_1, …`). One **guarded** reverse substitution,
   `s/g2\.e_1\b/e_1/g` (+ `e_2`), did **both** jobs at once: it de-mangled `g3.Vector.g2.e_1
   → g3.Vector.e_1` **and** performed the task's intended `g2.e_1 → e_1` bare-constant
   cleanup. Type refs (`g2.Vector`/`g3.Vector`/…) stayed qualified per Decision 1. The
   notebook now executes (exit 0). (The git repo was *also* corrupted this session — a
   separate crash-truncated tip commit — and was repaired first; unrelated to the sed
   mangling, which was genuinely committed.)

2. **Direction change for the full-`G` notebooks (`displayg2.py` / `displayg3.py`): local
   bare-name aliases, not `G.e_1` at every site.** After the `g2.G.e_1 → G.e_1` cleanup, Bill
   asked for bare names. These notebooks demonstrate the **full `G`** (every value is a `G`),
   and there is no bare module-level name for the full-`G` constants (`from gacalc.g2 import
   e_1` gives the *graded* `Vector`). So the setup cell now defines `e_1: G = G.e_1`, … (up
   to the pseudoscalar) and the body reads `2*e_1 + 3*e_2` (still a `G`). Class **methods**
   stay `G.`-qualified (`G.from_scalar`, `G.symbolic_multivector`, `G.bases`). This aliasing
   contradicts the "no local aliases for values that have a direct name" convention, so a
   **narrow carve-out was added to `CLAUDE.md`** (that convention section) sanctioning it for
   these two notebooks only.

**Verification:** all three notebooks execute headless (`MPLBACKEND=Agg PYTHONPATH=src python3
notebooks/<nb>.py` → exit 0; `displaygraded` went 1 → 0); `ruff check` + `ruff format --check`
clean on all touched files. **Staged:** `notebooks/displayg2.py`, `displayg3.py`,
`displaygraded.py`, `CLAUDE.md`.

## Context

The full-class demo notebooks build multivectors out of fully module-and-class-qualified
basis constants, e.g. (`notebooks/displayg3.py:91`):

```python
2 * g3.G.e_1 + 3 * g3.G.e_2 + 4 * g3.G.e_3 + 5 * g3.G.e_1
```

The repeated `g3.G.` prefix is noise — it reads worse than the math it encodes. The
project already prefers the imported form everywhere else: the README quick-start does
`from gacalc.g2 import G, e_1, e_2` then `3 * e_1 + 4 * e_2`, and
`notebooks/displayrotations.py` / `displaymv.py` already `from gacalc.gn import e_1, e_2, …`.
The goal is to make the demo notebooks read the same way.

**Nuance — this is not a blind `g3.G.` → `G.` sed.** The right imported name depends on
whether the notebook wants the **full `G`** or the **graded** value, and whether it uses
**one algebra or two** (post-2026-08-04, module-level `e_1` is the *graded* `Vector`, while
`G.e_1` is the full-class constant — see `README.md` "Import just the algebra you need").

## Scope (measured 2026-08-24)

- **`notebooks/displayg3.py`** — full-class notebook; `import gacalc.g3 as g3`, uses
  `g3.G.e_1` / `g3.G.e_123` / `g3.G.from_scalar(...)` and `g3.G` type annotations
  throughout (~15 sites).
- **`notebooks/displayg2.py`** — same shape for `g2.G.*` (~25 sites, incl.
  `translate(b=5 * g2.G.e_1)` and `g2.G` annotations).
- **`notebooks/displaygraded.py`** — imports **both** `g2` and `g3`, but (measured
  2026-08-24) only ever uses g2's **constants** (`g2.e_1`, `g2.e_2` — no `g3.e_1`/`g3.e_2`
  anywhere). So `from gacalc.g2 import e_1, e_2` is **unambiguous** and the constants become
  bare `e_1`/`e_2`. Its **types**, however, are used for *both* algebras (`g2.Vector` and
  `g3.Vector`, `g2.Bivector` and `g3.Bivector`, `g2.Rotor`, `g3.G`) — those genuinely
  collide, so the **type** references stay module-qualified (`g2.Vector` / `g3.Vector`).
  That qualification is a necessary type-disambiguation, not the `g3.G.e_1` verbosity being
  removed here.
- Already fine (do not touch): `displayrotations.py`, `displaymv.py` (both already import
  the names).

## Plan

1. **`displayg3.py`:** replace `import gacalc.g3 as g3` with `from gacalc.g3 import G`
   (and any other `g3.`-qualified names the file uses — verify with
   `grep -n 'g3\.' notebooks/displayg3.py` that only `g3.G` appears; add anything else to
   the import). Rewrite `g3.G.e_1` → `G.e_1`, `g3.G` annotations → `G`,
   `g3.G.from_scalar` → `G.from_scalar`.
2. **`displayg2.py`:** same, for `g2`.
3. **`displaygraded.py`:** add `from gacalc.g2 import e_1, e_2` and rewrite `g2.e_1` →
   `e_1`, `g2.e_2` → `e_2`. **Leave the type references module-qualified** (`g2.Vector` /
   `g3.Vector`, etc.) — they collide across the two algebras (see Scope).
4. **Verify the notebooks still execute** — run each through jupytext/pytest the way the
   suite does, and confirm no `g2.`/`g3.` name is left dangling (it would `NameError` on
   execution). Re-run `make format`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-24)

1. **`displaygraded.py` uses bare `e_1`/`e_2`** (imported from g2), not module-qualified —
   the constants don't collide (only g2's are used). Type references stay qualified because
   they *do* collide across g2/g3.
2. **Out of scope: `book/docs/`.** This task is notebooks only.
