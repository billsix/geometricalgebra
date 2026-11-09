# Notebooks — import basis constants instead of fully-qualified `g3.G.e_1`

**Created:** 2026-08-24 · **Completed:** 2026-08-25

The full-class demo notebooks built multivectors from fully qualified constants, e.g.
`2 * g3.G.e_1 + 3 * g3.G.e_2 + 4 * g3.G.e_3 + 5 * g3.G.e_1` in `notebooks/displayg3.py`. The repeated
prefix read worse than the math. Elsewhere the project already used imported names (the README
quick-start's `from gacalc.g2 import G, e_1, e_2`; `notebooks/displayrotations.py` and `displaymv.py`,
which were left untouched). The right imported name depends on whether a notebook wants the full `G`
or the graded value, and on whether it uses one algebra or two: since 2026-08-04 the module-level
`e_1` is the graded `Vector`, while `G.e_1` is the full-class constant.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-24)

1. **`displaygraded.py` uses bare `e_1`/`e_2`**, imported from g2. It imports both g2 and g3 but only
   used g2's constants (measured 2026-08-24), so the bare names are unambiguous. Its **type**
   references stay module-qualified (`g2.Vector` / `g3.Vector`, `g2.Bivector` / `g3.Bivector`,
   `g2.Rotor`, `g3.G`), because those collide across the two algebras.
2. **`book/docs/` was out of scope**; notebooks only.
3. **The full-`G` notebooks use local bare-name aliases** (a direction change, 2026-08-25). After the
   `g2.G.e_1 → G.e_1` cleanup, the maintainer asked for bare names. These notebooks demonstrate the
   full `G` (every value is a `G`), and no bare module-level name exists for the full-`G` constants
   (`from gacalc.g2 import e_1` gives the graded `Vector`), so the setup cell defines `e_1: G = G.e_1`, …
   up to the pseudoscalar, and the body reads `2*e_1 + 3*e_2` (still a `G`). Class methods stay
   `G.`-qualified (`G.from_scalar`, `G.symbolic_multivector`, `G.bases`). Because this contradicts the
   "no local aliases" convention, a **narrow carve-out was added to `CLAUDE.md`** for these two notebooks
   only.

## What changed

- `displayg2.py` / `displayg3.py`: `import gacalc.gN as gN` became `from gacalc.gN import G`, the
  `gN.G.` prefixes and annotations were dropped, and the setup cell gained the aliases above (~25 g2
  sites, ~15 g3 sites).
- **`displaygraded.py` had been committed broken.** An earlier blind `e_1 → g2.e_1` / `e_2 → g2.e_2`
  sed had turned the committed file into invalid attribute access (`g3.Vector.g2.e_1`; there is no
  `Vector.g2`), so the notebook raised `AttributeError` and did not execute (exit 1); a comment was
  mangled too (`from gacalc.g3 import g2.e_1, …`). One guarded reverse substitution,
  `s/g2\.e_1\b/e_1/g` (and `e_2`), both de-mangled `g3.Vector.g2.e_1 → g3.Vector.e_1` and performed
  the intended `g2.e_1 → e_1` cleanup. Type references stayed qualified per decision 1.
- Separately, the git repository was corrupted this session by a crash-truncated tip commit and was
  repaired first; that was unrelated to the sed damage, which was genuinely committed.

## Verification

All three notebooks executed headless (`MPLBACKEND=Agg PYTHONPATH=src python3 notebooks/<nb>.py` →
exit 0; `displaygraded` went from 1 to 0); `ruff check` + `ruff format --check` clean on every touched
file.
