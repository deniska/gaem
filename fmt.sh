#!/bin/sh

.venv/bin/isort --profile black *.py examples
.venv/bin/black -l 79 -S *.py examples
