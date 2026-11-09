#!/usr/bin/env bash
export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate
# No args -> an interactive shell; args (e.g. `-c '...'`) -> run them, so a pulled
# image can run a command with no --entrypoint override.
exec bash "$@"
