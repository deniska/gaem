#!/bin/sh

.venv/bin/isort --profile black *.py examples build_scripts/*.py gaem
.venv/bin/black -l 79 -S *.py examples build_scripts/*.py gaem
