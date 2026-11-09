# Book: the notation sweep

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.4
**Decision:** the basis vectors are written plain, `e_1`, `e_2`, `e_3`, as `relative-graph-paper`
introduces them and as the code names them. (The reviewer's recommendation, taken by William Emerison
Six <billsix@gmail.com>, 2026-11-09; recorded in `tasks/reference/book-outline.md`.)

## What changed

Every §3.4 case, per `CLAUDE.md` › "Math notation for readers":

- **Juxtaposition → an explicit `*`:**
  - `geometric-product`: `e_1 * e_{12} = e_2`, `e_2 * e_{12} = -e_1`, the sandwich
    `R * \vec{v} * \tilde{R}`;
  - `proof-rotate-from-a-to-b`: `|\vec{a}| * e_1`;
  - `proof-projection`: `|\vec{b}| * e_1`, `a'_1 * e_1`, and the closing `\vec{b} * \vec{a}`;
  - `proof-cross`: `|\vec{a}| * |\vec{b}| * \sin(\theta)`, `m * b'_2`, `|\vec{a}| * e_1`; and "the
    `\vec{e}_1\vec{e}_2` plane" → "the `e_{12}` plane" (likewise `e_{23}`);
  - the notebooks: `levels-of-abstraction`'s markdown and comments (`⟨a * b⟩₀`,
    `a * b = a·b + a∧b`, `a_1 * b_1 + a_2 * b_2`), and the `geometric-product` comment.
- **`\cdot` as multiplication:** `geometric-product`'s cracker example is `12 * 6^{-1} * 5`.
- **The unnamed angle:** `proof-cross`'s `\cos(\theta)^2 + \sin(\theta)^2 = 1`.
- **Primes:** `b'_1`, `b'_2`, `b'_3` in `proof-cross.rst` and `notebooks/proof-cross.py`.
- **The basis spelling:** every `\vec{e}_i` / `\vec{e_i}` → `e_i` across the pages.
- **The `sp2` alt text:** "the angle theta" (the figure and the prose use θ).
- **`vector-addition`:** `translate(b=b)` / `translate(b=-b)`, keyword as the page says, and
  `\text{translate}(b = \vec{b})(\vec{v})` in the formula.
- **`README.md`:** `3 * e_1 + 4 * e_2` and `3 * G.e_1 + 4 * G.e_2` spaced.
- **Kept on purpose:** the two sandwich spellings in the notebooks. `R * v * R~` is for a unit rotor
  (`geometric-product.py`) and `R * v * R^-1` for a non-unit versor (`rotation-from-vectors.py`);
  each is correct for its own object.

**Where the edits landed.** Most of the page edits sit in files committed with
`tasks/archive/2026/11/09/book-restructure-parts.md` and
`tasks/archive/2026/11/09/book-cross-references-and-author-notes.md`, which changed the same lines.
This commit carries `vector-addition.rst`, the `geometric-product` and `proof-cross` notebooks, and
the README.

## Verification

- A grep for the §3.4 patterns (`\vec{e}_`, `\vec{e_i}`, `\lvert`, `\cdot 6`, `\cos^2`, `b_i'`,
  `\vec{a}\vec{b}`, `\,\vec`) over the pages and notebooks finds nothing.
- The touched notebooks run.
- `ruff` is clean.
