#!/bin/sh

.venv/bin/isort --profile black *.py examples build_scripts/build_sdl.py gaem
.venv/bin/black -l 79 -S *.py examples build_scripts/build_sdl.py gaem
