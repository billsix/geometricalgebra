# Audit the Dockerfile package list for CLI tools the gates/CI need (cmp is missing)

**Status:** proposed — needs go-ahead (CI is currently RED)
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-09-30 **Updated:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)

## BLUF

A GitHub Actions job fails with `/bin/bash: line 1: cmp: command not found` — the image built by
the `Dockerfile` doesn't install `cmp` (from **`diffutils`**), which the codegen-determinism gate
(`make check-generated`) uses to compare the twice-generated `g*.py`. The immediate fix is one
package, but the task is broader: **audit every gate / CI job / entrypoint script for the CLI
tools it shells out to, cross-check against what the image actually installs, and add the missing
ones to the package list** (the host-runnable `entrypoint/0N-install-*.sh` scripts the Dockerfile
dispatches). "Done" = a reviewed list of missing packages + the one-line fix(es), CI green.

## The failure (verbatim)

The `generated` check (`make check-generated`) runs, inside the container:

```
python tools/gen_specialized.py; ... for f in g1.py g2.py g3.py; do
  cmp -s "$f" "/tmp/gen0/$(basename "$f")" || { echo "...non-deterministic..."; exit 1; }; done
```

and dies at `cmp: command not found`. So the determinism check never actually ran — it failed on
a missing tool, not on a real non-determinism. (The generator IS deterministic; the earlier lines
show both runs wrote identical files.)

## Immediate cause + fix

`cmp` ships in **`diffutils`**. Add `diffutils` to the base package install
(`entrypoint/01-install-base.sh`, dispatched by the `Dockerfile` per the "host-agnostic setup"
convention). That alone unblocks CI.

## The broader audit (the actual task)

Don't stop at `cmp`. Other gate/CI steps may shell out to tools not in the image and only fail
when that specific path runs (CI runs more than a local `make shell` typically exercises).

1. **Enumerate the tools the gates use.** `git grep` the CI-facing surface for shelled-out
   commands and check each is installed:
   - `.github/workflows/*.yml`, the `Makefile` gate targets (`check-format`, `check-generated`,
     `check-regions`, `test`, `lean`, `docs`), `proofs/check.sh`, `tools/*.py` (subprocess calls),
     `entrypoint/*.sh`.
   - Usual suspects beyond `cmp`/`diffutils`: `diff`/`patch`, `git`, `cmp`, `find`, `xargs`,
     `envsubst` (gettext), `jq`, `column`, `timeout` (coreutils), `bc`, `rsync`, `unzip`.
2. **Cross-check against installed packages.** The install lives in `entrypoint/01-install-base.sh`
   (+ the feature-group scripts `02-install-docs.sh`, `03-install-notebook-tex.sh`,
   `04-install-docs.sh`); list what each `dnf install`s and diff against the tool list from step 1.
3. **Add the missing packages** to the right group script (base for gate tools; a feature group if
   the tool is only for docs/lean/etc.), keeping the "host-runnable, no flags" convention.
4. **Verify:** rebuild the image and run each gate (`make check-generated`, `check-format`,
   `check-regions`, `test`) — they should get past the tool-availability stage.

## Notes / cross-refs

- Package-install convention: `entrypoint/0N-install-*.sh` group scripts the Dockerfile dispatches
  by ARG (personal overlay "Host-agnostic setup belongs in a script"). Add `diffutils` to the base
  group, not inline in the Dockerfile.
- This is invisible locally when your dev image happens to have the tool (or you never run
  `check-generated`); it only bites on the clean CI runner — the same class as the `: image`
  prereq bug noted in `CLAUDE.md` › Continuous integration.

## Open questions

1. **Just `diffutils` now, or the full audit first?** My lean: land `diffutils` immediately to
   un-red CI (a one-line PR), then do the broader audit as a follow-up so a second missing tool
   doesn't cause a second red run. Your call on whether to bundle them.
