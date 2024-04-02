{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    ruff
    python311
    python311Packages.pip
    python311Packages.virtualenv
  ];
  shellHook = ''
    export PIP_PREFIX=$(pwd)/_build/pip_packages
    export PYTHONPATH="$PIP_PREFIX/${pkgs.python311.sitePackages}:$PYTHONPATH"
    export PATH="$PIP_PREFIX/bin:$PATH"
    unset SOURCE_DATE_EPOCH
    alias format="ruff format"
    alias lint="ruff check --no-fix --select ALL --exclude CPY,PT,PTH,TD,PD"
  '';
}

# vim: sw=2
