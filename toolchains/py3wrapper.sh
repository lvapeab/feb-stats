#!/usr/bin/env bash
ROOT=$(dirname "$0")
# disable pycache which produces non-deterministic outputs
export PYTHONDONTWRITEBYTECODE=1
exec "$ROOT/venv/bin/python3.7" -B "$@" # don't write .pyc files on import; also PYTHONDONTWRITEBYTECODE=x
