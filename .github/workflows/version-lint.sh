#!/bin/bash

_latest="$(git tag --sort=taggerdate | tail -1 | cut -b 2-)" # The latest git tag
_pyproject_version="$(grep "version =" ./pyproject.toml | cut -d " " -f3 |  tr -d '"')" # The version in pyproject.toml
_main_version="$(grep "__version__ =" "./stateless/main.py"  | cut -d " " -f3 | tr -d '"')" # The __version__ in main.py
_error=0

if [ "$_latest" != "$_pyproject_version" ]; then
    echo "The version in the git tag (v${_latest}) does not match the version in pyproject.toml (${_pyproject_version})"
    _error=1
fi
if [ "$_latest" != "$_main_version" ]; then
    echo "The version in the git tag (v${_latest}) does not match the __version__ in stateless/main.py (${_pyproject_version})"
    _error=1
fi

exit $_error

