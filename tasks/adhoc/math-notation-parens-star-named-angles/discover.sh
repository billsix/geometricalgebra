#!/usr/bin/env bash
# Discovery for tasks/math-notation-parens-star-named-angles: every place a reader sees math
# written against the three notation rules. One grep per rule, over every file group that
# carries reader-facing math (book prose, figure labels, book + demo notebooks, Python
# docstrings incl. the generator's docstring table, Lean doc comments, reference docs, README).
# Prints `rule<TAB>file:line:text`; exits 0 even with no hits. Re-run after the fix: zero lines
# for rules 1 and 3 = done; rule 2 is a candidate list that must be READ (a juxtaposition may
# be prose, not a product), so its residue is explained in the task doc, not driven to zero.
#
#   tasks/adhoc/math-notation-parens-star-named-angles/discover.sh > .../data/hits-before.txt
set -u
cd "$(git rev-parse --show-toplevel)"

FILES=$(ls book/docs/*.rst book/docs/notebooks/*.py book/figures/epix/*.py notebooks/*.py \
           src/gacalc/*.py tools/*.py tests/*.py proofs/GacalcProofs/*.lean \
           tasks/reference/*.md README.md CLAUDE.md 2>/dev/null \
        | grep -vE '^src/gacalc/g[0-9]+\.py$')

# Rule 1 — a trig function applied without parentheses: `\cos\theta`, `\sin\beta_2`, `cos θ`,
# `sin (θ / 2)` (Lean's application syntax inside a doc comment), `cos x` in prose.
grep -nE '\\(cos|sin|tan)\\[a-zA-Z]|\\(cos|sin|tan) +[a-zA-Z\\]|\b(cos|sin|tan) +[θβαφψx-z(]' $FILES \
  | sed 's/^/1\t/'

# Rule 3 — an angle left unnamed: `\cos = …`, `cos = …`, `(cos = c, sin = s)`, `cos² + sin² = 1`.
grep -nE '\\(cos|sin)( |\\,)*=|\b(cos|sin)[²]? *= |\b(cos|sin)[²]? *\+ *(cos|sin)' $FILES \
  | sed 's/^/3\t/'

# Rule 2 — candidate juxtaposed products (to be READ): `|a||b|`, `\cos(\theta)\,\vec{a}`,
# `\vec{a}\,e_{12}`, `e_1 e_2`, `r\,\big(`, `A B`/`Ã B` in docstrings, `·` used as times.
grep -nE '\|[a-zA-Z]\|\|[a-zA-Z]\||\|[^|]+\|\s*\|[^|]+\|\s*(\\sin|\\cos|sin|cos)|\\(cos|sin)\([^)]*\)\\,|\\vec\{[a-z]\}\\,e_|\be_[0-9]+ e_[0-9]+|\\,\\big\(|\\,\\Big\(|·|\\cdot(s)? ' $FILES \
  | sed 's/^/2\t/'
exit 0
