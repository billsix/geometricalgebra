#!/usr/bin/env bash
# Install Lean 4 (https://lean-lang.org) — the open-source theorem prover / proof
# assistant — via elan, its official toolchain manager. Lean is not a Fedora dnf
# package; elan is fetched with the official curl installer (the same
# network-at-build style this image already uses for other tools, e.g. uv pip).
# elan installs into $HOME/.elan and this pulls the default *stable* toolchain
# (lean + lake), baking it into the image layer so an exported image has Lean
# offline. The Dockerfile adds $HOME/.elan/bin to PATH (ENV) after running this.
#
# Host-runnable: on a bare Fedora host, run this, then add ~/.elan/bin to PATH.
set -e
# git is required by `lake` to fetch dependencies (Mathlib is a git dependency:
# `lake new … math` / `lake exe cache get` clone github.com/leanprover-community/
# mathlib4). This container otherwise ships no git on purpose (git is a host-side
# concern here), so the Lean feature must add it itself. dnf-guarded for a bare host.
if command -v dnf >/dev/null 2>&1; then dnf install -y git; fi
curl -fsSL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
export PATH="$HOME/.elan/bin:$PATH"
elan default stable
lean --version
