# Cite Lagrange's identity everywhere it is used or referenced

**Status:** partly done — `MultiVectorBase.abs_sin`'s docstring and `proofs/GacalcProofs/Lagrange.lean`
already carry the name + link (2026-10-04 audit); the two `display*` notebooks remain — needs go-ahead
for the rest (filed 2026-09-27)
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-09-27 **Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)

## BLUF

Add an explicit reference/citation to **Lagrange's identity** — `‖a∧b‖² = ‖a‖²‖b‖² − (a·b)²`
(equivalently `‖a‖²‖b‖² = (a·b)² + ‖a∧b‖²`; in 3D `‖a∧b‖ = ‖a×b‖`) — with the source link
<https://en.wikipedia.org/wiki/Lagrange%27s_identity>, everywhere in this codebase where the identity
is used or referenced. The author was unaware the identity had a name/standard reference; "done" =
every site that uses or names it carries the name **and** the link, and the audit of "used by another
name" sites (Gram determinant, area-from-wedge) is complete with each either cited or explicitly
ruled out.

## Context — read first

- The identity is `‖a∧b‖² = ‖a‖²‖b‖² − (a·b)²`. In 𝒢ₙ it is what makes `‖a∧b‖ = ‖a‖‖b‖sinθ` and
  what connects the wedge magnitude to the Gram determinant `det[[a·a, a·b],[a·b, b·b]]`. Reference:
  <https://en.wikipedia.org/wiki/Lagrange%27s_identity>.
- **Sites that already name it** (re-grepped `git grep -niI lagrange` 2026-10-04, excluding
  `tasks/archive/`):
  - **DONE** — carry the name **and** the link already: the `MultiVectorBase.abs_sin` docstring in
    `src/gacalc/base.py`; `proofs/GacalcProofs/Lagrange.lean` (module header; theorems `lagrange_2d` /
    `lagrange_3d`).
  - **REMAINING** (name it, no link) — the actual work left:
    - `notebooks/displayg2.py` — the "**The Lagrange step**" markdown cell + the `lagrange_residual`
      computation and `assert lagrange_residual == 0`.
    - `notebooks/displayg3.py` — the "the **Lagrange identity** is …" cell + its "Lagrange step"
      residual cell + assert.
  - Lean / test / book sites that name it and can point at `Lagrange.lean` instead of repeating the
    link: `proofs/GacalcProofs/Trig.lean` (`lagrange_property_coord` / `lagrange_property`, 𝒢₂ and 𝒢₃),
    `Measures.lean` (`normSq_wedge_eq_lagrange`), `RotateComponents.lean` (module header),
    `proofs/README.md`, `tests/test_signed_sine.py` (module docstring + the signed-sine identity
    comment), `tests/test_multivector.py` (the `cos²θ + sin²θ == 1` comment),
    `book/docs/notebooks/levels-of-abstraction.py` (the two `cosine² + sine² = 1` cells), `CLAUDE.md`
    (the Lean leaves paragraph naming `lagrange_2d/3d`), `tasks/reference/lean-ga-proof-architecture.md`,
    `lean-for-gacalc.md`, `reduction-to-standard-position.md`.
  - `tasks/use-bivector-from-vectors-and-i-in-notebooks-and-tests.md` (its notebook-scope bullets) — refers to the
    "Lagrange-identity" cells; update the pointer if the cells change, but this is a *task* doc, so a
    citation there is optional (lower priority than the notebooks).
- **Candidate sites that use it by another name** — audit each; add the citation where the identity is
  actually the thing being invoked, or note "not the Lagrange identity" if it's unrelated:
  - `src/gacalc/measure.py` — `area`/`volume`/`content`: `content = |wedge| = √det(Gram)` is the
    Lagrange/Gram connection (see `tasks/reference/content-area-volume.md`).
  - `src/gacalc/base.py`, `src/gacalc/vectorcalc.py` — magnitude-of-wedge / cross-product-magnitude
    paths.
  - `tasks/reference/content-area-volume.md` (Gram determinant), `dot-wedge-projection-rejection.md`
    (the parallel/perpendicular decomposition of the geometric product), `unit-bivector-and-rotors.md`
    — these state the math the identity underlies; a "(this is Lagrange's identity — <link>)" aside is
    appropriate where the wedge-magnitude / Gram-determinant relation appears.
  - `src/gacalc/g2.py`, `g3.py` are **generated** (gitignored) — do **not** hand-edit; if a generated
    docstring should cite the identity, change `tools/gen_specialized.py` (or its `CUSTOM_METHOD_DOCS`)
    and regenerate. (Most likely no generated-code change is needed — the identity lives in the
    notebooks and reference docs, not the generated methods. Confirm during the audit.)
- **Convention reminders** for whoever does the work: `tasks/reference/*` docs are the durable home
  for the "why"; keep `CLAUDE.md` lean. Per the repo's "never cite an artifact you have not verified"
  rule, re-grep the sites above before editing (the inventory drifts). This is a doc/citation change
  only — no behavior changes, so `make test` should be unaffected; still run `make format` and, if any
  notebook markdown changed, confirm the notebooks still execute.

## Goal

Make Lagrange's identity discoverable and properly attributed throughout gacalc: anywhere the code,
notebooks, or reference docs invoke or name it, add the name "Lagrange's identity" and the reference
link, so a reader (and the author, who did not know its name) can find the standard source. Include an
audit pass over the "used by another name" sites so the coverage is complete, not just the two
notebooks that already say "Lagrange."

## Plan

- [x] `MultiVectorBase.abs_sin` docstring + `proofs/GacalcProofs/Lagrange.lean` carry the name + link
      (shipped with the sine / Lean work; confirmed 2026-10-04).
- [ ] Re-run `git grep -niI lagrange` and confirm the sites above (the inventory drifts).
- [ ] Add the name + link to `notebooks/displayg2.py` and `displayg3.py` Lagrange cells.
- [ ] Audit the "by another name" candidates (`measure.py`, `base.py`, `vectorcalc.py`, and the three
      reference docs); cite where the identity is invoked, or record "not Lagrange" where it isn't.
- [ ] Decide whether any *generated* docstring should cite it → if so, edit `tools/gen_specialized.py`
      and regenerate (never hand-edit `g*.py`); otherwise note "no generated change needed."
- [ ] `make format`; if notebook markdown changed, re-execute the notebooks; stage by path.

## Notes / decisions

- Filed 2026-09-27 at the author's request after discovering the identity has a standard name/source;
  the two `display*` notebooks already *use* the identity by name but cite no source.
- 2026-10-04 audit: the inventory above was refreshed; `abs_sin` and `Lagrange.lean` turned out to
  already cite the name + link, so the remaining work is the two notebooks + the by-another-name audit.

## Open questions

None yet — the scope is "cite it wherever it appears." One judgment call is folded into the plan:
whether any generated docstring (not just notebooks/reference docs) should carry the citation; the
audit answers it.
