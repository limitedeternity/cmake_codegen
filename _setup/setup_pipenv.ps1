$BASEDIR = Split-Path $MyInvocation.MyCommand.Path -Parent
$PIPX = Join-Path -Path $BASEDIR -ChildPath pipx.pyz

if (![System.IO.File]::Exists($PIPX))
{
    Invoke-WebRequest "https://github.com/pypa/pipx/releases/download/1.2.0/pipx.pyz" -OutFile $PIPX
}

python $PIPX ensurepath
python $PIPX install pipenv
