#!/usr/bin/env sh
set -e
python3.7 -m venv --without-pip "$1"

# remove unused activation scripts that break caching
rm "$1/bin/"activate*
