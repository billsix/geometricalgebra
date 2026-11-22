# Spell out basis blades as products of basis vectors (`e_12` → `1 * e_1 * e_2`)

**Status:** done 2026-11-22
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## What this did

The maintainer's request: in a teaching book, `1 * e_1 * e_2` says what the thing is better than the compound
index `e_12`, so write it that way wherever that works, in the plane and in space.

- **Rule (now in `CLAUDE.md`, "Math notation for readers"):** a blade of grade 2 or more that is a *value* is
  written as the product of its basis vectors, `y * e_1 * e_2` (`1 * …` when it stands alone), parenthesized
  after a vector, `a * (e_1 * e_2)`. The bold `\mathbf{e}_{12}` stays where it names the blade: where a page
  introduces it, as a plane's name or a subscript, in a figure label, and where the text points at gacalc's
  printed output. The plane `e_3 * e_1` is written as that product, because gacalc's `e_13` is its negative.
- **Book pages and notebook Markdown:** 11 book pages and 14 notebooks rewritten (the two reference cards
  already carry the form, from `tasks/archive/2026/11/22/cheat-sheet-gn-section-and-explicit-names.md`). Several
  identities now show their own reason: `e_1 * (e_1 * e_2) = e_2`, `(e_1 * e_2) * (e_1 * e_2) = -1`.
- **Code (class C-same):** 11 lines use `(e_1 * e_2)` or `(Vector.e_1 * Vector.e_2)` in place of the constant
  `e_12` / `Bivector.e_12` in `bootstrap-product.py`, `defining-g2.py`, `dual.py`, `geometric-product.py` and
  `product-from-projection.py`; all passed `ty` and pyright, so none moved to C-typed.
  `defining-g2.py`'s `B: Bivector = 2 * e_12`, the plane arguments of `projection-rejection-3d.py`, and the other
  `C-typed` lines keep the constant (decision 2).
- **The `e_31` note** is written `e_3 * e_1 = -e_1 * e_3` in `book/docs/projection-rejection-3d.rst`,
  `notebooks/projection-rejection-3d.py` and `book/figures/epix/proj3d_e31.py`.
- **Kept on purpose** (103 matches remain, each a naming line, plane name, figure label or file/field name): the
  product-rule lists that introduce `e_1 * e_2 = e_12`, "call it", the lists of blades, `proof-cross`,
  `projection-rejection-3d`, `proof-projection-3d`, `reflection-3d`, `frame-qr-3d`, `displaygraded` and
  `displayrotations`, and the lines of `displaymv.py` that name gacalc's output.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22: (1) a blade used as a plane's name or a subscript keeps
`\mathbf{e}_{12}`, except the `e_31` / `e_13` note; (2) `C-typed` code keeps the `e_12` constant. Rejected:
`1 * (e_1 ^ e_2)` (uses the wedge before it is taught) and retyping `Vector * Vector` in the generator.

## Verification

`tasks/adhoc/spell-out-basis-blades-as-vector-products/spell_out.py` made the edit; run once on the unmodified
files it reproduced the final diff, followed by `python tools/check_notebook_prose_width.py --fix` and `ruff`
(which removed two now-unused `e_12` imports and reformatted three notebooks). `make format`,
`make check-notebooks`, `make test` (1407 passed, 3 skipped) and `make docs` (exit 0, no overfull boxes)
passed.
