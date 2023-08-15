#!/bin/bash

REPO=$(git rev-parse --show-toplevel)
CWD=$REPO/scripts

PYTHON=$REPO/venv/bin/python

if [ ! -f "$PYTHON" ]; then
	mk venv
fi
test -f "$PYTHON"

"$PYTHON" "$CWD/run_handle_stop_testing.py"
echo $?
