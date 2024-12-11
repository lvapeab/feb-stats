#!/bin/bash
pipenv run ruff format  ;
pipenv run ruff check --fix ;
pipenv run mypy . ;
