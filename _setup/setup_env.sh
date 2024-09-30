#!/usr/bin/env bash
set -e

BASEDIR="$(dirname -- "$(readlink -e -- "$0")")"
PIPX=${BASEDIR%%/}/pipx.pyz

if ! [[ -f "$PIPX" ]]
then
    wget "https://github.com/pypa/pipx/releases/download/1.2.0/pipx.pyz" -O "$PIPX"
fi

function substitute_file()
{
    local target
    local contents

    target="$1"
    contents="$2"

    local tempfile
    tempfile=$(mktemp)

    echo "$contents" >| "$tempfile"
    echo "Prepared substitute for $target at $tempfile"

    if [[ -f "$target" ]]
    then
        git --no-pager diff --histogram --no-index -- "$target" "$tempfile" || true

        local t_perms
        local t_owner
        local t_group

        t_perms=$(stat --printf="%a" "$target")
        t_owner=$(stat --printf="%U" "$target")
        t_group=$(stat --printf="%G" "$target")

        read -p "mv: overwrite '$target'? " -n 1 -r
        echo

        if [[ "$REPLY" =~ ^[Yy]$ ]]
        then
            sudo mv "$tempfile" "$target"
            echo "OK: $tempfile -> $target"

            sudo chmod "$t_perms" "$target"
            sudo chown "$t_owner":"$t_group" "$target"
        else
            echo "Skipped: $tempfile -/> $target"
        fi
    else
        sudo mv "$tempfile" "$target"
        echo "OK: $tempfile -> $target"
    fi

    echo
}

if [[ -f /proc/sys/fs/binfmt_misc/WSLInterop ]]
then
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y python3-venv unzip

    substitute_file /etc/wsl.conf "$(cat <<END
[boot]
systemd = true

[automount]
enabled = true
root    = /mnt/
options = "metadata,umask=22,fmask=11"
END
    )"

    WIN_HOME=$(wslpath -au "$(cmd.exe /c "echo %USERPROFILE%" | sed 's/\\ / /g' | sed -e 's/[[:space:]]*$//')")
    substitute_file "$WIN_HOME/.wslconfig" "$(cat <<END
[wsl2]
dnsProxy = false
END
    )"
fi

python3 "$PIPX" ensurepath
python3 "$PIPX" install cmake==3.27.7
python3 "$PIPX" install pipenv==2023.10.24
