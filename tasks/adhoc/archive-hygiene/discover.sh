#!/usr/bin/env bash
# Discover archive-hygiene worklist items in archived task docs dated before 2026-11-08.
# Usage: tasks/adhoc/archive-hygiene/discover.sh [outdir]   (run from anywhere in the repo)
# Writes one snapshot file per check into outdir (default: tasks/adhoc/archive-hygiene/data).
# A re-run after the work is the gate: every file except docs.txt should be empty, apart from
# the exceptions recorded in tasks/archive-hygiene.md.
set -u
root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
out=${1:-tasks/adhoc/archive-hygiene/data}
mkdir -p "$out"

# Archived docs in scope: tasks/archive/2026/MM/DD/*.md dated before 2026-11-08.
docs() {
  find tasks/archive/2026 -name '*.md' | sort | awk -F/ '($4 $5) < "1108"'
}

docs > "$out/docs.txt"
# Scaffolding: Plan / Open questions headings, unchecked boxes, Status lines,
# "(original plan below)", "Context (read first)".
docs | xargs rg -n '^#+ (Plan|Open questions)|^\s*- \[ \]|\*\*Status:\*\*|original plan|Context \(read first\)' \
  > "$out/scaffolding.txt"
# Bare first name (authorship credits are reviewed by hand).
docs | xargs rg -n '\bBill\b' > "$out/bill.txt"
# Hex strings that look like short SHAs and do not resolve in this repo.
docs | xargs rg -on '\b[0-9a-f]{7,40}\b' | while IFS=: read -r f l sha; do
  case "$sha" in *[a-f]*) ;; *) continue ;; esac
  git cat-file -e "$sha^{commit}" 2>/dev/null || echo "$f:$l:$sha"
done > "$out/dead-shas.txt"
# tasks/... paths cited that do not exist.
docs | xargs rg -on 'tasks/[A-Za-z0-9_./-]+\.(md|py|sh|txt|lean)' | while IFS=: read -r f l p; do
  [ -e "$p" ] || echo "$f:$l:$p"
done > "$out/missing-paths.txt"
# Container-absolute paths.
docs | xargs rg -n '(^|[ `(])/(mvp|foo/opt)/' > "$out/container-paths.txt"
wc -l "$out"/*.txt
