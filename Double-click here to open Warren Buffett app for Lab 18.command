#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
exec lab-18/.venv/bin/python lab-18/launch.py
