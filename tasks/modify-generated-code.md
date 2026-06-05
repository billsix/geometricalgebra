# Sort generated product terms by grade

**Status:** in-progress
**Started:** 2026-06-04

## Goal

Investigate whether the generated closed-form expressions in `g1/g2/g3.py` (and any future `gN`)
can have the additive terms within each component ordered **by grade** — scalars first, then
vectors, then bivectors, then trivectors, etc. — instead of the current sympy ordering, which is
roughly lexicographic by symbol name and reads oddly (e.g. `e_12` sorts before `e_2`). For example
the `scalar` component currently generates:

```python
scalar=(
    self.e_1 * rhs.e_1
    - self.e_12 * rhs.e_12
    + self.e_2 * rhs.e_2
    + self.scalar * rhs.scalar
),
```

and we'd prefer grade-ordered:

```python
scalar=(
    self.scalar * rhs.scalar      # grade 0
    + self.e_1 * rhs.e_1          # grade 1
    + self.e_2 * rhs.e_2
    - self.e_12 * rhs.e_12        # grade 2
),
```

This is purely a readability/presentation change to the generated source — it must not alter the
computed values (the conformance suite must still pass).

## Plan

- [ ] Locate the term ordering: `format_assignment` in `tools/gen_specialized.py` uses
      `expr.as_ordered_terms()`. That's where the per-term order is decided.
- [ ] Decide the sort key. Each term is a product of one `self.<field>` and one `rhs.<field>`
      (a cse temp is possible but the geometric/inner/outer products currently produce none).
      Candidate key: `(grade(self_field), self_field_indices, grade(rhs_field), rhs_field_indices)`
      — i.e. order by the grade of the left operand's blade, then index, then the right. Confirm
      this gives the desired scalar→vector→bivector grouping on real output.
- [ ] Parse each term back to its component fields. Options: regex the rendered string for
      `self.<name>` / `rhs.<name>` and map name→grade via `field_name`/blade length; or work from
      the sympy term's free symbols (`a_<field>`, `b_<field>`) before rendering.
- [ ] Apply the ordering in `format_assignment` (replace/augment `as_ordered_terms()` with a sorted
      list). Keep the existing sign handling (`- term` vs `+ term`) and the inline-vs-wrapped logic.
- [ ] Regenerate `g1/g2/g3.py`, run `ruff` + `ty` + the full suite (118 tests) — must stay green.
- [ ] Eyeball the diff to confirm the new ordering reads as intended across all components.

## Notes / decisions

- Affects only generated output / the generator; no hand-written source.
- The geometric/inner/outer products produce no `cse` temporaries today, so every term is a simple
  `self.X * rhs.Y`. If that ever changes, the sort key needs a story for temp-valued terms (e.g.
  sort temps last, or by the min grade of their inputs).
- Single-term and constant (e.g. identically-zero) components are unaffected.

## Open questions

- ~~Left grade only vs composite?~~ → **Composite** (decided 2026-06-04): sort key is
  `(grade(left), left_indices, grade(right), right_indices)` — left operand's grade first, then its
  blade indices, then the right operand's grade and indices.
- Within a grade, order by blade index ascending (e.g. `e_1` before `e_2`, `e_12` before `e_13`)?
  (Implied by the composite key above; confirm on real output.)
- Should the same ordering also apply to the `_geometric_product` output (it uses the same
  `format_assignment`, so it would come along for free — presumably desired)?

**Status: queued** — implementation deferred per request; decision above is settled.
