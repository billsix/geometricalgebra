#!/usr/bin/env bash
# List every live reference to the seven ePiX helpers that move into gacalc.epixscene
# (archived tasks and frozen review records are history and stay as written).
cd "$(git rev-parse --show-toplevel)" || exit 1
git grep -n -E '\b_(scene2d|scene3d|frame_scene|bootstrap_live|line_scene|paper_scene|venn_scene)\b' \
    -- ':!tasks/archive' ':!tasks/review' ':!tasks/adhoc'
