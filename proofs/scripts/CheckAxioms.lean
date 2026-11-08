/-
The axioms gate for the gacalc proofs: every declaration in a `GacalcProofs.*` module may rest
only on Lean's three standard axioms, `propext`, `Classical.choice` and `Quot.sound`.

Anything else (`sorryAx` from a `sorry`, a user `axiom`, `Lean.ofReduceBool` from `native_decide`)
is reported with the declaration that depends on it, and the file fails to elaborate, so
`lake env lean scripts/CheckAxioms.lean` exits nonzero. `proofs/check.sh` runs it after
`lake build`. This file is not part of the `GacalcProofs` library, so `lake build` does not build it.
-/
import GacalcProofs

open Lean Elab Command

/-- Check every `GacalcProofs.*` declaration's axioms against the standard three. -/
elab "#check_gacalc_axioms" : command => do
  let env ← getEnv
  let allowed : Array Name := #[``propext, ``Classical.choice, ``Quot.sound]
  let mut checked : Nat := 0
  let mut failures : Array (Name × Array Name) := #[]
  for (declName, _) in env.constants.map₁.toList do
    let some moduleIdx := env.getModuleIdxFor? declName | continue
    let moduleName : Name := env.header.moduleNames[moduleIdx.toNat]!
    unless (`GacalcProofs).isPrefixOf moduleName do continue
    if declName.isInternal then continue
    checked := checked + 1
    let axioms : Array Name ← collectAxioms declName
    let extra : Array Name := axioms.filter (fun a => !allowed.contains a)
    unless extra.isEmpty do
      failures := failures.push (declName, extra)
  if checked == 0 then
    throwError "axioms gate: found no GacalcProofs declarations to check"
  for (declName, extra) in failures do
    logError m!"axioms gate: {declName} depends on {extra}"
  if failures.isEmpty then
    logInfo m!"axioms gate: {checked} declarations rest only on propext, Classical.choice, Quot.sound"

#check_gacalc_axioms
