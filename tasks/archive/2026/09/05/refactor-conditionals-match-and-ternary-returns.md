# Refactor conditionals: `match` / ternary-return / dedup / phase-extraction — rules + a project sweep

**Created:** 2026-09-05 · **Completed:** 2026-09-05 (William Emerison Six <billsix@gmail.com>)

Control-flow readability was improved in `tools/gen_specialized.py` (the pilot); a small set of
when-to-apply rules was derived from doing it, codified in `CLAUDE.md`, and applied project-wide at
discretion, never churning code that was already clear. The rules and worked examples live in
`tasks/reference/conditional-refactoring-rules.md`; `CLAUDE.md` carries the lean Rules A–E bullet.
This refined, not replaced, the existing "Prefer expressions", "Prefer `match` + `case _`" and "What
earns an extraction" conventions.

## The rules (summary)

- **A — ternary `return X if cond else Y`** for exactly two outcomes whose branches are single
  expressions and read at least as clearly; never collapse a top-of-function early-exit guard.
- **B — dedup before restructuring:** if branches are byte-identical (often a vestigial split kept
  apart only by comments), merge them and delete the dead discriminating test.
- **C — `match` earns its keep by structural work in the pattern** (type dispatch, destructuring that
  binds names, literal dispatch). The anti-pattern is narrower than "has a guard": every arm
  `case _ if <bool>`. Test: strip the guards — do the patterns still dispatch?
- **D — make a prefix/boolean check matchable** by first extracting a literal discriminant (e.g.
  `kind, _, label = name.partition("_")`), hoisting duplicated setup, with a `case _: raise` that
  documents the invariant.
- **E — extract long dispatch branch bodies into named nested functions** (≥ 3 arms and bodies too
  long to see the conditions on one screen): a long ladder interleaves the table of contents with the
  chapters. Nest, don't hoist (the bodies close over locals); two short branches stay inline.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-09-05)

1. **Case 3 (`generate_graded_type`'s per-type special-case chain) — keep the extraction, in the
   pure-return form.** The maintainer was shown the before/after prototype and approved it ("I love
   it"): each phase (`bivector_extras` / `rotor_extras` / `odd3_extras` / `vector_extras`) returns
   `list[ast.stmt]`, read-only over the enclosing scope, dispatched by `match spec.name:` with
   `body += …_extras()`. A mutate-via-closure prototype was rejected (a hidden side effect on a shared
   list). This confirmed Rule E.
2. **Worked examples go in a reference note**, not inline in `CLAUDE.md`.
3. **Line length is `make format`'s job, not a design input** (settled during the completion pass and
   recorded in `CLAUDE.md` and Rule A's text), which unblocked the ternaries first left only for
   exceeding 88 columns.

## What changed

- **Case 1** (`term_grade_key`'s `a_`/`b_` operand-symbol dispatch): Rules D + B — hoisted the
  duplicated `blade`, `match kind:` on the `partition("_")` discriminant with `case _: raise`.
- **Case 2** (`result_block_stmts`' `via_var`/`owner`/`else` chain): Rule B — merged the two
  byte-identical arms, deleting the dead `owner … and cast is cast_self` test; a `match` would have
  been worse for a `None` check. The sibling in `unary_stmt` was left: a live cast/no-cast distinction.
- **Rule A** applied to `blade_label` (its motivating example) and the inverse `blade_of_label`.
- **Case 3** as decided above.
- The rest of `gen_specialized.py`/`astbuild.py` was catalogued and left: guard-continues, error
  early-exits, comprehension filters, ternary conditions, and two-branch value builds that read fine.
- **Project-wide first pass** over hand-written `src/` + `tools/`: one structural win —
  `transforms.to_matrix`'s `backend` string dispatch became a `match` with `case _: raise` (Rule C).
  Left alone: `base.project`'s inner `fn` (a boolean-guard 3-way, the Rule-C anti-pattern, and it maps
  to Hestenes 2.9a/b/c), `transforms.rotor_for`, `functions.steps` (a generator), the `nbplotutils`
  x_range. No candidates in `tests/` or `notebooks/`.
- **Completion pass:** the first pass had only spot-checked Rule A, so an AST scan swept every
  guard-return pair in `src/` + `tools/`. After decision 3, about nine sites became wrapped ternaries
  (`base.blade_latex`, `base.__truediv__`, `base.magnitude`, `base.add_parens_or_dont`,
  `frame.is_frame`, `gen_specialized.i_classmethod`, `result_value`, `unary_stmt`,
  `astbuild.visit_Name`), and `base._coerce` became a 3-way type-dispatch `match` (Rule C). Confirmed
  leave-alones: `ComposableFunction.at` (a 3-outcome cascade) and `astbuild.cast_coef` (a 3-guard
  cascade).
- A separate type-annotation audit was spawned: `tasks/archive/2026/09/09/add-more-type-annotations.md`.

## Verification

A generator refactor is behaviour-preserving by definition, so the hard gate was a materialized
baseline of the generated `g1/g2/g3.py` diffed after every step: byte-identical throughout, plus
`make check-generated`. The real containerized gate (`make test` + `make format`, nested) was green:
449 tests, ruff, ty (including `ty check tools`).
