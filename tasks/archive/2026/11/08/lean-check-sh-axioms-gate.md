# `proofs/check.sh`: add the axioms gate it claims to have

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §7.1 (also §1.1, §2.1)
**Related:** `tasks/lean-proofs-remove-extras.md` (P6). Its plan adds `--wfail` to the same script.
It was kept separate on purpose (decided 2026-11-08): it is an optional proof cleanup, waiting on its
own open questions.

## What was wrong

`proofs/check.sh` (run by `make lean` and by CI's `lean.yml` on `v*` tags) said its "axioms grep"
was "the reliable, version-stable gate" against `sorryAx`. In fact it only grepped the sources for
`sorry`/`admit`. That misses:

- a user `axiom`;
- `native_decide` (`Lean.ofReduceBool`);
- `implemented_by`;
- any hole not spelled `sorry`.

`lake build` alone only warns on `sorry`: a probe build with a `sorry` theorem completed
successfully.

`tasks/reference/lean-for-gacalc.md` described an auto-discovering axioms gate that didn't exist.
`lean.yml`'s comment and `make lean`'s help text repeated the claim.

## What changed

- **`proofs/scripts/CheckAxioms.lean`** (new). It imports `GacalcProofs` and walks every
  non-internal declaration from a `GacalcProofs.*` module. For each, `Lean.collectAxioms` must
  return only `propext`, `Classical.choice` and `Quot.sound`; any other axiom is logged as an error
  naming the declaration, so `lake env lean` exits nonzero. It sits outside the `GacalcProofs`
  library, so `lake build` doesn't build it.
- **`proofs/check.sh`** runs it after `lake build` and the existing source grep, accumulating its
  status like the other steps. The grep is kept as a quick first check. The header and comments now
  describe what each step catches.
- **The other descriptions** now match what the script does:
  - `.github/workflows/lean.yml`'s comment;
  - `make lean`'s help text;
  - the `make lean` bullet in `CLAUDE.md`;
  - `proofs/README.md`;
  - `tasks/reference/lean-for-gacalc.md` (the "Gate" bullet);
  - `tasks/reference/lean-ga-proof-architecture.md` (the completeness-gate bullet).

## Verification

- **Negative probe:** a temporary `GacalcProofs/ZzAxiomProbe.lean` with `axiom probeAxiom : 1 = 2`,
  a theorem using it and a `sorry` theorem, imported from the root. The gate exited 1 and named all
  three: `probeUsesSorry depends on [sorryAx]`, `probeUsesAxiom depends on [probeAxiom]`, and
  `probeAxiom`. The probe was removed and the library rebuilt.
- **`bash proofs/check.sh`** on the real tree: "axioms gate: 1024 declarations rest only on propext,
  Classical.choice, Quot.sound", `[lean] OK`, exit 0. It took about 1.5 minutes after a built tree,
  about 3 minutes cold.
- `bash -n proofs/check.sh` and `make help`: clean. `check.sh` keeps mode 100755.
