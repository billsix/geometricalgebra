# Investigate: generate percent-formatted Python proof notebooks from Lean proofs

**Part of:** the Lean-proofs program (umbrella archived: `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`)
**Related:** the codegen conventions (`~/.claude/reference/codegen-conventions.md` — prefer structured
output over string concatenation; build a parity harness); the existing demo notebooks
(`notebooks/displayg2.py`/`displayg3.py`, jupytext percent format).

**Status:** proposed — needs go-ahead (filed 2026-09-29, William Emerison Six <billsix@gmail.com>)
**Priority:** 7
**Difficulty:** 7

## BLUF

Investigate whether we can **auto-generate a percent-formatted (jupytext) Python notebook that shows a
proof in normal, college-level math form, driven by / kept honest by the corresponding Lean proof** —
e.g. render "𝒢₂ multiplication is associative" or the distributive law as a readable
symbolic expansion, generated from the Lean development rather than hand-written. The maintainer
already has a notebook that shows the *distribution* nicely and wants that style (a) updated and (b)
**automated from the Lean proof**. "Done" for this investigation = a clear go/no-go with a worked
prototype for one law (associativity or distributivity of `G2.mul`), plus a written finding on how
much of Lean's reasoning can actually be surfaced.

## Context / the real question to answer first

- **Find the existing notebook** the maintainer means (likely `notebooks/displayg2.py` or a
  distributivity cell) and use its *presentation* as the target style — a college-level symbolic
  expansion, not Lean tactic jargon.
- **The crux — can Lean "trace all its steps"?** Be honest here: a `ring`/`ext <;> ring` proof (how
  `G2`/`G3` associativity and distributivity are proved) is **opaque** — `ring` produces a single
  reflection proof, not a human-readable chain of rewrites, so there is *no* natural "trace of
  deductions" to transcribe. Options to explore, roughly in increasing promise:
  1. **Lean tracing options** (`set_option trace.Meta.Tactic.ring`, `trace.Debug`, proof-term
     `#print`) — likely too low-level / not college-math-shaped. Investigate but expect it insufficient.
  2. **Generate the *algebraic expansion* symbolically (sympy/Python), and use Lean only to
     *certify* the identity.** The notebook shows the human-readable step-by-step distribution
     (exactly what the maintainer likes), generated from the *definitions* (the same `mul` table the
     Lean `G2.mul` encodes); Lean's role is the machine-check that the end identity holds. This
     matches gacalc's existing "show the work symbolically" notebooks and the codegen conventions.
  3. **A structured proof format:** write the Lean proof in a `calc`/step style (not `ring`) so each
     step is a named rewrite, then extract those steps and pretty-print them to LaTeX/Python. More
     faithful "from the Lean proof," but requires re-authoring proofs in an explicit style and a
     Lean→notebook extractor.
- **Decision to get from the maintainer:** is the goal "the notebook is *checked* by Lean" (option 2,
  pragmatic) or "the notebook is literally *transcribed from* the Lean proof's steps" (option 3,
  faithful but heavy)? These are very different projects.

## Plan (once greenlit)

- [ ] Locate + review the maintainer's existing distribution notebook; capture the target style.
- [ ] Spike each option on ONE law (start with `G2` left-distributivity `a(b+c)=ab+ac`, then
      associativity): what can Lean actually emit; what reads well at college level.
- [ ] Prototype the most promising (likely option 2: sympy expansion in a percent notebook + a Lean
      certificate cell / cross-check), following the codegen conventions (structured output, parity
      harness, determinism).
- [ ] Write the go/no-go finding into a reference doc; if go, scaffold the generator task.

## Open questions

1. **Faithfulness vs. pragmatism (the key decision):** notebook *checked by* Lean (symbolic expansion
    in Python, Lean certifies the identity), or notebook *transcribed from* the Lean proof's own steps
    (needs `calc`-style proofs + an extractor)? (Recommend starting with the checked-by-Lean form — it
    reuses the existing notebook style and is far cheaper — and only pursuing transcription if the
    maintainer specifically wants the Lean steps themselves shown.)
2. Which law is the best first prototype — distributivity (the maintainer already likes that notebook)
    or associativity (the motivating example)? (Recommend distributivity: an existing target to match.)
