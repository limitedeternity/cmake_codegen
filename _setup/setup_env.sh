#!/usr/bin/env bash
set -e
BASEDIR="$(dirname -- "$(readlink -e -- "$0")")"
PIPX=${BASEDIR%%/}/pipx.pyz

if ! [[ -f "$PIPX" ]]
then
    wget "https://github.com/pypa/pipx/releases/download/1.2.0/pipx.pyz" -O "$PIPX"
fi

python3 "$PIPX" ensurepath
python3 "$PIPX" install cmake==3.27.7
python3 "$PIPX" install pipenv==2023.10.24
