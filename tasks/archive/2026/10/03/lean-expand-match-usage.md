# Sweep the Lean proofs for additional `match` / total-dispatch opportunities

**Completed:** 2026-10-03 (William Emerison Six <billsix@gmail.com>) — a no-op sweep.

The maintainer liked the total `match` in `rVectorPart` and asked whether more of
`proofs/GacalcProofs/*.lean` could use `match`. A sweep for term-level `if`/`ite`/`dite`/`cond` and
for non-`match` case-dispatch found **nothing to convert**: every apparent `if … then` was inside a
docstring, the only `match` blocks were the two `rVectorPart` defs (`GradeProjection.lean`, already
total via `| _ => …`), and no other definition enumerated cases in a convertible form. The corpus
already used `match` wherever structural dispatch occurs and had no `if`/`elif` chains, so no code
changed. The forward-looking preference was recorded in gacalc's `CLAUDE.md` ("Prefer `match` / total
dispatch for structural case analysis", applying to the Lean proofs too). Tactic-mode case splits
(`rcases`/`cases`) were deliberately left as-is — converting them to term-mode `match` is a different,
riskier refactor and was not requested.
