# Sweep the Lean proofs for additional `match` / total-dispatch opportunities

**Status:** done (no-op). **Priority:** 7. **Difficulty:** 3.
**Completed:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).

The maintainer liked the total `match` in `rVectorPart` and asked whether more of
`proofs/GacalcProofs/*.lean` could use `match`. A sweep for term-level `if`/`ite`/`dite`/`cond` and
for non-`match` case-dispatch found **nothing to convert**: every apparent `if … then` was inside a
docstring, the only `match` blocks were the two `rVectorPart` defs (`GradeProjection.lean`, already
total via `| _ => …`), and no other definition enumerated cases in a convertible form. The corpus
already uses `match` wherever structural dispatch occurs and has no `if`/`elif` chains, so no code
changed. The forward-looking preference now lives in gacalc's `CLAUDE.md` ("Prefer `match` / total
dispatch for structural case analysis", applying to the Lean proofs too). Tactic-mode case splits
(`rcases`/`cases`) were deliberately left as-is — converting them to term-mode `match` is a different,
riskier refactor and was not requested.
