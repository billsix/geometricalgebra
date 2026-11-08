# `proofs/check.sh`: add the axioms gate it claims to have

**Status:** proposed — needs go-ahead (approved in session 2026-11-08; in progress)
**Priority:** 2
**Difficulty:** 3
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §7.1 (also §1.1, §2.1)
**Related:** `tasks/lean-proofs-remove-extras.md` (P6). Its plan step 2 adds `--wfail` to the same
`proofs/check.sh`. That task is kept separate (decided 2026-11-08): it is an optional proof cleanup,
waiting on its own open questions 1–2.

## BLUF

`proofs/check.sh` (run by `make lean` and by CI's `lean.yml` on tags) says its "axioms grep" is the
reliable gate against `sorryAx`. In fact it only greps the sources for the words `sorry`/`admit`.
Done means:

- `check.sh` runs a real axioms check: every `GacalcProofs.*` declaration may rest only on
  `propext`, `Classical.choice` and `Quot.sound`;
- a probe proves the check catches a `sorry` and a user `axiom`;
- every place that describes the gate says what it now does.

## Context

**What the gate does today.** `proofs/check.sh` runs `lake build`, then
`grep -rnE '\b(sorry|admit)\b'` over the sources. Its header (:4-7) calls this "the axioms grep …
the reliable, version-stable gate", but no axioms are checked. The grep misses:

- a user `axiom`;
- `native_decide` (which uses `Lean.ofReduceBool`);
- `implemented_by`;
- any hole that doesn't spell the word `sorry`.

None of these is in the sources today; the review's reader ran `#print axioms` on all 628 theorems.

**Why the grep isn't enough.** `lake build` only warns on `sorry` and still exits 0.

**Places that describe the gate:**

- `proofs/check.sh`'s header and its completeness-gate comment;
- `.github/workflows/lean.yml`'s comment ("the sorryAx axioms gate");
- `make lean`'s help text ("nonzero if any proof is incomplete (sorryAx)");
- `tasks/reference/lean-for-gacalc.md:207-211`, which describes an axioms gate that auto-discovers
  theorems;
- `tasks/reference/lean-ga-proof-architecture.md:804`, which describes the grep correctly.

**Toolchain:** Lean `v4.34.1` with Mathlib `v4.34.1` (`proofs/lean-toolchain`, `proofs/lakefile.toml`).
`lake` is on the sandbox PATH, and `proofs/.lake` is already built.

## Plan

- [ ] Add `proofs/scripts/CheckAxioms.lean`. It imports `GacalcProofs`, walks every non-internal
  declaration from a `GacalcProofs.*` module, and calls `Lean.collectAxioms` on each. It logs an
  error naming any declaration with an axiom outside the three, so `lake env lean` exits nonzero.
  It lives outside the `GacalcProofs` library, so `lake build` doesn't build it.
- [ ] Run it from `check.sh` after `lake build`, accumulating its status like the other steps. Keep
  the source grep as a fast first check, and correct the header and comments.
- [ ] Prove it: a temporary probe module with an `axiom` and a `sorry` must fail the gate. Revert
  the probe.
- [ ] Correct `lean.yml`'s comment, `make lean`'s help, and the two reference docs.
- [ ] Gate: `bash proofs/check.sh` (exit 0).

## Open questions

None.
