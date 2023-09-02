#!/bin/bash
set -e

BASEDIR=$(readlink -f "$0" | xargs dirname)
PIPX=${BASEDIR%%/}/pipx.pyz

if ! [[ -f "$PIPX" ]]; then
  wget "https://github.com/pypa/pipx/releases/download/1.2.0/pipx.pyz" -O "$PIPX"
fi

sudo apt update
sudo apt install -y python3-venv

python3 "$PIPX" ensurepath
python3 "$PIPX" install pipenv
