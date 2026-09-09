#!/usr/bin/env python3
# Copyright (c) 2026 William Emerison Six
#
# Fail if the version in pyproject.toml has no `## [<version>]` heading in
# CHANGELOG.md -- the guard against releasing unlogged (gacalc 0.0.19 shipped
# with an empty `[Unreleased]` on 2026-09-05). It catches an unlogged RELEASE
# only; an unlogged CHANGE is caught by the conventions' reconciliation of
# `[Unreleased]` against `<last tag>..HEAD` at squash / session end / release.
#
# Run from the repo root (any time; meant for the format gate -- see
# tasks/wire-changelog-guard.md):
#   python tools/check_changelog.py [--pyproject P] [--changelog C]
# Exit 0 when the heading exists, 1 with a message otherwise.

import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    ap: argparse.ArgumentParser = argparse.ArgumentParser()
    ap.add_argument("--pyproject", default="pyproject.toml")
    ap.add_argument("--changelog", default="CHANGELOG.md")
    args: argparse.Namespace = ap.parse_args()
    m: re.Match[str] | None = re.search(
        r'^version\s*=\s*"([^"]+)"', Path(args.pyproject).read_text(), re.M
    )
    if not m:
        print(f'{args.pyproject}: no `version = "..."` line found', file=sys.stderr)  # noqa: T201
        return 1
    version: str = m.group(1)
    text: str = Path(args.changelog).read_text()
    if re.search(rf"^## \[{re.escape(version)}\]", text, re.M):
        return 0
    print(  # noqa: T201 -- the diagnostic is the tool's output
        f"{args.changelog}: no `## [{version}]` heading for the version in "
        f"{args.pyproject} -- promote `[Unreleased]` to `## [{version}] -- <date>` "
        "(and write the entry, if `[Unreleased]` is empty) before releasing.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
