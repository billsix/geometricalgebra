#!/usr/bin/env bash
# Install Lean 4 (https://lean-lang.org) — the open-source theorem prover / proof
# assistant — via elan, its official toolchain manager. Lean is not a Fedora dnf
# package; elan is fetched with the official curl installer (the same
# network-at-build style this image already uses for other tools, e.g. uv pip).
# elan installs into $HOME/.elan, and this installs exactly ONE toolchain (lean +
# lake): the one the proofs pin in proofs/lean-toolchain, so `lake` never has to
# fetch a second one and an exported image has the proofs' Lean offline. The
# Dockerfile adds $HOME/.elan/bin to PATH (ENV) after running this.
#
# The toolchain comes from $LEAN_TOOLCHAIN when set (the Dockerfile sets it from
# the copied proofs/lean-toolchain), otherwise from proofs/lean-toolchain beside
# this script's repo checkout.
#
# Host-runnable: from the repo, run entrypoint/install-lean.sh, then add
# ~/.elan/bin to PATH.
set -eo pipefail
if [ -z "${LEAN_TOOLCHAIN:-}" ]; then
    LEAN_TOOLCHAIN="$(cat "$(dirname "$0")/../proofs/lean-toolchain")"
fi
# git is required by `lake` to fetch dependencies (Mathlib is a git dependency:
# `lake new … math` / `lake exe cache get` clone github.com/leanprover-community/
# mathlib4). The base image ships no git on purpose (git is a host-side concern
# here); a feature that needs it adds it itself -- this one, and 06-install-epix.sh
# for the ePiX fetch. dnf-guarded for a bare host.
if command -v dnf >/dev/null 2>&1; then dnf install -y git; fi
curl -fsSL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
    | sh -s -- -y --default-toolchain "$LEAN_TOOLCHAIN"
export PATH="$HOME/.elan/bin:$PATH"
lean --version
